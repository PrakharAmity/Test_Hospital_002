from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from .models import Prescription
from .serializers import PrescriptionSerializer
from .pdf import generate_prescription_pdf
from accounts.permissions import IsDoctorOrAdminRole

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all().select_related('appointment__patient', 'appointment__doctor').order_by('-created_at')
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'appointment__patient__full_name',
        'appointment__doctor__name',
        'dosage',
        'instructions'
    ]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsDoctorOrAdminRole()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['get'], url_path='pdf')
    def download_pdf(self, request, pk=None):
        """
        Download the prescription formatted as a printable medical PDF.
        """
        prescription = self.get_object()
        pdf_content = generate_prescription_pdf(prescription)

        response = HttpResponse(pdf_content, content_type='application/pdf')
        filename = f"prescription_{str(prescription.id)[:8]}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
