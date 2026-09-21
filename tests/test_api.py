import pytest
from datetime import date, time
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import User
from patients.models import Patient
from appointments.models import Doctor, Appointment
from prescriptions.models import Prescription

@pytest.fixture
def api_client():
    client = APIClient()
    user, _ = User.objects.get_or_create(
        username="admin_api",
        defaults={"role": "admin", "is_staff": True, "is_superuser": True}
    )
    user.set_password("AdminPass123!")
    user.save()
    client.force_authenticate(user=user)
    return client

@pytest.mark.django_db
def test_auth_jwt_obtain_and_refresh_tokens():
    """Test obtaining JWT token pair and refreshing the access token."""
    User.objects.filter(username="jwt_user").delete()
    user = User.objects.create_user(
        username="jwt_user",
        email="jwt@medledger.local",
        password="TestPassword123!",
        role="doctor"
    )

    client = APIClient()
    token_resp = client.post('/api/auth/token/', {
        "username": "jwt_user",
        "password": "TestPassword123!"
    }, format='json')

    assert token_resp.status_code == status.HTTP_200_OK
    data = token_resp.json()
    assert 'access' in data
    assert 'refresh' in data
    assert data['user']['role'] == "doctor"

    refresh_resp = client.post('/api/auth/refresh/', {
        "refresh": data['refresh']
    }, format='json')
    assert refresh_resp.status_code == status.HTTP_200_OK
    assert 'access' in refresh_resp.json()

@pytest.mark.django_db
def test_doctor_list_api_status_and_schema(api_client):
    """Test retrieving list of doctors and verifying schema attributes."""
    Doctor.objects.create(
        name="Dr. Hemant Joshi",
        department="Pediatrics",
        experience=14,
        consultation_fee=750.00
    )
    response = api_client.get('/api/doctors/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    results = data.get('results', data)
    assert len(results) >= 1
    doc = results[0]
    for key in ['id', 'name', 'department', 'experience', 'consultation_fee']:
        assert key in doc

@pytest.mark.django_db
def test_prescription_create_and_pdf_download(api_client):
    """Test creating a prescription and generating a compliant downloadable PDF."""
    patient = Patient.objects.create(
        full_name="Anil Kumble",
        date_of_birth=date(1970, 10, 17),
        gender="Male",
        phone="+91-9876543299",
        blood_group="O+"
    )
    doctor = Doctor.objects.create(
        name="Dr. Srinath",
        department="Orthopedics",
        experience=15,
        consultation_fee=900.00
    )
    appointment = Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        date=date(2026, 11, 20),
        time=time(11, 0),
        status="Completed"
    )

    rx = Prescription.objects.create(
        appointment=appointment,
        medicines=[{"name": "Calcium 500mg", "dosage": "1 daily"}],
        dosage="1 tablet daily after breakfast",
        instructions="Maintain light mobility exercise."
    )

    pdf_response = api_client.get(f'/api/prescriptions/{rx.id}/pdf/')
    assert pdf_response.status_code == status.HTTP_200_OK
    assert pdf_response['Content-Type'] == 'application/pdf'
    # Valid PDF magic bytes header
    assert pdf_response.content.startswith(b'%PDF-')
    assert len(pdf_response.content) > 1000

@pytest.mark.django_db
def test_api_pagination_metadata_structure(api_client):
    """Test standard API pagination metadata keys."""
    response = api_client.get('/api/patients/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'count' in data
    assert 'next' in data
    assert 'previous' in data
    assert 'results' in data

@pytest.mark.django_db
def test_patient_serializer_validation_errors(api_client):
    """Test that patient serializer rejects too-short or invalid phone numbers."""
    invalid_payload = {
        "full_name": "Invalid Phone User",
        "date_of_birth": "1990-01-01",
        "gender": "Male",
        "phone": "123", # Invalid: less than 8 digits
        "blood_group": "A+"
    }
    response = api_client.post('/api/patients/', invalid_payload, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "phone" in response.json()

@pytest.mark.django_db
def test_bill_serializer_validation_errors(api_client):
    """Test that billing serializer rejects negative invoice amounts."""
    patient = Patient.objects.create(
        full_name="Negative Amount Patient",
        date_of_birth=date(1991, 1, 1),
        gender="Female",
        phone="+91-9876543200",
        blood_group="B+"
    )
    invalid_payload = {
        "patient": str(patient.id),
        "amount": "-500.00",
        "discount_percent": "0.00",
        "tax_percent": "18.00"
    }
    response = api_client.post('/api/bills/', invalid_payload, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "amount" in response.json()
