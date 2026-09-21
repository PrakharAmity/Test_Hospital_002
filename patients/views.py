from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Patient
from .serializers import PatientSerializer
from .pagination import CustomPatientPagination

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by('-registered_date', '-created_at')
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPatientPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'phone', 'email', 'blood_group']
    filterset_fields = {
        'blood_group': ['exact'],
        'gender': ['exact'],
        'registered_date': ['exact', 'gte', 'lte'],
    }
    ordering_fields = ['full_name', 'registered_date', 'date_of_birth']
    ordering = ['-registered_date', '-created_at']

    def list(self, request, *args, **kwargs):
        # Support simulated error trigger for testing search recovery
        if request.query_params.get('simulate_error') == 'true':
            return Response(
                {"error": "Simulated hospital server timeout while querying patient records."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return super().list(request, *args, **kwargs)
