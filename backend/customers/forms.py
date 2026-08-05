from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer

        fields = [
            'company_name', 'contact_person', 'phone_number', 'email', 'billing_address', 'vat_number'
        ]
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
