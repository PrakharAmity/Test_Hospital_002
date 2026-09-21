from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'id', 'full_name', 'date_of_birth', 'gender',
            'phone', 'email', 'blood_group', 'address',
            'emergency_contact', 'registered_date', 'created_at'
        ]
        read_only_fields = ['id', 'registered_date', 'created_at']

    def validate_phone(self, value):
        if not value or len(value.strip()) < 8:
            raise serializers.ValidationError("Phone number must contain at least 8 digits.")
        return value.strip()
