from django.db import models
from django.utils import timezone

class Project(models.Model):
    project_code = models.CharField(max_length=20, unique=True, verbose_name="Project/Site Code")
    project_name = models.CharField(max_length=150, verbose_name="Site Name")
    location_city = models.CharField(max_length=50, verbose_name="City/Region")
    client = models.ForeignKey(
        'customers.Customer', # Point to the 'Customer' model in your customers app
        on_delete=models.PROTECT,  # Protect prevents accidental deletion of client if they have active projects
        related_name='projects',
        verbose_name="Assigned Client"
    )
    
    # Establish link to Employee via the custom through table
    employees = models.ManyToManyField(
        'employees.EmployeeMaster', # Update 'hr_app' to match your actual HR app directory name
        through='ProjectAssignment',
        related_name='assigned_projects'
    )
    
    is_active = models.BooleanField(default=True, verbose_name="Site Active Status")
    start_date = models.DateField()
    estimated_end_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = "Project Site"
        verbose_name_plural = "Project Sites"

    def __str__(self):
        return f"{self.project_code} - {self.project_name}"


class ProjectAssignment(models.Model):
    """Intermediate table to track employee deployment durations at specific sites."""
    
    employee = models.ForeignKey('employees.EmployeeMaster', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    
    # Track critical assignment metrics
    role_at_site = models.CharField(max_length=100)
    assigned_date = models.DateField(default=timezone.localdate)
    released_date = models.DateField(
        blank=True, 
        null=True, 
        help_text="Leave blank if the employee is currently active at this site."
    )
    
    # Status handling
    is_current_assignment = models.BooleanField(
        default=True, 
        help_text="Uncheck this if the employee has completed their work at this site."
    )

    class Meta:
        verbose_name = "Work Site Assignment"
        verbose_name_plural = "Work Site Assignments"
        # Prevent assigning the same employee to the same project twice simultaneously
        unique_together = ('employee', 'project', 'assigned_date')

    def __str__(self):
        return f"{self.employee.employee_id} -> {self.project.project_code}"
