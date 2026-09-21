// MedLedger Patient Live Search Module (Challenge Mode)
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
