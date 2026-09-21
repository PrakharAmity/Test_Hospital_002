import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

BUGGY_SEARCH_JS = """// MedLedger Patient Live Search Module (Challenge Mode)
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('patient-search-input');
    const searchButton = document.getElementById('patient-search-button');
    const searchSpinner = document.getElementById('patient-search-spinner');
    const patientTableBody = document.getElementById('patients-tbody');
    const errorMessage = document.getElementById('patient-search-error');

    function setLoadingState(loading) {
        if (searchButton) searchButton.disabled = loading;
        if (searchInput) searchInput.disabled = loading;
        if (searchSpinner) {
            searchSpinner.classList.toggle('d-none', !loading);
        }
    }

    function renderPatients(patients) {
        if (!patientTableBody) return;
        if (!patients || patients.length === 0) {
            patientTableBody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-muted">No patients found.</td></tr>';
            return;
        }
        patientTableBody.innerHTML = patients.map(p => `
            <tr>
                <td class="fw-semibold">${p.full_name}</td>
                <td><span class="badge bg-danger-subtle text-danger border border-danger-subtle">${p.blood_group}</span></td>
                <td>${p.gender}</td>
                <td>${p.phone}</td>
                <td>${p.date_of_birth}</td>
                <td>
                    <span class="badge bg-success-subtle text-success border border-success-subtle">Active</span>
                </td>
            </tr>
        `).join('');
    }

    function executeSearch(query) {
        if (errorMessage) errorMessage.classList.add('d-none');
        setLoadingState(true);

        fetch(`/api/patients/?search=${encodeURIComponent(query)}`)
            .then(res => {
                if (!res.ok) {
                    throw new Error("Simulated or real server error occurred during patient search.");
                }
                return res.json();
            })
            .then(data => {
                const results = data.results !== undefined ? data.results : data;
                renderPatients(results);
                // Issue 4: setLoadingState(false) is ONLY executed on success!
                // If the fetch fails, search button remains disabled and spinner never stops!
                setLoadingState(false);
            });
            // Intentionally missing .catch() and .finally() error recovery
    }

    if (searchButton) {
        searchButton.addEventListener('click', () => {
            const q = searchInput ? searchInput.value.trim() : '';
            executeSearch(q);
        });
    }

    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                executeSearch(searchInput.value.trim());
            }
        });
    }
});
"""

FIXED_SEARCH_JS = """// MedLedger Patient Live Search Module (Solution Mode)
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('patient-search-input');
    const searchButton = document.getElementById('patient-search-button');
    const searchSpinner = document.getElementById('patient-search-spinner');
    const patientTableBody = document.getElementById('patients-tbody');
    const errorMessage = document.getElementById('patient-search-error');

    function setLoadingState(loading) {
        if (searchButton) searchButton.disabled = loading;
        if (searchInput) searchInput.disabled = loading;
        if (searchSpinner) {
            searchSpinner.classList.toggle('d-none', !loading);
        }
    }

    function renderPatients(patients) {
        if (!patientTableBody) return;
        if (!patients || patients.length === 0) {
            patientTableBody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-muted">No patients found.</td></tr>';
            return;
        }
        patientTableBody.innerHTML = patients.map(p => `
            <tr>
                <td class="fw-semibold">${p.full_name}</td>
                <td><span class="badge bg-danger-subtle text-danger border border-danger-subtle">${p.blood_group}</span></td>
                <td>${p.gender}</td>
                <td>${p.phone}</td>
                <td>${p.date_of_birth}</td>
                <td>
                    <span class="badge bg-success-subtle text-success border border-success-subtle">Active</span>
                </td>
            </tr>
        `).join('');
    }

    function executeSearch(query) {
        if (errorMessage) errorMessage.classList.add('d-none');
        setLoadingState(true);

        fetch(`/api/patients/?search=${encodeURIComponent(query)}`)
            .then(res => {
                if (!res.ok) {
                    throw new Error("Simulated or real server error occurred during patient search.");
                }
                return res.json();
            })
            .then(data => {
                const results = data.results !== undefined ? data.results : data;
                renderPatients(results);
            })
            .catch(err => {
                if (errorMessage) {
                    errorMessage.textContent = err.message || "Failed to load patient records.";
                    errorMessage.classList.remove('d-none');
                }
            })
            .finally(() => {
                // Fixed: Loading state and search button are always reset in finally block!
                setLoadingState(false);
            });
    }

    if (searchButton) {
        searchButton.addEventListener('click', () => {
            const q = searchInput ? searchInput.value.trim() : '';
            executeSearch(q);
        });
    }

    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                executeSearch(searchInput.value.trim());
            }
        });
    }
});
"""

class Command(BaseCommand):
    help = "Toggle MedLedger between Challenge Mode (6 intentional bugs) and Solution Mode (all tests pass)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--fixed',
            action='store_true',
            help='Switch to Solution Mode: fix all 6 bugs so all 36 tests pass.'
        )
        parser.add_argument(
            '--bugs',
            action='store_true',
            help='Switch to Challenge Mode: activate the 6 intentional bugs for debugging challenges.'
        )

    def handle(self, *args, **options):
        base_dir = settings.BASE_DIR
        env_file = base_dir / '.env'
        js_file = base_dir / 'static' / 'js' / 'patient_search.js'
        js_file.parent.mkdir(parents=True, exist_ok=True)

        if options['fixed']:
            # Set fixed mode
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write("MEDLEDGER_CHALLENGE_MODE=False\n")
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write(FIXED_SEARCH_JS)
            self.stdout.write(self.style.SUCCESS("[OK] Successfully switched to Solution Mode! (MEDLEDGER_CHALLENGE_MODE=False)"))
            self.stdout.write(self.style.SUCCESS("  Run 'pytest' to verify all 36 tests pass."))
        else:
            # Default to challenge mode
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write("MEDLEDGER_CHALLENGE_MODE=True\n")
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write(BUGGY_SEARCH_JS)
            self.stdout.write(self.style.WARNING("! Successfully switched to Challenge Mode! (MEDLEDGER_CHALLENGE_MODE=True)"))
            self.stdout.write(self.style.WARNING("  6 intentional bugs active. 6 tests will fail deterministically."))
