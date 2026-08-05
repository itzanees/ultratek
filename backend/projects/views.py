from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Project, ProjectAssignment
from .forms import ProjectForm

def home(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Project site initiated successfully.")
            return redirect('projects_home')
    else:
        form = ProjectForm()

        """Lists all operational project sites with built-in search filters."""
        query = request.GET.get('q', '')
        
        if query:
            projects = Project.objects.filter(
                Q(project_code__icontains=query) |
                Q(project_name__icontains=query) |
                Q(location_city__icontains=query) |
                Q(client__company_name__icontains=query)
            ).distinct()
        else:
            projects = Project.objects.all().select_related('client')

        return render(request, 'projects/home.html', {
            'projects': projects,
            'query': query,
            'form' : form
        })

def create_project(request):
    """Processes entry data for building new project locations."""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Project site initiated successfully.")
            return redirect('projects_home')
    else:
        form = ProjectForm()
        
    return render(request, 'projects/project_form.html', {'form': form})


def crew_detail_ajax(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    crew = ProjectAssignment.objects.filter(
        project = project,
        is_current_assignment = True
    ).select_related('employee')

    return render(request, 'projects/crew_details.html', {'project':project,'crew': crew})

# Phone Number ID, 1201382143063728
# Temporary/Permanent Access Token : EAAUMYRHHq2MBSOW3LDAZCwQzILZCdofmoTKu1tAFTWfNXp2QT4iCZCLCvDCFXSOnWo3qLAtTSNpqMKgOUA9kpF54ZBimWKAgZB92ZCpvm6vrEIS7j4BueZBKv9xzz6Vuf32X1DHp13NdgSChujSUzxZCYLjCqJ7tldZA4Og7icaf3wU4V4LGjv9W0qWbuuNAVFsG9LNPIEc7zkHDEvroMfSiuLm2K9RAUK0NdDmkTZAA0j2bTbm8WZBT1FxDrW57GmPU77QtpVELjz8ffCBaGZBCswZDZD