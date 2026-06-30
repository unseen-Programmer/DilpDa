from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import User

from .models import Restaurant
from .permissions import IsAdminUserRole, IsRestaurantOwnerOrAdmin
from .serializers import RestaurantSerializer, RestaurantStatusSerializer


class RestaurantViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return (AllowAny(),)
        if self.action in ("approve", "reject"):
            return (IsAdminUserRole(),)
        return (IsAuthenticated(), IsRestaurantOwnerOrAdmin())

    def get_queryset(self):
        queryset = Restaurant.objects.select_related("owner", "owner__user")
        user = self.request.user

        if user.is_authenticated and user.role == User.Role.ADMIN:
            return queryset
        if user.is_authenticated and user.role == User.Role.RESTAURANT_OWNER:
            return queryset.filter(owner__user=user)
        return queryset.filter(status=Restaurant.Status.APPROVED)

    def perform_create(self, serializer):
        owner_profile = getattr(self.request.user, "restaurant_owner_profile", None)
        if owner_profile is None:
            raise ValidationError({"detail": "Restaurant owner profile is required."})
        serializer.save(owner=owner_profile)

    def create(self, request, *args, **kwargs):
        if request.user.role != User.Role.RESTAURANT_OWNER:
            return Response(
                {"detail": "Only restaurant owners can create restaurants."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not hasattr(request.user, "restaurant_owner_profile"):
            return Response(
                {"detail": "Restaurant owner profile is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)

    @action(
        detail=False,
        methods=("get",),
        url_path="my-restaurants",
        permission_classes=(IsAuthenticated,),
    )
    def my_restaurants(self, request):
        if request.user.role != User.Role.RESTAURANT_OWNER:
            return Response(
                {"detail": "Only restaurant owners can view this resource."},
                status=status.HTTP_403_FORBIDDEN,
            )

        restaurants = self.get_queryset()
        serializer = self.get_serializer(restaurants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=("post",), permission_classes=(IsAdminUserRole,))
    def approve(self, request, pk=None):
        restaurant = self.get_object()
        restaurant.status = Restaurant.Status.APPROVED
        restaurant.save(update_fields=("status", "updated_at"))
        serializer = RestaurantStatusSerializer(restaurant)
        return Response(serializer.data)

    @action(detail=True, methods=("post",), permission_classes=(IsAdminUserRole,))
    def reject(self, request, pk=None):
        restaurant = self.get_object()
        restaurant.status = Restaurant.Status.REJECTED
        restaurant.save(update_fields=("status", "updated_at"))
        serializer = RestaurantStatusSerializer(restaurant)
        return Response(serializer.data)
