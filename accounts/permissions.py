from rest_framework import permissions

class IsAdminRole(permissions.BasePermission):
    """
    Custom permission to only allow administrators access.
    """
    message = "Administrator privileges required to access this resource."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == 'admin' or request.user.is_superuser or request.user.is_staff)
        )

class IsDoctorRole(permissions.BasePermission):
    """
    Custom permission to only allow doctors access.
    """
    message = "Doctor privileges required to access this resource."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'doctor'
        )

class IsReceptionistRole(permissions.BasePermission):
    """
    Custom permission to only allow receptionists access.
    """
    message = "Receptionist privileges required to access this resource."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'receptionist'
        )

class IsDoctorOrAdminRole(permissions.BasePermission):
    """
    Allows doctors or administrators access.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role in ('admin', 'doctor') or request.user.is_superuser)
        )
