from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request,'attendance/home.html')



import json
import requests
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from employees.models import SiteManager, AttendanceRecord, ProgressReport

VERIFY_TOKEN = settings.VERIFY_TOKEN  # Match this in Meta Portal
WHATSAPP_TOKEN = settings.WHATSAPP_API_TOKEN
PHONE_NUMBER_ID = settings.WHATSAPP_PHONE_NUMBER_ID

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