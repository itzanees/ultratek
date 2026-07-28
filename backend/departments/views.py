from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Department
from .forms import DepartmentForm

def home(request):
    query = request.GET.get('q', '') # Fetch the search term from the URL query parameters

    if query:
            # Search by ID, first name, last name, or email
            departments = Department.objects.filter(
                Q(dept_code__icontains=query) |
                Q(name__icontains=query)
            )
    else:
            departments = Department.objects.all()

    context = {
            'departments' : departments,
            'query' : query
        }
    return render(request, 'departments/home.html', context)


def create_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save() # Automatically inserts a clean row into your database table
            return redirect('detaprtment_success') # Redirect after saving to prevent duplicate inputs
    else:
        form = DepartmentForm() # Show a blank form instance
            
    return render(request, 'departments/department_form.html', {'form': form})
    
def department_success(request):
    return render(request, 'departments/success.html')