from django.urls import path
from .import views

urlpatterns = [
    path('employees/', views.home, name='employees_home'),
    path('employee/add/', views.create_employee, name='create_employee'),
    path('employee/success/', views.employee_success, name='employee_success'),
]