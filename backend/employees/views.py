from django.shortcuts import render, redirect
from django.db.models import Q
from .models import EmployeeMaster
from .forms import EmployeeForm

def home(request):

    query = request.GET.get('q', '') # Fetch the search term from the URL query parameters
    
    if query:
        # Search by ID, first name, last name, or email
        employees = EmployeeMaster.objects.filter(
            Q(employee_id__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    else:
        employees = EmployeeMaster.objects.all()
        
    context = {
        'employees' : employees,
        'query' : query
    }
    return render(request, 'employees/home.html', context)

def create_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save() # Automatically inserts a clean row into your database table
            return redirect('employee_success') # Redirect after saving to prevent duplicate inputs
    else:
        form = EmployeeForm() # Show a blank form instance
        
    return render(request, 'employees/employee_form.html', {'form': form})

def employee_success(request):
    return render(request, 'employees/success.html')