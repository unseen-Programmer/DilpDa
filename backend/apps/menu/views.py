from decimal import Decimal, InvalidOperation

from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.accounts.models import User
from apps.restaurants.models import Restaurant

from .models import FoodCategory, MenuItem
from .pagination import MenuPagination
from .permissions import IsRestaurantOwnerOrAdmin
from .serializers import FoodCategorySerializer, MenuItemSerializer


def parse_bool(value):
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in ("true", "1", "yes"):
        return True
    if normalized in ("false", "0", "no"):
        return False
    return None


class FoodCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = FoodCategorySerializer
    pagination_class = MenuPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ("name", "description", "restaurant__name")
    ordering_fields = ("display_order", "name", "created_at", "updated_at")
    ordering = ("display_order", "name")

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return (AllowAny(),)
        return (IsRestaurantOwnerOrAdmin(),)

    def get_queryset(self):
        queryset = FoodCategory.objects.select_related("restaurant", "restaurant__owner")
        user = self.request.user

        if user.is_authenticated and user.role == User.Role.ADMIN:
            pass
        elif user.is_authenticated and user.role == User.Role.RESTAURANT_OWNER:
            queryset = queryset.filter(restaurant__owner__user=user)
        else:
            queryset = queryset.filter(
                restaurant__status=Restaurant.Status.APPROVED,
                is_active=True,
            )

        restaurant_id = self.request.query_params.get("restaurant")
        is_active = parse_bool(self.request.query_params.get("is_active"))

        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        return queryset

    def create(self, request, *args, **kwargs):
        if request.user.role not in (User.Role.RESTAURANT_OWNER, User.Role.ADMIN):
            return Response(
                {"detail": "Only restaurant owners can create categories."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)


class MenuItemViewSet(viewsets.ModelViewSet):
    serializer_class = MenuItemSerializer
    pagination_class = MenuPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ("name", "description", "restaurant__name", "category__name")
    ordering_fields = (
        "display_order",
        "name",
        "price",
        "discount_price",
        "preparation_time",
        "created_at",
        "updated_at",
    )
    ordering = ("display_order", "name")

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return (AllowAny(),)
        return (IsRestaurantOwnerOrAdmin(),)

    def get_queryset(self):
        queryset = MenuItem.objects.select_related(
            "restaurant",
            "restaurant__owner",
            "category",
        )
        user = self.request.user

        if user.is_authenticated and user.role == User.Role.ADMIN:
            pass
        elif user.is_authenticated and user.role == User.Role.RESTAURANT_OWNER:
            queryset = queryset.filter(restaurant__owner__user=user)
        else:
            queryset = queryset.filter(restaurant__status=Restaurant.Status.APPROVED)

        params = self.request.query_params
        restaurant_id = params.get("restaurant")
        category_id = params.get("category")
        food_type = params.get("food_type")
        stock_status = params.get("stock_status")
        is_available = parse_bool(params.get("is_available"))
        is_featured = parse_bool(params.get("is_featured"))
        min_price = params.get("min_price")
        max_price = params.get("max_price")

        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if food_type:
            queryset = queryset.filter(food_type=food_type)
        if stock_status:
            queryset = queryset.filter(stock_status=stock_status)
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available)
        if is_featured is not None:
            queryset = queryset.filter(is_featured=is_featured)
        if min_price:
            try:
                queryset = queryset.filter(price__gte=Decimal(min_price))
            except InvalidOperation:
                pass
        if max_price:
            try:
                queryset = queryset.filter(price__lte=Decimal(max_price))
            except InvalidOperation:
                pass

        return queryset

    def create(self, request, *args, **kwargs):
        if request.user.role not in (User.Role.RESTAURANT_OWNER, User.Role.ADMIN):
            return Response(
                {"detail": "Only restaurant owners can create menu items."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)
