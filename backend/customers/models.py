from django.db import models
from django.utils import timezone


class Customer(models.Model):
    customer_code = models.CharField(max_length=20, unique=True, verbose_name="Client Code")
    company_name = models.CharField(max_length=150, verbose_name="Company/Client Name")
    contact_person = models.CharField(max_length=100, blank=True, null=True, verbose_name="Contact Representative")
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Billing & Corporate Data
    vat_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="VAT / Tax Number")
    billing_address = models.TextField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['company_name']

    def __str__(self):
        return f"{self.customer_code} - {self.company_name}"

    def save(self, *args, **kwargs):
            """Overrides the default save method to auto-generate sequential IDs."""
            if not self.customer_code:
                current_year = str(timezone.now().year)[2:]
                prefix = f"CST-{current_year}-"
                
                # Find the highest existing ID number for the current year
                last_customer = Customer.objects.filter(
                    customer_code__startswith=prefix
                ).order_by('customer_code').last()
    
                if last_customer:
                    # Extract the number part from the last ID (e.g., '0001' from 'EMP-2026-0001')
                    try:
                        last_sequence = int(last_customer.customer_code.split('-')[-1])
                        new_sequence = last_sequence + 1
                    except (ValueError, IndexFailure):
                        new_sequence = 1
                else:
                    new_sequence = 1
    
                # Format the sequential integer with padded zeros (e.g., 0001, 0002)
                self.customer_code = f"{prefix}{new_sequence:04d}"
    
            super().save(*args, **kwargs)
