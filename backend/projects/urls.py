from django.urls import path
from .import views

urlpatterns = [
    path('projects/', views.home, name='projects_home'),
]