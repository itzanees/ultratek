from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from projects.models import Project
from employees.models import EmployeeMaster
from .models import WorkingHours, AttendanceLog, SiteScheduleConfig
from projects.models import ProjectAssignment
from django.db.models import Sum, Count

import json
import logging
import requests
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
# from .models import SiteManager, AttendanceRecord, ProgressReport



VERIFY_TOKEN = "MY_SECRET_DJANGO_TOKEN"  # Match this in Meta Portal
WHATSAPP_TOKEN = settings.WHATSAPP_API_TOKEN
PHONE_NUMBER_ID = settings.WHATSAPP_PHONE_NUMBER_ID

def home(request):


    # 1. Handle date filtration (Default to today's local date)
    date_str = request.GET.get('date', '')
    if date_str:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        target_date = timezone.localdate()

    # 2. Fetch all logs logged on that specific day
    logs = AttendanceLog.objects.filter(date=target_date).select_related('employee', 'project_site')

    # 3. High-level metric calculations
    total_present = logs.count()
    
    total_ot_hours = logs.aggregate(total_ot=Sum('overtime_hours_worked'))['total_ot'] or 0.00
    
    whatsapp_entries = logs.filter(source='WHATSAPP').count()
    manual_entries = logs.filter(source='MANUAL').count()

    # Find sites that have missing "Working Hours" rule mappings
    total_sites = Project.objects.filter(is_active=True).count()
    active_sites_logged = logs.values('project_site').distinct().count()
    unreported_sites = max(0, total_sites - active_sites_logged)

    return render(request, 'attendance/home.html', {
        'logs': logs,
        'target_date': target_date.strftime('%Y-%m-%d'),
        'metrics': {
            'total_present': total_present,
            'total_ot_hours': total_ot_hours,
            'whatsapp_count': whatsapp_entries,
            'manual_count': manual_entries,
            'unreported_sites': unreported_sites
        }
    })
    # sites = Project.objects.filter(is_active=True)
    # employees = EmployeeMaster.objects.filter(is_active=True)
    # return render(request,'attendance/home.html', {'sites': sites, 'employees':employees})

def mark_site_attendance(request):
    sites = Project.objects.filter(is_active=True)
    
    if request.method == "POST":
        site_id = request.POST.get('project_site')
        selected_employee_ids = request.POST.getlist('present_employees')
        target_date_str = request.POST.get('attendance_date')
        
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date() if target_date_str else timezone.localdate()
        project = Project.objects.get(id=site_id)
        
        # 1. Fetch site's expected scheduling parameter setup
        schedule_config = getattr(project, 'schedule_config', None)
        if not schedule_config:
            messages.error(request, f"Error: Configuration aborted. No 'Working Hours Template' linked to {project.project_name}.")
            return redirect('mark_attendance')
            
        hours_template = schedule_config.working_hours
        
        # Combine parameters to establish accurate timestamp metrics
        base_in = datetime.combine(target_date, hours_template.standard_start_time)
        base_out = datetime.combine(target_date, hours_template.standard_end_time)
        
        saved_count = 0
        for emp_id in selected_employee_ids:
            # Prevent duplication issues across database rows
            log, created = AttendanceLog.objects.get_or_create(
                employee_id=emp_id,
                date=target_date,
                defaults={
                    'project_site': project,
                    'check_in': base_in,
                    'check_out': base_out,
                    'regular_hours_worked': hours_template.expected_hours_per_day,
                    'overtime_hours_worked': 0.00, # Base value; overwritten during checkout modifications
                    'source': 'MANUAL'
                }
            )
            if created:
                saved_count += 1
                
        messages.success(request, f"Successfully logged attendance entries for {saved_count} workers at {project.project_name}.")
        return redirect('mark_site_attendance')
        
    # Get active employees to populate our checklist choice lists
    employees = EmployeeMaster.objects.filter(is_active=True)
    return render(request, 'attendance/mark_attendance.html', {
        'sites': sites,
        'employees': employees,
        'today': timezone.localdate().strftime('%Y-%m-%d')
    })


def crew_list_ajax(request):
    # crew = get_object_or_404(, id=customer_id)
    project_id = request.GET.get('project_id')

    if not project_id:
        return JsonResponse({'assigned':[], 'available':[]})

    try:
        project = Project.objects.get(id=project_id)

        crew = project.employees.all().values('id', 'first_name')
        crew_ids = [emp['id'] for emp in crew]

        availabe_crew = EmployeeMaster.objects.exclude(id__in=crew_ids).values('id','first_name')

        return JsonResponse({
            'assigned': list(crew),
            'available': list(availabe_crew)
        })
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=400)

# whatsapp integration

@csrf_exempt
def whatsapp_webhook(request):
    # 1. Verification Step (GET Request from Meta)
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return HttpResponse(challenge, status=200)
        return HttpResponse('Verification failed', status=403)

    # 2. Incoming Messages (POST Request from Meta)
    elif request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        
        try:
            entries = data.get('entry', [])
            for entry in entries:
                changes = entry.get('changes', [])
                for change in changes:
                    value = change.get('value', {})
                    messages = value.get('messages', [])
                    
                    if messages:
                        msg = messages[0]
                        sender_phone = msg.get('from')  # Manager's phone number
                        
                        # Process text messages
                        if msg.get('type') == 'text':
                            text_body = msg.get('text', {}).get('body', '')
                            handle_incoming_text(sender_phone, text_body)
                            
        except Exception as e:
            # Log exception here
            print(f"Error processing webhook: {e}")

        # Meta expects a 200 OK fast to prevent retries
        return JsonResponse({'status': 'success'}, status=200)

    return HttpResponse('Method not allowed', status=405)


def handle_incoming_text(sender_phone, text):
    # Find manager by phone number
    manager = SiteManager.objects.filter(phone_number=sender_phone).first()
    if not manager:
        send_whatsapp_text(sender_phone, "Unauthorized number. Please contact HR.")
        return

    text_clean = text.strip()

    if text_clean.upper().startswith("ATTENDANCE"):
        # Format: ATTENDANCE | Site Name | 12 Present, 2 Absent
        parts = text_clean.split('|')
        site_name = parts[1].strip() if len(parts) > 1 else manager.assigned_site
        details = parts[2].strip() if len(parts) > 2 else ""

        AttendanceRecord.objects.create(
            site_manager=manager,
            site_name=site_name,
            details=details
        )
        send_whatsapp_text(sender_phone, f"✅ Attendance logged for {site_name}.")

    elif text_clean.upper().startswith("PROGRESS"):
        # Format: PROGRESS | Site Name | Progress summary
        parts = text_clean.split('|')
        site_name = parts[1].strip() if len(parts) > 1 else manager.assigned_site
        details = parts[2].strip() if len(parts) > 2 else ""

        ProgressReport.objects.create(
            site_manager=manager,
            site_name=site_name,
            report_summary=details
        )
        send_whatsapp_text(sender_phone, f"✅ Progress report saved for {site_name}.")

    else:
        # Prompt user with correct template format
        msg = ("Format not recognized. Please use:\n\n"
               "1. ATTENDANCE | Site Name | Details\n"
               "2. PROGRESS | Site Name | Summary")
        send_whatsapp_text(sender_phone, msg)

def send_whatsapp_text(recipient_phone, message_text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_phone,
        "type": "text",
        "text": {"body": message_text}
    }
    requests.post(url, json=payload, headers=headers)

