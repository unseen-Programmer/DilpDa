from rest_framework.permissions import BasePermission

from apps.accounts.models import User


class IsDeliveryActor(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role
            in (
                User.Role.CUSTOMER,
                User.Role.RESTAURANT_OWNER,
                User.Role.DELIVERY_PARTNER,
                User.Role.ADMIN,
            )
        )


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.ADMIN
        )


class IsDeliveryPartnerRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.DELIVERY_PARTNER
        )
