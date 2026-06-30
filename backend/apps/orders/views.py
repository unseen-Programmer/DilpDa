from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import User

from .models import Cart, Order
from .permissions import IsCustomer, IsCustomerRestaurantOwnerOrAdmin
from .serializers import (
    AddToCartSerializer,
    CancelOrderSerializer,
    CartSerializer,
    OrderSerializer,
    PlaceOrderSerializer,
    RemoveCartItemSerializer,
    UpdateOrderStatusSerializer,
    UpdateCartItemQuantitySerializer,
)


class CartViewSet(viewsets.ViewSet):
    permission_classes = (IsCustomer,)

    def get_cart(self):
        customer_profile = self.request.user.customer_profile
        cart, _ = Cart.objects.prefetch_related(
            "items",
            "items__menu_item",
        ).get_or_create(
            customer=customer_profile,
            is_active=True,
        )
        return cart

    def serialize_cart(self, cart, status_code=status.HTTP_200_OK):
        cart = Cart.objects.select_related("restaurant").prefetch_related(
            "items",
            "items__menu_item",
        ).get(id=cart.id)
        return Response(CartSerializer(cart).data, status=status_code)

    @action(detail=False, methods=("get",), url_path="current")
    def current(self, request):
        return self.serialize_cart(self.get_cart())

    @action(detail=False, methods=("post",), url_path="add")
    def add(self, request):
        cart = self.get_cart()
        serializer = AddToCartSerializer(
            data=request.data,
            context={"cart": cart, "request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.serialize_cart(cart, status.HTTP_201_CREATED)

    @action(detail=False, methods=("patch",), url_path="update-quantity")
    def update_quantity(self, request):
        cart = self.get_cart()
        serializer = UpdateCartItemQuantitySerializer(
            data=request.data,
            context={"cart": cart, "request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.serialize_cart(cart)

    @action(detail=False, methods=("delete",), url_path="remove-item")
    def remove_item(self, request):
        cart = self.get_cart()
        serializer = RemoveCartItemSerializer(
            data=request.data,
            context={"cart": cart, "request": request},
        )
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            cart.items.filter(id=serializer.validated_data["item_id"]).delete()
            cart.refresh_restaurant()

        return self.serialize_cart(cart)

    @action(detail=False, methods=("post", "delete"), url_path="clear")
    def clear(self, request):
        cart = self.get_cart()

        with transaction.atomic():
            cart.items.all().delete()
            cart.restaurant = None
            cart.save(update_fields=("restaurant", "updated_at"))

        return self.serialize_cart(cart)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = (IsCustomerRestaurantOwnerOrAdmin,)

    def get_queryset(self):
        queryset = Order.objects.select_related(
            "customer",
            "customer__user",
            "restaurant",
            "restaurant__owner",
            "restaurant__owner__user",
        ).prefetch_related("items", "items__menu_item")
        user = self.request.user

        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.RESTAURANT_OWNER:
            return queryset.filter(restaurant__owner__user=user)
        return queryset.filter(customer__user=user)

    def get_customer_cart(self):
        return Cart.objects.select_related("customer", "restaurant").prefetch_related(
            "items",
            "items__menu_item",
            "items__menu_item__restaurant",
        ).get_or_create(
            customer=self.request.user.customer_profile,
            is_active=True,
        )[0]

    @action(
        detail=False,
        methods=("post",),
        permission_classes=(IsCustomer,),
        url_path="place",
    )
    def place(self, request):
        cart = self.get_customer_cart()
        serializer = PlaceOrderSerializer(
            data=request.data,
            context={"cart": cart, "request": request},
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=("get",),
        permission_classes=(IsCustomer,),
        url_path="history",
    )
    def history(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=("get",),
        url_path="restaurant-orders",
    )
    def restaurant_orders(self, request):
        if request.user.role not in (User.Role.RESTAURANT_OWNER, User.Role.ADMIN):
            return Response(
                {"detail": "Only restaurant owners or administrators can view restaurant orders."},
                status=status.HTTP_403_FORBIDDEN,
            )
        queryset = self.filter_queryset(self.get_queryset())
        restaurant_id = request.query_params.get("restaurant")
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=("post",), url_path="cancel")
    def cancel(self, request, pk=None):
        order = self.get_object()
        serializer = CancelOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.user.role == User.Role.RESTAURANT_OWNER:
            return Response(
                {"detail": "Restaurant owners cannot cancel customer orders."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if order.order_status in (
            Order.OrderStatus.OUT_FOR_DELIVERY,
            Order.OrderStatus.DELIVERED,
            Order.OrderStatus.CANCELLED,
        ):
            return Response(
                {"detail": "This order cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.order_status = Order.OrderStatus.CANCELLED
        if serializer.validated_data.get("reason"):
            order.notes = (
                f"{order.notes}\nCancellation reason: {serializer.validated_data['reason']}"
            ).strip()
        order.save(update_fields=("order_status", "notes", "updated_at"))
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=("patch",), url_path="update-status")
    def update_status(self, request, pk=None):
        if request.user.role not in (User.Role.RESTAURANT_OWNER, User.Role.ADMIN):
            return Response(
                {"detail": "Only restaurant owners or administrators can update order status."},
                status=status.HTTP_403_FORBIDDEN,
            )

        order = self.get_object()
        serializer = UpdateOrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order.order_status = serializer.validated_data["order_status"]
        order.save(update_fields=("order_status", "updated_at"))
        return Response(self.get_serializer(order).data)
