from django.urls import path
from .import views

urlpatterns = [
    path('projects/', views.home, name='projects_home'),
    path('projects/<int:project_id>/', views.crew_detail_ajax, name='crew_detail_ajax'),
    path('projects/add/', views.create_project, name='create_project'),
]