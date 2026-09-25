# AI Context

## Project

MedLedger is an offline-capable hospital management system for patient records, doctor scheduling, clinical billing with GST, prescription PDF issuance, and financial reporting via web dashboards and REST APIs.

## Tech Stack

- **Backend**: Python 3.12, Django 5.1, Django REST Framework 3.14+, SimpleJWT, django-filter
- **Database**: SQLite via Django ORM
- **Export & Frontend**: ReportLab, Django Templates, Bootstrap 5.3, Vanilla JS
- **Testing**: pytest, pytest-django, Factory Boy, Faker

## Repository Structure

```
medledger/      # Project settings, WSGI/ASGI, root URLs
accounts/       # RBAC User model, JWT authentication, permissions
patients/       # Patient registry, pagination, search service
appointments/   # Consultations, scheduling filters, ViewSets
billing/        # Invoices, tax/discount calculation, revenue analytics
prescriptions/  # Prescriptions, ReportLab PDF generation
dashboard/      # Server-rendered HTML dashboard views
static/js/      # Patient search client logic
tests/          # Pytest suite
```

## Entry Points

- **Backend Server**: `python manage.py runserver 0.0.0.0:8000` via `manage.py`
- **Root Router**: `medledger/urls.py` (mounts `/api/` apps and `/` dashboard)
- **Configuration**: `medledger/settings.py` (database, JWT, DRF defaults, auth model)
- **Fixtures**: `python manage.py loaddata fixtures/seed_data.json`

## Architecture

- **API Flow**: Request → Router (`urls.py`) → JWT/Session Auth → Permissions → FilterSet → ModelViewSet → Serializer validation → ORM → SQLite → JSON.
- **Dashboard Flow**: Request → Session Auth (`@login_required`) → View (`dashboard/views.py`) → ORM query/aggregation → Paginator → Template → HTML.
- **Domain Logic**: Resides in model methods (`Bill.calculate_total`), services (`PatientSearchService`), and generators (`pdf.py`).
- **Data Layer**: Relational models in SQLite accessed exclusively via Django ORM with UUID primary keys.

## Important Modules

### Accounts & Security (`accounts/`)
- `User` (`models.py`) — `AbstractUser` with role choices (`admin`, `doctor`, `receptionist`) and boolean role properties.
- `permissions.py` — DRF permissions (`IsAdminRole`, `IsDoctorRole`, `IsReceptionistRole`, `IsDoctorOrAdminRole`) validating `request.user.role`.

### Patients & Search (`patients/`)
- `Patient` (`models.py`) — Patient entity with demographics, blood group, and UUID keys.
- `CustomPatientPagination` (`pagination.py`) — `PageNumberPagination` subclass (page size: 10).
- `PatientSearchService` (`services.py`) — Manages search execution and transient `is_loading` / `last_error` states.

### Appointments & Scheduling (`appointments/`)
- `Doctor` & `Appointment` (`models.py`) — Doctor registry and consultations with lifecycle statuses (`Scheduled`, `In-Progress`, `Completed`, `Cancelled`).
- `AppointmentFilter` (`filters.py`) — `FilterSet` filtering by doctor UUID, department, status, and dates (`start_date`, `end_date`).
- `AppointmentViewSet` (`views.py`) — Consultations CRUD, filtering, and deletion.

### Billing & Revenue (`billing/`)
- `Bill` (`models.py`) — Invoices for patients/appointments. `calculate_total()` applies discount and GST percentages to gross `amount` into `total_amount`.
- `RevenueAnalyticsView` (`views.py`) — Aggregates financial metrics (`total_billed`, `collected`, `outstanding`) via ORM queries.

### Prescriptions (`prescriptions/`)
- `Prescription` (`models.py`) — JSON medicine regimens and dosage instructions tied to `Appointment`.
- `generate_prescription_pdf` (`pdf.py`) — ReportLab PDF generator consumed by `download_pdf` action on `PrescriptionViewSet`.

## Data Relationships

- **Patient Registration**: Request → `PatientSerializer` validation → `Patient.objects.create()` → UUID assigned.
- **Appointment Booking**: Request → validated with `Patient` and `Doctor` foreign keys → saved as `Appointment`.
- **Billing Calculation**: `Bill.save()` triggers `calculate_total()` with `amount`, `discount_percent`, `tax_percent` → persists `total_amount`.
- **Revenue Aggregation**: `Bill.objects.aggregate()` filters on `paid_status` → sums `total_amount` into metrics payload.
- **Prescription PDF**: `Prescription` model → `generate_prescription_pdf()` → ReportLab canvas → `HttpResponse(content_type='application/pdf')`.
- **Client Search**: DOM input → `fetch('/api/patients/?search=...')` → updates table rows and toggles loading spinner.

## Debugging Invariants

- Domain models (`Patient`, `Doctor`, `Appointment`, `Bill`, `Prescription`) use UUID primary keys instead of auto-incrementing integers.
- Role permissions require `request.user.is_authenticated` before evaluating `request.user.role`.
- List filtering delegates directly to `django_filters` backends using explicit lookup expressions.
- Invoice totals in `Bill.total_amount` derive strictly from `calculate_total()` on `save()`.
- Client search UI state must synchronize with asynchronous request completion and error lifecycles.

## Testing

- **Framework**: `pytest` with `pytest-django` (`pytest.ini`).
- **Directory**: `tests/`.
- **Suites**:
  - `test_api.py`: Auth tokens, endpoint contracts.
  - `test_appointments.py`: Consultations, filters, deletions.
  - `test_billing.py`: Invoicing, tax/discount calculations.
  - `test_patients.py`: Patient CRUD, pagination.
  - `test_permissions.py`: RBAC across admin, doctor, receptionist.
  - `test_search.py`: Live search and error recovery.

## Runtime / Commands

- **Dependencies**: `pip install -r requirements.txt`
- **Run Server**: `python manage.py runserver 0.0.0.0:8000`
- **Migrate**: `python manage.py migrate`
- **Seed Data**: `python manage.py loaddata fixtures/seed_data.json`
- **Run Tests**: `pytest`

## Debugging Context

- **Boundary Separation**: `/api/` delivers JSON via DRF; root routes render HTML templates via session login.
- **Role Constants**: Roles are lowercase strings (`admin`, `doctor`, `receptionist`) on `User.role`.
- **Filter Lookups**: Appointment date filtering uses Django field lookups (`gte`, `lte`, `lt`, `gt`).
- **Numeric Precision**: Monetary fields use `DecimalField`; financial calculations require exact `Decimal` precision.
- **State Ownership**: `PatientSearchService` and client `patient_search.js` manage transient UI/loading state independently of DB records.
