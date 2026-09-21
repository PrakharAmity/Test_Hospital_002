import pytest
from datetime import date
from rest_framework import status
from rest_framework.test import APIClient
from patients.models import Patient
from accounts.models import User

@pytest.fixture
def api_client():
    client = APIClient()
    user = User.objects.filter(username='admin').first()
    if not user:
        user = User.objects.create_superuser(username='admin_test', email='admin@test.com', password='password123')
    client.force_authenticate(user=user)
    return client

@pytest.mark.django_db
def test_patient_list_and_create(api_client):
    """Test patient creation via API and listing."""
    payload = {
        "full_name": "Ramesh Gupta",
        "date_of_birth": "1985-05-15",
        "gender": "Male",
        "phone": "+91-9812345678",
        "email": "ramesh.gupta@example.com",
        "blood_group": "B+",
        "address": "42 MG Road, Bengaluru",
        "emergency_contact": "+91-9876543210"
    }
    response = api_client.post('/api/patients/', payload, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['full_name'] == "Ramesh Gupta"
    assert data['blood_group'] == "B+"

    list_response = api_client.get('/api/patients/')
    assert list_response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_patient_retrieve_update_delete(api_client):
    """Test CRUD operations: retrieve, partial update, and deletion of a patient."""
    patient = Patient.objects.create(
        full_name="Meena Kumari",
        date_of_birth=date(1990, 3, 20),
        gender="Female",
        phone="+91-9988776655",
        email="meena@example.com",
        blood_group="A+",
        address="10 Park Street, Kolkata"
    )

    # Retrieve
    retrieve_resp = api_client.get(f'/api/patients/{patient.id}/')
    assert retrieve_resp.status_code == status.HTTP_200_OK
    assert retrieve_resp.json()['full_name'] == "Meena Kumari"

    # Update
    update_resp = api_client.patch(f'/api/patients/{patient.id}/', {"address": "15 Park Street, Kolkata"}, format='json')
    assert update_resp.status_code == status.HTTP_200_OK
    assert update_resp.json()['address'] == "15 Park Street, Kolkata"

    # Delete
    delete_resp = api_client.delete(f'/api/patients/{patient.id}/')
    assert delete_resp.status_code == status.HTTP_204_NO_CONTENT
    assert not Patient.objects.filter(id=patient.id).exists()

@pytest.mark.django_db
def test_patient_pagination_page_size_and_no_skipped_records(api_client):
    """
    Issue 2 — Pagination Skips the Last Patient on Every Page.
    The patient registry must return exactly 10 patients on page 1 without skipping records.
    """
    # Ensure at least 15 patients exist
    count = Patient.objects.count()
    if count < 15:
        for i in range(15 - count):
            Patient.objects.create(
                full_name=f"Test Patient {i}",
                date_of_birth=date(1990, 1, 1),
                gender="Male",
                phone=f"+91-98000000{i:02d}",
                blood_group="O+"
            )

    response = api_client.get('/api/patients/?page=1')
    assert response.status_code == status.HTTP_200_OK
    results = response.json().get('results', [])

    # In challenge mode, the slicing bug drops the 10th item (returning only 9).
    # In solution mode, exactly 10 patients are returned.
    assert len(results) == 10, f"Expected exactly 10 patients per page, but got {len(results)}."

@pytest.mark.django_db
def test_patient_pagination_second_page(api_client):
    """Test pagination navigation to page 2 with proper count metadata."""
    count = Patient.objects.count()
    if count < 15:
        for i in range(15 - count):
            Patient.objects.create(
                full_name=f"Page Two Patient {i}",
                date_of_birth=date(1992, 2, 2),
                gender="Female",
                phone=f"+91-98110000{i:02d}",
                blood_group="A+"
            )

    response = api_client.get('/api/patients/?page=2')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'count' in data
    assert 'next' in data
    assert 'previous' in data
    assert data['previous'] is not None

@pytest.mark.django_db
def test_patient_filter_by_blood_group(api_client):
    """Test filtering patient records by blood group metadata."""
    Patient.objects.create(
        full_name="Rare AB Blood Patient",
        date_of_birth=date(1988, 7, 10),
        gender="Male",
        phone="+91-9123456789",
        blood_group="AB-"
    )
    response = api_client.get('/api/patients/?blood_group=AB-')
    assert response.status_code == status.HTTP_200_OK
    results = response.json().get('results', [])
    assert len(results) >= 1
    for p in results:
        assert p['blood_group'] == "AB-"

@pytest.mark.django_db
def test_patient_filter_by_registered_date(api_client):
    """Test filtering patient records by registered date range."""
    today = date.today().isoformat()
    response = api_client.get(f'/api/patients/?registered_date__gte={today}')
    assert response.status_code == status.HTTP_200_OK
    results = response.json().get('results', [])
    for p in results:
        assert p['registered_date'] >= today
