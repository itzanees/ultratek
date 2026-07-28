from django import forms
from .models import EmployeeMaster
from departments.models import Department

class EmployeeForm(forms.ModelForm):
     # Fetch active employees dynamically for the dropdown field selection
    departments = forms.ModelChoiceField(
            queryset=Department.objects.filter(is_active=True),
            required=False,
            empty_label="--- Select Department (Optional) ---",
            label="Department"
        )

    class Meta:
        model = EmployeeMaster
        # Specify fields you want to show on the public page form
        fields = [
            'employee_id', 'first_name', 'last_name', 'email', 'phone_number', 'departments'
        ]
        
        # Add HTML date picker calendars to date fields
        widgets = {
            'passport_expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'id_expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Automatically inject Bootstrap CSS styling into every generated field
        for field_name, field in self.fields.items():
            if field_name not in ['passport_expiry_date', 'id_expiry_date']:
                field.widget.attrs['class'] = 'form-control'
