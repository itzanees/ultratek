from django import forms
from .models import Department
from employees.models import EmployeeMaster

class DepartmentForm(forms.ModelForm):
    # Fetch active employees dynamically for the dropdown field selection
    manager = forms.ModelChoiceField(
        queryset=EmployeeMaster.objects.filter(is_active=True),
        required=False,
        empty_label="--- Select Department Head (Optional) ---",
        label="Department Head / Manager"
    )

    class Meta:
        model = Department
        # Specify fields you want to show on the public page form
        fields = [
            'dept_code', 'name', 'manager', 'is_active'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply standard Bootstrap classes to form fields
        for name, field in self.fields.items():
            if name != 'is_active':
                field.widget.attrs.update({'class': 'form-control'})
       
