from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.accounts.models import User


class IsAdminUserRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.ADMIN
        )


class IsRestaurantOwnerRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.RESTAURANT_OWNER
        )


class IsRestaurantOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.ADMIN:
            return True
        if request.method in SAFE_METHODS or request.user.role == User.Role.RESTAURANT_OWNER:
            return obj.owner.user_id == request.user.id
        return False
