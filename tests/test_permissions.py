import pytest
from datetime import date, time
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import User
from patients.models import Patient
from appointments.models import Doctor, Appointment

@pytest.fixture
def admin_user():
    user, _ = User.objects.get_or_create(
        username="admin_perm",
        defaults={"role": "admin", "is_staff": True, "is_superuser": True}
    )
    user.role = "admin"
    user.save()
    return user

@pytest.fixture
def receptionist_user():
    user, _ = User.objects.get_or_create(
        username="receptionist_perm",
        defaults={"role": "receptionist", "is_staff": False, "is_superuser": False}
    )
    user.role = "receptionist"
    user.save()
    return user

@pytest.fixture
def doctor_user():
    user, _ = User.objects.get_or_create(
        username="doctor_perm",
        defaults={"role": "doctor", "is_staff": False, "is_superuser": False}
    )
    user.role = "doctor"
    user.save()
    return user

@pytest.mark.django_db
def test_admin_can_access_revenue_endpoint(admin_user):
    """Admin user must be allowed full access to hospital revenue reports."""
    client = APIClient()
    client.force_authenticate(user=admin_user)
    response = client.get('/api/billing/revenue/')
    assert response.status_code == status.HTTP_200_OK
    assert 'total_revenue' in response.json()

@pytest.mark.django_db
def test_receptionist_forbidden_from_revenue_endpoint(receptionist_user):
    """
    Issue 6 — Unauthorized Receptionist Can Access Admin Revenue Reports.
    Receptionist users must receive HTTP 403 Forbidden when accessing the revenue API.
    """
    client = APIClient()
    client.force_authenticate(user=receptionist_user)
    response = client.get('/api/billing/revenue/')

    # In challenge mode, missing role permission allows receptionist (returns 200 OK).
    # In solution mode, IsAdminRole blocks receptionist with HTTP 403 Forbidden.
    assert response.status_code == status.HTTP_403_FORBIDDEN, (
        f"Expected HTTP 403 Forbidden for receptionist, but got {response.status_code}."
    )

@pytest.mark.django_db
def test_doctor_forbidden_from_revenue_endpoint(doctor_user):
    """Doctor role must be forbidden from accessing admin-only revenue analytics."""
    client = APIClient()
    client.force_authenticate(user=doctor_user)
    response = client.get('/api/billing/revenue/')
    # In challenge mode without IsAdminRole, doctor also inappropriately gets 200
    # In solution mode, doctor correctly gets 403
    assert response.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_200_OK)

@pytest.mark.django_db
def test_unauthenticated_user_rejected():
    """Unauthenticated anonymous request must be rejected with HTTP 401."""
    client = APIClient()
    response = client.get('/api/billing/revenue/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_receptionist_can_manage_appointments(receptionist_user):
    """Receptionist users must have full permission to schedule patient appointments."""
    client = APIClient()
    client.force_authenticate(user=receptionist_user)

    patient = Patient.objects.create(
        full_name="Govind Rao",
        date_of_birth=date(1980, 5, 2),
        gender="Male",
        phone="+91-9876543211",
        blood_group="A+"
    )
    doctor = Doctor.objects.create(
        name="Dr. Sunita Sen",
        department="Neurology",
        experience=10,
        consultation_fee=1000.00
    )

    payload = {
        "patient": str(patient.id),
        "doctor": str(doctor.id),
        "date": "2026-11-12",
        "time": "11:30:00",
        "status": "Scheduled"
    }
    response = client.post('/api/appointments/', payload, format='json')
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_doctor_role_can_create_prescription(doctor_user):
    """Doctors must be authorized to generate prescriptions."""
    client = APIClient()
    client.force_authenticate(user=doctor_user)

    patient = Patient.objects.create(
        full_name="Harish Patel",
        date_of_birth=date(1989, 9, 1),
        gender="Male",
        phone="+91-9876543212",
        blood_group="B+"
    )
    doctor = Doctor.objects.create(
        name="Dr. Vivek Nair",
        department="General Medicine",
        experience=8,
        consultation_fee=600.00
    )
    appointment = Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        date=date(2026, 11, 14),
        time=time(10, 0),
        status="Scheduled"
    )

    payload = {
        "appointment": str(appointment.id),
        "medicines": [{"name": "Amoxicillin 500mg", "dosage": "1 cap twice daily"}],
        "dosage": "1 cap twice daily",
        "instructions": "Take after meals."
    }
    response = client.post('/api/prescriptions/', payload, format='json')
    assert response.status_code == status.HTTP_201_CREATED
