from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

class EmployeeMaster(models.Model):
    # --- 1. CORE IDENTIFICATION ---
    employee_id = models.CharField(max_length=20, unique=True, blank=True, verbose_name="Employee ID")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(unique=True, blank=True)
    
    # Saudi Phone Validator (+9665XXXXXXXX)
    saudi_phone_regex = RegexValidator(
        regex=r'^\+9665\d{8}$',
        message="Format must be: '+9665XXXXXXXX'"
    )
    phone_number = models.CharField(validators=[saudi_phone_regex], max_length=13, unique=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True, help_text="e.g., O+, A-")

    # Link to the departments application
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.PROTECT, # Protect prevents deleting a department if it still has active employees
        related_name='employees',
        blank=True,
        null=True,
        verbose_name="Assigned Department"
    )

    # --- 2. PASSPORT & LEGAL DOCUMENTS ---
    iqama_number = models.CharField(max_length=10, unique=True, blank=True, null=True, verbose_name="Iqama / National ID")
    iqama_expiry_gregorian = models.DateField(blank=True, null=True, verbose_name="Iqama Expiry (Gregorian)")
    
    passport_number = models.CharField(blank=True, null=True, max_length=20, unique=True)
    passport_expiry_date = models.DateField(blank=True, null=True, verbose_name="Passport Expiry Date")
    id_expiry_date = models.DateField(blank=True, null=True, verbose_name="Company ID Expiry Date")

    # --- 3. SITE-TO-SITE TRAVEL DETAILS ---

    # Add this property inside your EmployeeMaster class in hr_app/models.py
    @property
    def current_site(self):
        """Fetches the active work site layout assigned to this employee."""
        active_assignment = self.projectassignment_set.filter(is_current_assignment=True).first()
        if active_assignment:
            return active_assignment.project
        return None
    
    last_transfer_date = models.DateField(blank=True, null=True, help_text="Date relocated to current site")
    transportation_mode = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., Company Bus, Flight")

    # --- 4. LEAVE & VACATION TRACKING ---
    last_leave_start_date = models.DateField(blank=True, null=True)
    last_leave_end_date = models.DateField(blank=True, null=True)
    next_planned_leave = models.DateField(blank=True, null=True)
    
    # Leave balance metrics (In Days)
    leaves_allocated = models.PositiveIntegerField(default=30, help_text="Total annual leave quota")
    leaves_used = models.PositiveIntegerField(default=0)

    # --- 5. REPATRIATION & FLIGHT LOGISTICS ---
    nearest_airport_ksa = models.CharField(max_length=50, help_text="Nearest airport to work site (e.g., JED, RUH, DMM)")
    home_country_airport = models.CharField(max_length=100, help_text="Destination airport in home country")
    last_air_fare_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Cost in SAR")

    # --- 6. HOME COUNTRY EMERGENCY CONTACTS ---
    emergency_contact_name = models.CharField(max_length=100, verbose_name="Home Country Contact Name")
    emergency_contact_relationship = models.CharField(max_length=50, verbose_name="Relationship (e.g., Spouse, Parent)")
    
    # International phone validator for home country number
    intl_phone_regex = RegexValidator(
        regex=r'^\+\d{7,15}$',
        message="International phone must start with '+' followed by 7 to 15 digits."
    )
    emergency_contact_number = models.CharField(validators=[intl_phone_regex], max_length=16, verbose_name="Home Country Phone")

    # --- 7. METADATA ---
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Employee Master Record"
        verbose_name_plural = "Employee Master Records"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.employee_id}"

    # --- DYNAMIC CALCULATED FIELDS ---
    @property
    def leaves_left(self):
        """Dynamically computes remaining leaves safely."""
        return max(0, self.leaves_allocated - self.leaves_used)

    @property
    def needs_passport_renewal(self):
        """Checks if passport expires in less than 90 days."""
        if self.passport_expiry_date:
            return (self.passport_expiry_date - timezone.localdate()).days < 90
        return False

    def save(self, *args, **kwargs):
        """Overrides the default save method to auto-generate sequential IDs."""
        if not self.employee_id:
            current_year = timezone.now().year
            prefix = f"EMP-{current_year}-"
            
            # Find the highest existing ID number for the current year
            last_employee = EmployeeMaster.objects.filter(
                employee_id__startswith=prefix
            ).order_by('employee_id').last()

            if last_employee:
                # Extract the number part from the last ID (e.g., '0001' from 'EMP-2026-0001')
                try:
                    last_sequence = int(last_employee.employee_id.split('-')[-1])
                    new_sequence = last_sequence + 1
                except (ValueError, IndexFailure):
                    new_sequence = 1
            else:
                new_sequence = 1

            # Format the sequential integer with padded zeros (e.g., 0001, 0002)
            self.employee_id = f"{prefix}{new_sequence:04d}"

        super().save(*args, **kwargs)
