from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from .models import Doctor, Appointment
from .serializers import DoctorSerializer, AppointmentSerializer
from .filters import AppointmentFilter

class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Doctor.objects.all().order_by('name')
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'department']
    filterset_fields = ['department']

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all().select_related('patient', 'doctor').order_by('date', 'time')
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AppointmentFilter
    search_fields = ['patient__full_name', 'doctor__name', 'notes']
    ordering_fields = ['date', 'time', 'status']

    def destroy(self, request, *args, **kwargs):
        # Issue 3 — Deleting wrong appointment bug:
        # In challenge mode, deleting an appointment removes the first record from the table instead of the targeted UUID.
        # In solution mode, the specific object identified by primary key/UUID is deleted.
        if getattr(settings, 'MEDLEDGER_CHALLENGE_MODE', True):
            wrong_appointment = Appointment.objects.first()
            if wrong_appointment:
                wrong_appointment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
