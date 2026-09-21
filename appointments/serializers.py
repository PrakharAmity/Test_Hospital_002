from rest_framework import serializers
from .models import Doctor, Appointment
from patients.serializers import PatientSerializer

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'name', 'department', 'experience', 'availability', 'consultation_fee', 'phone', 'email']

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    department = serializers.CharField(source='doctor.department', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'doctor', 'patient_name', 'doctor_name',
            'department', 'date', 'time', 'status', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        doctor = attrs.get('doctor', getattr(self.instance, 'doctor', None))
        date = attrs.get('date', getattr(self.instance, 'date', None))
        time = attrs.get('time', getattr(self.instance, 'time', None))
        status = attrs.get('status', getattr(self.instance, 'status', 'Scheduled'))

        if doctor and date and time and status != 'Cancelled':
            conflicts = Appointment.objects.filter(
                doctor=doctor,
                date=date,
                time=time,
            ).exclude(status='Cancelled')
            if self.instance:
                conflicts = conflicts.exclude(pk=self.instance.pk)
            if conflicts.exists():
                raise serializers.ValidationError({
                    "conflict": "This doctor already has an appointment scheduled at this date and time."
                })
        return attrs
