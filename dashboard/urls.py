from django.urls import path
from .views import (
    login_view, logout_view, overview_view,
    patients_view, appointments_view, billing_view,
    prescriptions_view, revenue_view
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', overview_view, name='dashboard_overview'),
    path('patients/', patients_view, name='dashboard_patients'),
    path('appointments/', appointments_view, name='dashboard_appointments'),
    path('billing/', billing_view, name='dashboard_billing'),
    path('prescriptions/', prescriptions_view, name='dashboard_prescriptions'),
    path('revenue/', revenue_view, name='dashboard_revenue'),
]
