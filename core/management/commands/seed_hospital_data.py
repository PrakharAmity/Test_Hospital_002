import json
import random
import uuid
from datetime import date, time, timedelta, datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from faker import Faker
from django.conf import settings

class Command(BaseCommand):
    help = "Generate realistic Indian hospital fixture data and save to fixtures/seed_data.json"

    def handle(self, *args, **options):
        fake = Faker('en_IN')
        Faker.seed(42)
        random.seed(42)

        fixtures = []

        # 1. Accounts: Admin, Doctor, Receptionist
        admin_id = 1
        doctor_user_id = 2
        receptionist_user_id = 3

        fixtures.extend([
            {
                "model": "accounts.user",
                "pk": admin_id,
                "fields": {
                    "username": "admin",
                    "password": make_password("AdminPass123!"),
                    "first_name": "Hospital",
                    "last_name": "Admin",
                    "email": "admin@medledger.local",
                    "role": "admin",
                    "is_staff": True,
                    "is_superuser": True,
                    "is_active": True,
                    "phone": "+91-9820011223",
                    "date_joined": "2026-01-01T00:00:00Z"
                }
            },
            {
                "model": "accounts.user",
                "pk": doctor_user_id,
                "fields": {
                    "username": "dr.sharma",
                    "password": make_password("DoctorPass123!"),
                    "first_name": "Rajesh",
                    "last_name": "Sharma",
                    "email": "dr.sharma@medledger.local",
                    "role": "doctor",
                    "is_staff": False,
                    "is_superuser": False,
                    "is_active": True,
                    "phone": "+91-9811223344",
                    "date_joined": "2026-01-01T00:00:00Z"
                }
            },
            {
                "model": "accounts.user",
                "pk": receptionist_user_id,
                "fields": {
                    "username": "reception",
                    "password": make_password("ReceptionPass123!"),
                    "first_name": "Pooja",
                    "last_name": "Verma",
                    "email": "reception@medledger.local",
                    "role": "receptionist",
                    "is_staff": False,
                    "is_superuser": False,
                    "is_active": True,
                    "phone": "+91-9877665544",
                    "date_joined": "2026-01-01T00:00:00Z"
                }
            }
        ])

        # 2. Doctors (25 doctors)
        departments = [
            "Cardiology", "Neurology", "Orthopedics", "Pediatrics",
            "Oncology", "General Medicine", "Dermatology", "ENT",
            "Gastroenterology", "Nephrology"
        ]

        doctor_uuids = [str(uuid.UUID(int=i + 1000)) for i in range(25)]
        doctor_names = [
            "Rajesh Sharma", "Ananya Iyer", "Vikram Patel", "Priya Nair", "Arjun Sen",
            "Sneha Reddy", "Rohan Mehta", "Kavita Rao", "Amit Deshmukh", "Sunita Chatterjee",
            "Manoj Bajpai", "Deepa Krishnan", "Sanjay Kapoor", "Meera Joshi", "Gaurav Malhotra",
            "Pooja Saxena", "Nitin Gupta", "Alka Trivedi", "Siddharth Bose", "Ritu Singhania",
            "Vivek Anand", "Divya Menon", "Karthik Raja", "Shweta Kulkarni", "Pradeep Varma"
        ]

        for i in range(25):
            dept = departments[i % len(departments)]
            fixtures.append({
                "model": "appointments.doctor",
                "pk": doctor_uuids[i],
                "fields": {
                    "name": doctor_names[i],
                    "department": dept,
                    "experience": 5 + (i * 3) % 25,
                    "availability": "Mon-Fri 09:00 - 17:00",
                    "consultation_fee": f"{500 + (i * 50):.2f}",
                    "phone": f"+91-{9800000000 + i * 11111}",
                    "email": f"{doctor_names[i].lower().replace(' ', '.')}@medledger.local",
                    "created_at": "2026-01-01T09:00:00Z"
                }
            })

        # 3. Patients (150 patients)
        patient_uuids = [str(uuid.UUID(int=i + 10000)) for i in range(150)]
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        genders = ['Male', 'Female', 'Other']

        for i in range(150):
            reg_date = date(2026, 1 + (i % 8), 1 + (i % 25)).isoformat()
            fixtures.append({
                "model": "patients.patient",
                "pk": patient_uuids[i],
                "fields": {
                    "full_name": fake.name(),
                    "date_of_birth": date(1960 + (i % 45), 1 + (i % 12), 1 + (i % 28)).isoformat(),
                    "gender": genders[i % len(genders)],
                    "phone": f"+91-{9700000000 + i * 13579}",
                    "email": f"patient_{i + 1}@example.com",
                    "blood_group": blood_groups[i % len(blood_groups)],
                    "address": f"{fake.street_address()}, {fake.city()}, India",
                    "emergency_contact": f"+91-{9600000000 + i * 24680}",
                    "registered_date": reg_date,
                    "created_at": f"{reg_date}T10:00:00Z"
                }
            })

        # 4. Appointments (400 appointments)
        appointment_uuids = [str(uuid.UUID(int=i + 50000)) for i in range(400)]
        statuses = ['Scheduled', 'Completed', 'In-Progress', 'Cancelled']
        times = ["09:30:00", "10:15:00", "11:00:00", "12:00:00", "14:00:00", "15:30:00", "16:15:00", "17:00:00"]

        # Ensure we have appointments specifically on Sept 1, Sept 15, and Sept 30 for boundary testing
        special_dates = {
            0: (date(2026, 9, 1), times[0]),
            1: (date(2026, 9, 15), times[1]),
            2: (date(2026, 9, 30), times[2]), # Boundary end date!
        }

        for i in range(400):
            p_uuid = patient_uuids[i % len(patient_uuids)]
            d_uuid = doctor_uuids[i % len(doctor_uuids)]
            if i in special_dates:
                appt_date, appt_time = special_dates[i]
            else:
                month = 1 + (i % 9) # Jan to Sep 2026
                day = 1 + (i % 28)
                appt_date = date(2026, month, day)
                appt_time = times[i % len(times)]

            fixtures.append({
                "model": "appointments.appointment",
                "pk": appointment_uuids[i],
                "fields": {
                    "patient": p_uuid,
                    "doctor": d_uuid,
                    "date": appt_date.isoformat(),
                    "time": appt_time,
                    "status": statuses[i % len(statuses)],
                    "notes": f"Routine clinical consultation checkup #{i + 1}.",
                    "created_at": f"{appt_date.isoformat()}T08:00:00Z"
                }
            })

        # 5. Bills (250 bills)
        bill_uuids = [str(uuid.UUID(int=i + 70000)) for i in range(250)]
        for i in range(250):
            appt_uuid = appointment_uuids[i]
            p_uuid = patient_uuids[i % len(patient_uuids)]
            gross = Decimal(f"{1000 + (i * 150):.2f}")
            disc = Decimal(f"{(i * 5) % 30:.2f}")
            tax = Decimal('18.00')

            # Correct total for seed data
            taxable = gross - (gross * (disc / Decimal('100.00')))
            total = taxable + (taxable * (tax / Decimal('100.00')))

            fixtures.append({
                "model": "billing.bill",
                "pk": bill_uuids[i],
                "fields": {
                    "appointment": appt_uuid,
                    "patient": p_uuid,
                    "amount": f"{gross:.2f}",
                    "discount_percent": f"{disc:.2f}",
                    "tax_percent": f"{tax:.2f}",
                    "total_amount": f"{total:.2f}",
                    "paid_status": (i % 3 != 0),
                    "generated_date": "2026-08-01T10:00:00Z"
                }
            })

        # 6. Prescriptions (300 prescriptions)
        common_medicines = [
            {"name": "Paracetamol 650mg", "dosage": "1 tablet", "instructions": "After food, twice daily"},
            {"name": "Amoxicillin 500mg", "dosage": "1 capsule", "instructions": "Morning and evening for 5 days"},
            {"name": "Pantoprazole 40mg", "dosage": "1 tablet", "instructions": "Empty stomach before breakfast"},
            {"name": "Metformin 500mg", "dosage": "1 tablet", "instructions": "With dinner"},
            {"name": "Atorvastatin 10mg", "dosage": "1 tablet", "instructions": "At bedtime"},
            {"name": "Cetirizine 10mg", "dosage": "1 tablet", "instructions": "As needed for allergy symptoms"}
        ]

        prescription_uuids = [str(uuid.UUID(int=i + 90000)) for i in range(300)]
        for i in range(300):
            appt_uuid = appointment_uuids[i]
            meds = [
                common_medicines[i % len(common_medicines)],
                common_medicines[(i + 2) % len(common_medicines)]
            ]
            fixtures.append({
                "model": "prescriptions.prescription",
                "pk": prescription_uuids[i],
                "fields": {
                    "appointment": appt_uuid,
                    "medicines": meds,
                    "dosage": "1 tablet twice daily after meals",
                    "instructions": "Complete the full antibiotic course. Avoid cold beverages and maintain hydration.",
                    "created_at": "2026-08-01T11:00:00Z"
                }
            })

        fixture_path = settings.BASE_DIR / 'fixtures' / 'seed_data.json'
        fixture_path.parent.mkdir(parents=True, exist_ok=True)
        with open(fixture_path, 'w', encoding='utf-8') as f:
            json.dump(fixtures, f, indent=2)

        self.stdout.write(self.style.SUCCESS(
            f"Successfully generated {len(fixtures)} records into {fixture_path}!\n"
            f"  - 3 Users (admin, doctor, receptionist)\n"
            f"  - 25 Doctors\n"
            f"  - 150 Patients\n"
            f"  - 400 Appointments\n"
            f"  - 250 Bills\n"
            f"  - 300 Prescriptions"
        ))
