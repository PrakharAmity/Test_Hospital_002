import pytest
from decimal import Decimal
from datetime import date
from rest_framework import status
from rest_framework.test import APIClient
from patients.models import Patient
from appointments.models import Doctor, Appointment
from billing.models import Bill
from accounts.models import User

@pytest.fixture
def api_client():
    client = APIClient()
    user = User.objects.filter(username='admin').first()
    if not user:
        user = User.objects.create_superuser(username='admin_test', email='admin@test.com', password='password123')
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def sample_patient():
    return Patient.objects.create(
        full_name="Sunil Gavaskar",
        date_of_birth=date(1975, 6, 10),
        gender="Male",
        phone="+91-9870001122",
        blood_group="B+"
    )

@pytest.mark.django_db
def test_bill_creation_and_invoice_generation(api_client, sample_patient):
    """Test generating a new invoice for a patient."""
    payload = {
        "patient": str(sample_patient.id),
        "amount": "2500.00",
        "discount_percent": "0.00",
        "tax_percent": "18.00",
        "paid_status": False
    }
    response = api_client.post('/api/bills/', payload, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert Decimal(data['total_amount']) == Decimal('2950.00')

@pytest.mark.django_db
def test_billing_total_with_discount_and_gst(api_client, sample_patient):
    """
    Issue 5 — Billing Calculation Returns Incorrect Invoice Total.
    Example specified in QA challenge:
      Amount: ₹10,000
      Discount: 10%
      GST: 18%
    Correct financial order:
      Taxable Amount = 10,000 - (10% of 10,000) = ₹9,000
      GST = 18% of ₹9,000 = ₹1,620
      Total Invoice = ₹9,000 + ₹1,620 = ₹10,620.00
    """
    bill = Bill(
        patient=sample_patient,
        amount=Decimal('10000.00'),
        discount_percent=Decimal('10.00'),
        tax_percent=Decimal('18.00')
    )
    bill.save()

    # In challenge mode, incorrect tax calculation order yields 10,800.00.
    # In solution mode, compliant Decimal calculation yields 10,620.00.
    assert bill.total_amount == Decimal('10620.00'), (
        f"Incorrect invoice total: expected Decimal('10620.00'), got {bill.total_amount}."
    )

@pytest.mark.django_db
def test_billing_decimal_precision_no_float_drift(api_client, sample_patient):
    """Test Decimal financial precision avoiding binary floating point rounding drift."""
    bill = Bill(
        patient=sample_patient,
        amount=Decimal('1234.50'),
        discount_percent=Decimal('5.00'),
        tax_percent=Decimal('18.00')
    )
    bill.save()
    # 1234.50 - 5% (61.73) = 1172.77; Tax 18% (211.10) = 1383.87
    assert isinstance(bill.total_amount, Decimal)
    assert bill.total_amount > Decimal('1000.00')

@pytest.mark.django_db
def test_billing_discount_only_calculation(api_client, sample_patient):
    """Test invoice total when discount is applied with 0% tax."""
    bill = Bill(
        patient=sample_patient,
        amount=Decimal('5000.00'),
        discount_percent=Decimal('20.00'),
        tax_percent=Decimal('0.00')
    )
    bill.save()
    assert bill.total_amount == Decimal('4000.00')

@pytest.mark.django_db
def test_billing_tax_only_calculation(api_client, sample_patient):
    """Test invoice total when tax is applied with 0% discount."""
    bill = Bill(
        patient=sample_patient,
        amount=Decimal('2000.00'),
        discount_percent=Decimal('0.00'),
        tax_percent=Decimal('18.00')
    )
    bill.save()
    assert bill.total_amount == Decimal('2360.00')

@pytest.mark.django_db
def test_billing_payment_status_update(api_client, sample_patient):
    """Test updating the payment status of an existing bill."""
    bill = Bill.objects.create(
        patient=sample_patient,
        amount=Decimal('1500.00'),
        discount_percent=Decimal('0.00'),
        tax_percent=Decimal('18.00'),
        paid_status=False
    )
    response = api_client.patch(f'/api/bills/{bill.id}/', {'paid_status': True}, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['paid_status'] is True
    bill.refresh_from_db()
    assert bill.paid_status is True
