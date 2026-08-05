import csv
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime
from django.db.models import Q
from .models import Customer
from .forms import CustomerForm

def home(request):
    form = CustomerForm()
    query = request.GET.get('q', '') # Fetch the search term from the URL query parameters
            
    if query:
        # Search by ID, first name, last name, or email
        customers = Customer.objects.filter(
            Q(customer_code__icontains=query) |
            Q(company_name__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(billing_address__icontains=query) |
            Q(email__icontains=query)
        )
    else:
        customers = Customer.objects.all()
        
    context = {
        'customers' : customers,
        'query' : query,
        'form' : form
            }
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save() # Automatically inserts a clean row into your database table
            # return redirect('customers_home') # Redirect after saving to prevent duplicate inputs
            return render(request, 'customers/home.html', context)

    return render(request, 'customers/home.html', context)

def customer_detail_ajax(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    # Renders a partial HTML template instead of a full page
    return render(request, 'customers/customer_details.html', {'customer': customer})
