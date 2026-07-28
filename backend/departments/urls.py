from django.urls import path
from .import views

urlpatterns = [
    path('departments/', views.home, name='departments_home'),
    path('departments/create/', views.create_department, name='create_department'),
    path('departments/success/', views.department_success, name='detaprtment_success'),
]