import uuid
from django.db import models
from patients.models import Patient

class Doctor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    experience = models.PositiveIntegerField(help_text="Years of professional experience")
    availability = models.CharField(max_length=100, default="Mon-Fri 09:00 - 17:00")
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    phone = models.CharField(max_length=20, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"Dr. {self.name} ({self.department})"

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('Scheduled', 'Scheduled'),
        ('In-Progress', 'In-Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f"Appointment: {self.patient.full_name} with Dr. {self.doctor.name} on {self.date} at {self.time}"
