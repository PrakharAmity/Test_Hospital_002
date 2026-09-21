from django.conf import settings
from .models import Patient

class PatientSearchService:
    """
    Search service managing patient search queries and loading/error states.
    """
    def __init__(self):
        self.is_loading = False
        self.last_error = None
        self.results = []

    def execute_search(self, query):
        self.is_loading = True
        self.last_error = None
        try:
            if query == "simulate_error" or query == "timeout":
                raise ConnectionError("Simulated hospital database connection timeout.")
            self.results = list(Patient.objects.filter(full_name__icontains=query))
            # Successful query sets is_loading to False
            self.is_loading = False
            return self.results
        except Exception as e:
            self.last_error = str(e)
            # Issue 4 — Buggy: fails to reset loading state upon exception in challenge mode!
            # In challenge mode, is_loading remains True forever after an error.
            # In solution mode, error recovery resets is_loading to False.
            if not getattr(settings, 'MEDLEDGER_CHALLENGE_MODE', True):
                self.is_loading = False
            # In challenge mode: self.is_loading remains True!
            raise
