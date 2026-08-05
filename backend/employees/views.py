import csv
import io
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from django.db.models import Q
from .models import EmployeeMaster
from .forms import EmployeeForm, CSVImportForm

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
            messages.success(request, f'Created employee successfully.')
            return redirect('employees_home') # Redirect after saving to prevent duplicate inputs
    else:
        form = EmployeeForm() # Show a blank form instance
        
    return render(request, 'employees/employee_form.html', {'form': form})


def import_employee(request):
    if request.method == "POST":
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            
            # Basic validation check for file extension type
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Error: This file format is not supported. Please upload a .csv file.')
                return redirect('import_employees')

            # Read and parse decoded data streams safely
            data_set = csv_file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            next(io_string) # Skip the initial CSV column header row

            success_count = 0
            error_count = 0

            for row in csv.reader(io_string, delimiter=','):
                if not row:
                    continue  # Skip blank trailing lines
                
                try:
                    # Map the CSV index positions to your Model fields
                    EmployeeMaster.objects.create(
                        first_name=row[0].strip(),
                        last_name=row[1].strip(),
                        email=row[2].strip(),
                        phone_number=row[3].strip(),
                    )
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    # Optional: Log 'str(e)' error description vectors for deep debugging

            messages.success(request, f'Import Complete: {success_count} profiles loaded successfully. Errors: {error_count}.')
            return redirect('employees_home')
    else:
        form = CSVImportForm()
        
    return render(request, 'employees/import_csv.html', {'form': form})

def employee_success(request):
    return render(request, 'employees/success.html')