from django.urls import path
from .import views

urlpatterns = [
    path('customers/', views.home, name='customers_home'),
]