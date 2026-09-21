import pytest
from datetime import date, time
from rest_framework import status
from rest_framework.test import APIClient
from patients.models import Patient
from appointments.models import Doctor, Appointment
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
def sample_doctor():
    return Doctor.objects.create(
        name="Dr. Alok Verma",
        department="Cardiology",
        experience=12,
        availability="Mon-Fri 09:00 - 17:00",
        consultation_fee=800.00
    )

@pytest.fixture
def sample_patient():
    return Patient.objects.create(
        full_name="Karan Malhotra",
        date_of_birth=date(1982, 4, 12),
        gender="Male",
        phone="+91-9876501234",
        blood_group="O+"
    )

@pytest.mark.django_db
def test_appointment_booking(api_client, sample_doctor, sample_patient):
    """Test standard appointment scheduling."""
    payload = {
        "patient": str(sample_patient.id),
        "doctor": str(sample_doctor.id),
        "date": "2026-10-15",
        "time": "10:00:00",
        "status": "Scheduled",
        "notes": "General cardiac consultation"
    }
    response = api_client.post('/api/appointments/', payload, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['date'] == "2026-10-15"
    assert data['doctor_name'] == "Dr. Alok Verma"

@pytest.mark.django_db
def test_appointment_conflict_detection(api_client, sample_doctor, sample_patient):
    """Test that double booking a doctor at the exact same date and time slot is prevented."""
    Appointment.objects.create(
        patient=sample_patient,
        doctor=sample_doctor,
        date=date(2026, 11, 5),
        time=time(14, 30),
        status="Scheduled"
    )

    conflict_payload = {
        "patient": str(sample_patient.id),
        "doctor": str(sample_doctor.id),
        "date": "2026-11-05",
        "time": "14:30:00",
        "status": "Scheduled"
    }
    response = api_client.post('/api/appointments/', conflict_payload, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "conflict" in response.json() or "non_field_errors" in response.json()

@pytest.mark.django_db
def test_appointment_date_range_includes_boundary_date(api_client, sample_doctor, sample_patient):
    """
    Issue 1 — Appointment Date Range Excludes Boundary Date.
    Appointments scheduled on the exact ending boundary date must be included in the query results.
    """
    # Create appointment on exact boundary date September 30, 2026
    boundary_date = "2026-09-30"
    boundary_appt = Appointment.objects.create(
        patient=sample_patient,
        doctor=sample_doctor,
        date=date(2026, 9, 30),
        time=time(11, 0),
        status="Scheduled",
        notes="Boundary consultation on Sept 30"
    )

    url = f"/api/appointments/?doctor={sample_doctor.id}&start_date=2026-09-01&end_date=2026-09-30"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    results = response.json().get('results', [])
    matching_ids = [a['id'] for a in results]

    # In challenge mode, 'lt' excludes Sept 30, causing this assertion to fail.
    # In solution mode, 'lte' includes Sept 30, causing this assertion to pass.
    assert str(boundary_appt.id) in matching_ids, (
        f"Appointment on boundary date {boundary_date} was excluded from filter results."
    )

@pytest.mark.django_db
def test_appointment_delete_removes_exact_record(api_client, sample_doctor, sample_patient):
    """
    Issue 3 — Removing Appointment Deletes Wrong Record.
    Deleting an appointment must strictly delete the record identified by its UUID.
    """
    patient2 = Patient.objects.create(
        full_name="Second Patient",
        date_of_birth=date(1995, 8, 20),
        gender="Female",
        phone="+91-9871112233",
        blood_group="B+"
    )

    appt_a = Appointment.objects.create(
        patient=sample_patient,
        doctor=sample_doctor,
        date=date(2026, 12, 1),
        time=time(9, 0),
        notes="First appointment A"
    )
    appt_b = Appointment.objects.create(
        patient=patient2,
        doctor=sample_doctor,
        date=date(2026, 12, 1),
        time=time(10, 0),
        notes="Target appointment B"
    )

    # Issue DELETE request specifically for appt_b
    response = api_client.delete(f'/api/appointments/{appt_b.id}/')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify that appt_b was deleted and appt_a was preserved
    appt_b_exists = Appointment.objects.filter(id=appt_b.id).exists()
    appt_a_exists = Appointment.objects.filter(id=appt_a.id).exists()

    # In challenge mode, appt_a was deleted and appt_b remained!
    assert not appt_b_exists, "Targeted appointment B was not deleted."
    assert appt_a_exists, "Wrong appointment A was incorrectly deleted instead of appointment B."

@pytest.mark.django_db
def test_appointment_reschedule_and_status_update(api_client, sample_doctor, sample_patient):
    """Test updating appointment time and status transition."""
    appt = Appointment.objects.create(
        patient=sample_patient,
        doctor=sample_doctor,
        date=date(2026, 12, 10),
        time=time(15, 0),
        status="Scheduled"
    )
    response = api_client.patch(
        f'/api/appointments/{appt.id}/',
        {"status": "Completed", "notes": "Patient consulted and vitals recorded."},
        format='json'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['status'] == "Completed"

@pytest.mark.django_db
def test_appointment_filter_by_doctor_and_department(api_client, sample_doctor, sample_patient):
    """Test filtering appointments by doctor UUID and department name."""
    Appointment.objects.create(
        patient=sample_patient,
        doctor=sample_doctor,
        date=date(2026, 12, 20),
        time=time(16, 0),
        status="Scheduled"
    )
    response = api_client.get(f'/api/appointments/?department=Cardiology')
    assert response.status_code == status.HTTP_200_OK
    results = response.json().get('results', [])
    assert len(results) >= 1
    for r in results:
        assert r['department'].lower() == "cardiology"
