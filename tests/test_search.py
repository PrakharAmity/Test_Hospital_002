import pytest
from pathlib import Path
from datetime import date
from rest_framework import status
from rest_framework.test import APIClient
from django.conf import settings
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
def test_patient_search_by_name(api_client):
    """Test searching patient by name substring."""
    Patient.objects.create(
        full_name="Chitrangada Mukherjee",
        date_of_birth=date(1992, 1, 1),
        gender="Female",
        phone="+91-9988001122",
        blood_group="O+"
    )
    response = api_client.get('/api/patients/?search=Chitrangada')
    assert response.status_code == status.HTTP_200_OK
    results = response.json().get('results', [])
    assert any("Chitrangada" in p['full_name'] for p in results)

@pytest.mark.django_db
def test_patient_search_by_phone(api_client):
    """Test searching patient by phone number."""
    Patient.objects.create(
        full_name="Unique Phone Patient",
        date_of_birth=date(1987, 2, 2),
        gender="Male",
        phone="+91-9999988888",
        blood_group="AB+"
    )
    response = api_client.get('/api/patients/?search=9999988888')
    assert response.status_code == status.HTTP_200_OK
    results = response.json().get('results', [])
    assert len(results) >= 1
    assert results[0]['phone'] == "+91-9999988888"

@pytest.mark.django_db
def test_patient_search_no_results_returns_empty(api_client):
    """Test search with unmatched query returns HTTP 200 with empty list."""
    response = api_client.get('/api/patients/?search=NonExistentPatientQueryXYZ')
    assert response.status_code == status.HTTP_200_OK
    results = response.json().get('results', [])
    assert len(results) == 0

@pytest.mark.django_db
def test_search_simulated_error_handling(api_client):
    """Test that server error simulation parameter cleanly triggers HTTP 500."""
    response = api_client.get('/api/patients/?simulate_error=true')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "error" in response.json()

from patients.services import PatientSearchService

@pytest.mark.django_db
def test_patient_search_resets_loading_state_on_error():
    """
    Issue 4 — Patient Search Remains Loading Forever After Server Error.
    When a search request encounters a server error or timeout, the loading state
    must be cleanly reset to allow future user searches.
    """
    service = PatientSearchService()
    with pytest.raises(ConnectionError):
        service.execute_search("simulate_error")

    # In challenge mode, is_loading remains True after the exception!
    # In solution mode, error recovery ensures is_loading is reset to False.
    assert service.is_loading is False, (
        "Search service loading state remained True after server error. "
        "Search button remains permanently disabled and spinner spins forever."
    )

@pytest.mark.django_db
def test_patient_search_resets_loading_state_on_success():
    """Verify that successful queries leave the service in a ready, not-loading state."""
    service = PatientSearchService()
    service.execute_search("Test")
    assert service.is_loading is False

