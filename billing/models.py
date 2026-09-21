import uuid
from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.conf import settings
from patients.models import Patient
from appointments.models import Appointment

class Bill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bills'
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bills')
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base gross amount")
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Discount percentage (e.g. 10.00 for 10%)")
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=18.00, help_text="GST / Tax percentage (default 18.00%)")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    paid_status = models.BooleanField(default=False)
    generated_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-generated_date']

    def calculate_total(self):
        """
        Calculate invoice total after applying discount and GST.
        """
        amount_dec = Decimal(str(self.amount))
        discount_dec = Decimal(str(self.discount_percent if self.discount_percent is not None else '0.00'))
        tax_dec = Decimal(str(self.tax_percent if self.tax_percent is not None else '18.00'))

        # Issue 5 — Incorrect billing calculation order and float precision:
        # In challenge mode, tax is applied to the gross pre-discount amount and calculated with floats.
        # In solution mode, discount is subtracted first to get taxable net, then GST is applied using Decimal arithmetic.
        if getattr(settings, 'MEDLEDGER_CHALLENGE_MODE', True):
            # Buggy: calculates tax on full amount, uses float, produces 10800 instead of 10620
            tax_val = float(amount_dec) * (float(tax_dec) / 100.0)
            disc_val = float(amount_dec) * (float(discount_dec) / 100.0)
            buggy_total = float(amount_dec) + tax_val - disc_val
            return Decimal(f"{buggy_total:.2f}")

        # Correct Decimal calculation:
        discount_amount = (amount_dec * (discount_dec / Decimal('100.00'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        taxable_amount = amount_dec - discount_amount
        tax_amount = (taxable_amount * (tax_dec / Decimal('100.00'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total = (taxable_amount + tax_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return total

    def save(self, *args, **kwargs):
        self.total_amount = self.calculate_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bill {self.id} for {self.patient.full_name} — ₹{self.total_amount}"
