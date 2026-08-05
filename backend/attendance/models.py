from django.db import models
from django.utils import timezone
# from projects.models import Project


class WorkingHours(models.Model):
    name = models.CharField(max_length=100, verbose_name="e.g., Standard 8-Hour Site Shift")
    standard_start_time = models.TimeField(help_text="Standard daily check-in time")
    standard_end_time = models.TimeField(help_text="Standard daily check-out time")
    
    # Quantitative configuration limits
    expected_hours_per_day = models.DecimalField(max_digits=4, decimal_places=2, default=8.00)
    overtime_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.50)
    
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Working Hours Schedule"
        verbose_name_plural = "Working Hours Schedules"

    def __str__(self):
        return f"{self.name} ({self.expected_hours_per_day} hrs/day)"

class SiteScheduleConfig(models.Model):
    """Maps which project site uses which working hours rules template."""
    project_site = models.OneToOneField('projects.Project', on_delete=models.CASCADE, related_name="schedule_config")
    working_hours = models.ForeignKey(WorkingHours, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.project_site.project_name} -> {self.working_hours.name}"


class AttendanceLog(models.Model):
    """Tracks daily registration logs for payroll and overtime evaluation."""
    employee = models.ForeignKey('employees.EmployeeMaster', on_delete=models.CASCADE, related_name="attendance_logs")
    project_site = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.localdate)
    
    # Timestamps
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(blank=True, null=True)
    
    # Performance calculation caches
    regular_hours_worked = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    overtime_hours_worked = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    
    # Meta tracking to log data entry sources
    ENTRY_SOURCES = [
        ('MANUAL', 'Manual Dashboard Entry'),
        ('WHATSAPP', 'Automated WhatsApp API Vector')
    ]
    source = models.CharField(max_length=10, choices=ENTRY_SOURCES, default='MANUAL')

    class Meta:
        unique_together = ('employee', 'date') # Limits double logging per employee per day
        verbose_name = "Attendance Entry"
        verbose_name_plural = "Attendance Entries"

    def __str__(self):
        return f"{self.employee.first_name} - {self.date} [{self.project_site.project_code}]"