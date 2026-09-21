import uuid
from django.db import models
from appointments.models import Appointment

class Prescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='prescriptions')
    medicines = models.JSONField(default=list, help_text="List of medicines with name, dosage, frequency, and duration")
    dosage = models.CharField(max_length=200, help_text="Summary dosage regimen")
    instructions = models.TextField(blank=True, default="Take after meals. Maintain adequate hydration.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prescription for {self.appointment.patient.full_name} by Dr. {self.appointment.doctor.name}"
