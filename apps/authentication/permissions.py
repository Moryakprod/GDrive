from rest_framework import permissions
from rest_framework.exceptions import ValidationError


class IsAdminOrOwnUserObjectAccess(permissions.BasePermission):
    """Check that user can update only himself."""

    def has_object_permission(self, request, view, obj):
        """
        Access to the object has an admin or the user who created this object.
        """
        if view.action == 'retrieve' and (request.user == obj or obj.is_superuser):
            return True
        if request.user == obj:
            return True
        return False


class IsAuthenticated(permissions.IsAuthenticated):
    """
    Add additional layer to check a confirmed email.
    """

    def has_permission(self, request, view, *args, **kwargs):
        if not request.user.is_confirmed_email:
            raise ValidationError({'non_field_errors': [_('Provided email is not confirmed')]})
        return super().has_permission(request, view, *args, **kwargs)
