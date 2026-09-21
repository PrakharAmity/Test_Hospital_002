from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('patients.urls')),
    path('api/', include('appointments.urls')),
    path('api/', include('billing.urls')),
    path('api/', include('prescriptions.urls')),
    path('', include('dashboard.urls')),
]
