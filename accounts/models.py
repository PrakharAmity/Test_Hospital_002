from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        DOCTOR = 'doctor', 'Doctor'
        RECEPTIONIST = 'receptionist', 'Receptionist'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.RECEPTIONIST,
        help_text="Role determining access privileges across dashboards and APIs."
    )
    phone = models.CharField(max_length=20, blank=True, null=True)

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    @property
    def is_receptionist(self):
        return self.role == self.Role.RECEPTIONIST

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
