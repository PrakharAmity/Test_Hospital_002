from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BillViewSet, RevenueAnalyticsView

router = DefaultRouter()
router.register(r'bills', BillViewSet, basename='bill')

urlpatterns = [
    path('billing/revenue/', RevenueAnalyticsView.as_view(), name='revenue_analytics'),
    path('', include(router.urls)),
]
