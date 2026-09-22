
# MedLedger — Hospital Management & Patient Records Dashboard

MedLedger is an interactive, production-grade Hospital Management and Patient Records Dashboard designed for doctors, receptionists, hospital administrators, and healthcare staff. It enables healthcare organizations to manage patient registrations, doctor appointment scheduling, prescription generation, commercial billing with GST compliance, and audited financial analytics through a modern offline-first Django web application.

This repository serves as a **real-world debugging challenge** for AI-assisted debugging platforms and evaluation engines.

---

## 1. Application Overview

### Core Features

- **Dynamic Patient Registry**: Search and browse patient records with medical metadata, blood groups, contact details, and pagination.
- **Appointment Scheduling**: Book, reschedule, and manage doctor consultations with double-booking conflict detection and availability filtering.
- **Smart Filtering & Sorting**: Filter appointments across medical departments, doctor assignments, statuses, and calendar date ranges.
- **Interactive Billing Dashboard**: Generate itemized patient invoices, calculate discounts and GST, track payment status, and audit outstanding hospital receivables.
- **Prescription Generator & PDF Export**: Issue clinical prescriptions with dosage regimens and download official, high-resolution hospital PDF documents offline using ReportLab.
- **Audited Financial Analytics**: Hospital statistics covering gross billed revenue, total collections, outstanding receivables, doctor capacity, and department workload.
- **Role-Based Authentication (RBAC)**: Secure multi-tier authentication with JWT API support and distinct operational roles:
  - **Administrator** (`admin`)
  - **Doctor** (`dr.sharma`)
  - **Receptionist** (`reception`)

### Technology Stack

- **Backend**: Python 3.12, Django 5.1, Django REST Framework, SimpleJWT, Django Filter, ReportLab
- **Database**: SQLite (100% offline, zero external service dependencies)
- **Frontend**: Django Templates, Bootstrap 5.3 (bundled locally), Vanilla JavaScript, CSS Variables, Responsive Medical UI
- **Testing**: Pytest, pytest-django, Factory Boy
- **Data Fixtures**: 1,128 deterministic records generated via Faker (150 patients, 25 doctors, 400 appointments, 250 bills, 300 prescriptions)

---

## 2. Debugging Challenge

QA engineers and healthcare staff have reported several operational issues in the MedLedger dashboard. The repository contains exactly **6 intentional logical bugs** that must be investigated and resolved.

### Issue 1 — Appointment Date Range Excludes Boundary Date
- **User Symptom**: Receptionists filtering appointments between **1 September 2026** and **30 September 2026** cannot see appointments scheduled exactly on **30 September**.
- **Reproduction**:
  1. Open Appointment Scheduling dashboard.
  2. Set Start Date: `2026-09-01`.
  3. Set End Date: `2026-09-30`.
  4. Appointments scheduled on September 30 do not appear in the filtered results.

### Issue 2 — Pagination Skips the Last Patient on Every Page
- **User Symptom**: The patient registry is configured to display **10 patients per page**, but only **9** appear. When navigating from Page 1 to Page 2, one patient record is skipped completely.
- **Reproduction**:
  1. Open Patient Registry.
  2. Navigate to Page 1 and count displayed patient records (9 instead of 10).
  3. Navigate to Page 2 and compare IDs with Page 1; the 10th record from the database is missing.

### Issue 3 — Removing Appointment Deletes Wrong Record
- **User Symptom**: Deleting an appointment removes another patient's appointment instead of the selected one.
- **Reproduction**:
  1. Open Appointment Scheduling.
  2. Select an appointment and click Delete.
  3. Refresh the appointment list; another appointment has disappeared while the selected appointment remains.

### Issue 4 — Patient Search Remains Loading Forever After Server Error
- **User Symptom**: When searching for a patient and an asynchronous error or network timeout occurs, the search button remains permanently disabled and the spinner continues to spin indefinitely.
- **Reproduction**:
  1. Open Patient Registry.
  2. Trigger a search query during a simulated server error or timeout.
  3. Observe that the loading spinner never stops and future search interactions are blocked.

### Issue 5 — Billing Calculation Returns Incorrect Invoice Total
- **User Symptom**: Invoices with both discount and GST produce incorrect totals.
  - Example: Base Amount = ₹10,000, Discount = 10%, GST = 18%.
  - The displayed total does not match expected tax regulations.

### Issue 6 — Unauthorized Receptionist Can Access Admin Revenue Reports
- **User Symptom**: Users authenticated with the Receptionist role can directly access confidential hospital revenue analytics endpoints.
- **Reproduction**:
  1. Authenticate with a receptionist account.
  2. Navigate to `/api/billing/revenue/` or the Revenue Analytics dashboard.
  3. Financial revenue data loads successfully instead of being restricted.

---

## 3. Expected Behavior After Fixing Bugs

Once all issues are resolved:

1. **Date Filters**: Filtering appointments by date range includes records scheduled on the selected maximum boundary date.
2. **Pagination**: Every pagination page displays exactly 10 patients without skipping records.
3. **Appointment Deletion**: Deleting an appointment removes only the targeted record by primary key/UUID.
4. **Search Resilience**: Failed or timed-out searches cleanly reset loading states, re-enable buttons, and allow retrying.
5. **Billing Precision**: Invoices apply discounts first and calculate GST on the taxable net amount using Decimal arithmetic (₹10,000 with 10% discount and 18% GST correctly equals ₹10,620.00).
6. **Role Permissions**: Receptionists and doctors receive HTTP 403 Forbidden when requesting admin revenue endpoints.
7. **Automated Test Suite**: All 36 automated tests pass with exit code 0 (`36 passed in X.XXs`).

---

## 4. Seed Credentials

| Role | Username | Password |
| :--- | :--- | :--- |
| **Administrator** | `admin` | `AdminPass123!` |
| **Doctor** | `dr.sharma` | `DoctorPass123!` |
| **Receptionist** | `reception` | `ReceptionPass123!` |
