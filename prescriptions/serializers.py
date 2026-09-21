from rest_framework import serializers
from .models import Prescription
from appointments.models import Appointment

class PrescriptionSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='appointment.patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='appointment.doctor.name', read_only=True)
    department = serializers.CharField(source='appointment.doctor.department', read_only=True)
    appointment_date = serializers.DateField(source='appointment.date', read_only=True)

    class Meta:
        model = Prescription
        fields = [
            'id', 'appointment', 'patient_name', 'doctor_name',
            'department', 'appointment_date', 'medicines',
            'dosage', 'instructions', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
