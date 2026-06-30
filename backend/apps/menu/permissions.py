from rest_framework.permissions import BasePermission

from apps.accounts.models import User


class IsRestaurantOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in (User.Role.RESTAURANT_OWNER, User.Role.ADMIN)
        )

    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.ADMIN:
            return True

        restaurant = getattr(obj, "restaurant", None)
        return bool(restaurant and restaurant.owner.user_id == request.user.id)
