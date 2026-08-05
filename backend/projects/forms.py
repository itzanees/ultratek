from django import forms
from .models import Project
from customers.models import Customer
from employees.models import EmployeeMaster

class ProjectForm(forms.ModelForm):
    # Dynamic searchable dropdown for the ForeignKey client relationship
    client = forms.ModelChoiceField(
        queryset=Customer.objects.filter(is_active=True),
        empty_label="--- Type to search client ---",
        label="Assigned Client"
    )
    
    # Searchable multi-select element to bundle many employees at creation
    employees = forms.ModelMultipleChoiceField(
        queryset=EmployeeMaster.objects.filter(is_active=True),
        required=False,
        label="Assign Initial Team Members",
        help_text="Hold Ctrl/Cmd to select multiple, or type to filter below."
    )

    class Meta:
        model = Project
        fields = [
            'project_code', 'project_name', 'location_city', 
            'client', 'employees', 'start_date', 'estimated_end_date', 'is_active'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'estimated_end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        """Override save to cleanly write entries to the ProjectAssignment through table."""
        project = super().save(commit=commit)
        if commit:
            # Handle intermediate tracking data connections safely
            # Note: This assigns them with empty roles/current dates by default
            chosen_employees = self.cleaned_data.get('employees', [])
            for employee in chosen_employees:
                from .models import ProjectAssignment
                ProjectAssignment.objects.get_or_create(
                    employee=employee,
                    project=project,
                    is_current_assignment=True
                )
        return project
