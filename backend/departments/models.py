from django.db import models

class Department(models.Model):
    dept_code = models.CharField(max_length=10, unique=True, verbose_name="Department Code")
    name = models.CharField(max_length=100, unique=True, verbose_name="Department Name")
    
    # Track the manager or head of department
    manager = models.ForeignKey(
        'employees.EmployeeMaster', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='managed_departments',
        verbose_name="Department Head"
    )
    
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self):
        return f"{self.dept_code} - {self.name}"
