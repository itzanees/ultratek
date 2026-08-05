from django.urls import path
from .import views

urlpatterns = [
    path('customers/', views.home, name='customers_home'),
    path('customers/<int:customer_id>/', views.customer_detail_ajax, name='customer_detail_ajax'),
]