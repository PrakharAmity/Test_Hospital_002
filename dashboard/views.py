from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.conf import settings
from decimal import Decimal
from patients.models import Patient
from appointments.models import Doctor, Appointment
from billing.models import Bill
from prescriptions.models import Prescription

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_overview')

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard_overview'))
        messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def overview_view(request):
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    total_appointments = Appointment.objects.count()
    scheduled_today = Appointment.objects.filter(status='Scheduled').count()

    # Financial KPIs
    billing_stats = Bill.objects.aggregate(
        total_revenue=Sum('total_amount'),
        collected=Sum('total_amount', filter=Q(paid_status=True)),
        outstanding=Sum('total_amount', filter=Q(paid_status=False))
    )

    # Department distribution
    dept_distribution = Doctor.objects.values('department').annotate(
        doctor_count=Count('id')
    ).order_by('-doctor_count')

    recent_appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-date', '-time')[:6]

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
        'scheduled_today': scheduled_today,
        'total_revenue': billing_stats['total_revenue'] or Decimal('0.00'),
        'collected_revenue': billing_stats['collected'] or Decimal('0.00'),
        'outstanding_revenue': billing_stats['outstanding'] or Decimal('0.00'),
        'dept_distribution': dept_distribution,
        'recent_appointments': recent_appointments,
        'active_tab': 'overview'
    }
    return render(request, 'dashboard/overview.html', context)

@login_required
def patients_view(request):
    query = request.GET.get('q', '').strip()
    blood_group = request.GET.get('blood_group', '').strip()

    patients_qs = Patient.objects.all().order_by('-registered_date', '-created_at')
    if query:
        patients_qs = patients_qs.filter(
            Q(full_name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query)
        )
    if blood_group:
        patients_qs = patients_qs.filter(blood_group=blood_group)

    paginator = Paginator(patients_qs, 10)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)

    context = {
        'page_obj': page_obj,
        'query': query,
        'blood_group': blood_group,
        'blood_groups': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
        'active_tab': 'patients'
    }
    return render(request, 'dashboard/patients.html', context)

@login_required
def appointments_view(request):
    doctor_id = request.GET.get('doctor', '').strip()
    department = request.GET.get('department', '').strip()
    status_filter = request.GET.get('status', '').strip()
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()

    appointments_qs = Appointment.objects.select_related('patient', 'doctor').all().order_by('date', 'time')

    if doctor_id:
        appointments_qs = appointments_qs.filter(doctor_id=doctor_id)
    if department:
        appointments_qs = appointments_qs.filter(doctor__department__iexact=department)
    if status_filter:
        appointments_qs = appointments_qs.filter(status__iexact=status_filter)
    if start_date:
        appointments_qs = appointments_qs.filter(date__gte=start_date)
    if end_date:
        # Respect challenge mode for UI consistency
        if getattr(settings, 'MEDLEDGER_CHALLENGE_MODE', True):
            appointments_qs = appointments_qs.filter(date__lt=end_date)
        else:
            appointments_qs = appointments_qs.filter(date__lte=end_date)

    paginator = Paginator(appointments_qs, 15)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)

    doctors = Doctor.objects.all().order_by('name')
    departments = Doctor.objects.values_list('department', flat=True).distinct().order_by('department')

    context = {
        'page_obj': page_obj,
        'doctors': doctors,
        'departments': departments,
        'doctor_id': doctor_id,
        'department': department,
        'status_filter': status_filter,
        'start_date': start_date,
        'end_date': end_date,
        'active_tab': 'appointments'
    }
    return render(request, 'dashboard/appointments.html', context)

@login_required
def billing_view(request):
    bills_qs = Bill.objects.select_related('patient', 'appointment__doctor').all().order_by('-generated_date')

    status_filter = request.GET.get('status', '')
    if status_filter == 'paid':
        bills_qs = bills_qs.filter(paid_status=True)
    elif status_filter == 'unpaid':
        bills_qs = bills_qs.filter(paid_status=False)

    paginator = Paginator(bills_qs, 15)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'active_tab': 'billing'
    }
    return render(request, 'dashboard/billing.html', context)

@login_required
def prescriptions_view(request):
    prescriptions_qs = Prescription.objects.select_related(
        'appointment__patient',
        'appointment__doctor'
    ).all().order_by('-created_at')

    paginator = Paginator(prescriptions_qs, 15)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)

    context = {
        'page_obj': page_obj,
        'active_tab': 'prescriptions'
    }
    return render(request, 'dashboard/prescriptions.html', context)

@login_required
def revenue_view(request):
    # Issue 6 check in UI view as well:
    # If not challenge mode and user is not admin, forbidden!
    if not getattr(settings, 'MEDLEDGER_CHALLENGE_MODE', True):
        if request.user.role != 'admin' and not request.user.is_superuser:
            return HttpResponseForbidden("Forbidden: Only Administrators may access hospital revenue records.")

    stats = Bill.objects.aggregate(
        total_billed=Sum('total_amount'),
        total_collected=Sum('total_amount', filter=Q(paid_status=True)),
        total_outstanding=Sum('total_amount', filter=Q(paid_status=False)),
        total_invoices=Count('id'),
        paid_invoices=Count('id', filter=Q(paid_status=True)),
        unpaid_invoices=Count('id', filter=Q(paid_status=False)),
    )

    context = {
        'stats': stats,
        'active_tab': 'revenue'
    }
    return render(request, 'dashboard/revenue.html', context)
