from django.urls import path
from . import views

urlpatterns = [
    path('branches/', views.home, name='branches_home'),
]