from django.db import models

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
