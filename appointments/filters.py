import django_filters
from django.conf import settings
from .models import Appointment

class AppointmentFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    
    # Issue 1 — Boundary date exclusion bug:
    # In challenge mode, 'lt' lookup is used, which excludes appointments occurring exactly on end_date.
    # In solution mode, 'lte' lookup is used, including the boundary date.
    if getattr(settings, 'MEDLEDGER_CHALLENGE_MODE', True):
        end_date = django_filters.DateFilter(field_name='date', lookup_expr='lt')
    else:
        end_date = django_filters.DateFilter(field_name='date', lookup_expr='lte')

    doctor = django_filters.UUIDFilter(field_name='doctor__id')
    department = django_filters.CharFilter(field_name='doctor__department', lookup_expr='iexact')
    status = django_filters.CharFilter(field_name='status', lookup_expr='iexact')

    class Meta:
        model = Appointment
        fields = ['doctor', 'department', 'status', 'start_date', 'end_date']
