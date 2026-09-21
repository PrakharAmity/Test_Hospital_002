from rest_framework import viewsets, views, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from django.conf import settings
from decimal import Decimal
from .models import Bill
from .serializers import BillSerializer
from accounts.permissions import IsAdminRole

class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all().select_related('patient', 'appointment').order_by('-generated_date')
    serializer_class = BillSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['paid_status', 'patient']
    search_fields = ['patient__full_name', 'id']
    ordering_fields = ['generated_date', 'total_amount', 'amount']

class RevenueAnalyticsView(views.APIView):
    """
    Hospital Revenue and Financial Analytics Endpoint.
    Restricted strictly to Administrator users.
    """
    # Issue 6 — Unauthorized Receptionist Can Access Admin Revenue Reports:
    # In challenge mode, permission_classes only checks IsAuthenticated (allowing receptionists).
    # In solution mode, permission_classes includes IsAdminRole (returns HTTP 403 Forbidden for receptionists/doctors).
    if getattr(settings, 'MEDLEDGER_CHALLENGE_MODE', True):
        permission_classes = [IsAuthenticated]
    else:
        permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        stats = Bill.objects.aggregate(
            total_billed=Sum('total_amount'),
            total_collected=Sum('total_amount', filter=Q(paid_status=True)),
            total_outstanding=Sum('total_amount', filter=Q(paid_status=False)),
            total_invoices=Count('id'),
            paid_invoices=Count('id', filter=Q(paid_status=True)),
            unpaid_invoices=Count('id', filter=Q(paid_status=False)),
        )

        return Response({
            "total_revenue": stats['total_billed'] or Decimal('0.00'),
            "collected_revenue": stats['total_collected'] or Decimal('0.00'),
            "outstanding_revenue": stats['total_outstanding'] or Decimal('0.00'),
            "total_invoices": stats['total_invoices'] or 0,
            "paid_invoices": stats['paid_invoices'] or 0,
            "unpaid_invoices": stats['unpaid_invoices'] or 0,
        }, status=status.HTTP_200_OK)
