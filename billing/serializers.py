from rest_framework import serializers
from decimal import Decimal
from .models import Bill

class BillSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    calculated_total = serializers.DecimalField(source='total_amount', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Bill
        fields = [
            'id', 'appointment', 'patient', 'patient_name',
            'amount', 'discount_percent', 'tax_percent',
            'total_amount', 'calculated_total', 'paid_status',
            'generated_date'
        ]
        read_only_fields = ['id', 'total_amount', 'generated_date']

    def validate_amount(self, value):
        if value < Decimal('0.00'):
            raise serializers.ValidationError("Invoice amount cannot be negative.")
        return value

    def validate_discount_percent(self, value):
        if value < Decimal('0.00') or value > Decimal('100.00'):
            raise serializers.ValidationError("Discount percentage must be between 0 and 100.")
        return value

    def validate_tax_percent(self, value):
        if value < Decimal('0.00') or value > Decimal('100.00'):
            raise serializers.ValidationError("Tax percentage must be between 0 and 100.")
        return value
