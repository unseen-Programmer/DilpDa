from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.menu.models import MenuItem
from apps.restaurants.models import Restaurant

from .models import Cart, CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source="menu_item.name", read_only=True)
    restaurant = serializers.IntegerField(source="menu_item.restaurant_id", read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    effective_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = (
            "id",
            "menu_item",
            "menu_item_name",
            "restaurant",
            "quantity",
            "unit_price",
            "effective_price",
            "discount_amount",
            "subtotal",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "menu_item",
            "menu_item_name",
            "restaurant",
            "quantity",
            "unit_price",
            "effective_price",
            "discount_amount",
            "subtotal",
            "created_at",
            "updated_at",
        )


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_payable = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = (
            "id",
            "restaurant",
            "restaurant_name",
            "items",
            "subtotal",
            "discount_amount",
            "total_payable",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class AddToCartSerializer(serializers.Serializer):
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_menu_item(self, menu_item):
        if menu_item.restaurant.status != Restaurant.Status.APPROVED:
            raise serializers.ValidationError(
                "Only items from approved restaurants can be added to cart."
            )
        if not menu_item.is_available:
            raise serializers.ValidationError("This menu item is currently unavailable.")
        if menu_item.stock_status != MenuItem.StockStatus.IN_STOCK:
            raise serializers.ValidationError("This menu item is out of stock.")
        return menu_item

    def validate(self, attrs):
        cart = self.context["cart"]
        menu_item = attrs["menu_item"]
        quantity = attrs["quantity"]

        if cart.restaurant_id and cart.restaurant_id != menu_item.restaurant_id:
            raise serializers.ValidationError(
                {"menu_item": "Cart can contain items from only one restaurant."}
            )

        existing_quantity = 0
        if cart.id:
            existing_quantity = (
                cart.items.filter(menu_item=menu_item)
                .values_list("quantity", flat=True)
                .first()
                or 0
            )
        if existing_quantity + quantity > menu_item.stock_quantity:
            raise serializers.ValidationError(
                {"quantity": "Requested quantity exceeds available stock."}
            )

        return attrs

    @transaction.atomic
    def save(self, **kwargs):
        cart = self.context["cart"]
        menu_item = self.validated_data["menu_item"]
        quantity = self.validated_data["quantity"]

        item, created = CartItem.objects.select_for_update().get_or_create(
            cart=cart,
            menu_item=menu_item,
            defaults={"quantity": quantity},
        )
        if not created:
            item.quantity += quantity
            item.save(update_fields=("quantity", "updated_at"))

        if cart.restaurant_id is None:
            cart.restaurant = menu_item.restaurant
            cart.save(update_fields=("restaurant", "updated_at"))

        return item


class UpdateCartItemQuantitySerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        cart = self.context["cart"]
        try:
            item = cart.items.select_related("menu_item").get(id=attrs["item_id"])
        except CartItem.DoesNotExist:
            raise serializers.ValidationError({"item_id": "Cart item not found."})

        if not item.menu_item.is_available:
            raise serializers.ValidationError("This menu item is currently unavailable.")
        if item.menu_item.stock_status != MenuItem.StockStatus.IN_STOCK:
            raise serializers.ValidationError("This menu item is out of stock.")
        if attrs["quantity"] > item.menu_item.stock_quantity:
            raise serializers.ValidationError(
                {"quantity": "Requested quantity exceeds available stock."}
            )

        attrs["item"] = item
        return attrs

    def save(self, **kwargs):
        item = self.validated_data["item"]
        item.quantity = self.validated_data["quantity"]
        item.save(update_fields=("quantity", "updated_at"))
        return item


class RemoveCartItemSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()

    def validate_item_id(self, item_id):
        cart = self.context["cart"]
        if not cart.items.filter(id=item_id).exists():
            raise serializers.ValidationError("Cart item not found.")
        return item_id


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "id",
            "menu_item",
            "menu_item_name",
            "quantity",
            "unit_price",
            "discount_price",
            "subtotal",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_email = serializers.EmailField(source="customer.user.email", read_only=True)
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "order_number",
            "customer",
            "customer_email",
            "restaurant",
            "restaurant_name",
            "delivery_address",
            "payment_method",
            "payment_status",
            "order_status",
            "subtotal",
            "discount",
            "delivery_charge",
            "grand_total",
            "notes",
            "estimated_delivery_time",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class PlaceOrderSerializer(serializers.Serializer):
    delivery_address = serializers.CharField()
    payment_method = serializers.ChoiceField(choices=Order.PaymentMethod.choices)
    delivery_charge = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.00"),
        default=Decimal("0.00"),
    )
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        cart = self.context["cart"]
        cart_items = list(
            cart.items.select_related("menu_item", "menu_item__restaurant").all()
        )

        if not cart_items:
            raise serializers.ValidationError("Cannot place an order with an empty cart.")
        if cart.restaurant_id is None:
            raise serializers.ValidationError("Cart restaurant is required.")
        if cart.restaurant.status != Restaurant.Status.APPROVED:
            raise serializers.ValidationError("Restaurant is not approved for orders.")

        for item in cart_items:
            menu_item = item.menu_item
            if not menu_item.is_available:
                raise serializers.ValidationError(
                    {menu_item.name: "This menu item is currently unavailable."}
                )
            if menu_item.stock_status != MenuItem.StockStatus.IN_STOCK:
                raise serializers.ValidationError({menu_item.name: "This item is out of stock."})
            if item.quantity > menu_item.stock_quantity:
                raise serializers.ValidationError(
                    {menu_item.name: "Requested quantity exceeds available stock."}
                )

        attrs["cart_items"] = cart_items
        return attrs

    @transaction.atomic
    def save(self, **kwargs):
        cart = self.context["cart"]
        cart_items = self.validated_data["cart_items"]
        menu_item_ids = [item.menu_item_id for item in cart_items]
        locked_menu_items = {
            item.id: item
            for item in MenuItem.objects.select_for_update().filter(id__in=menu_item_ids)
        }

        for cart_item in cart_items:
            menu_item = locked_menu_items[cart_item.menu_item_id]
            if cart_item.quantity > menu_item.stock_quantity:
                raise serializers.ValidationError(
                    {menu_item.name: "Requested quantity exceeds available stock."}
                )

        subtotal = cart.subtotal
        discount = cart.discount_amount
        delivery_charge = self.validated_data["delivery_charge"]
        grand_total = cart.total_payable + delivery_charge
        order = Order.objects.create(
            customer=cart.customer,
            restaurant=cart.restaurant,
            delivery_address=self.validated_data["delivery_address"],
            payment_method=self.validated_data["payment_method"],
            subtotal=subtotal,
            discount=discount,
            delivery_charge=delivery_charge,
            grand_total=grand_total,
            notes=self.validated_data.get("notes", ""),
            estimated_delivery_time=timezone.now() + timedelta(minutes=45),
        )

        order_items = []
        for cart_item in cart_items:
            menu_item = locked_menu_items[cart_item.menu_item_id]
            effective_price = menu_item.discount_price or menu_item.price
            order_items.append(
                OrderItem(
                    order=order,
                    menu_item=menu_item,
                    menu_item_name=menu_item.name,
                    quantity=cart_item.quantity,
                    unit_price=menu_item.price,
                    discount_price=menu_item.discount_price,
                    subtotal=effective_price * cart_item.quantity,
                )
            )
            menu_item.stock_quantity -= cart_item.quantity
            update_fields = ["stock_quantity", "updated_at"]
            if menu_item.stock_quantity == 0:
                menu_item.stock_status = MenuItem.StockStatus.OUT_OF_STOCK
                update_fields.append("stock_status")
            menu_item.save(update_fields=update_fields)

        OrderItem.objects.bulk_create(order_items)
        cart.items.all().delete()
        cart.restaurant = None
        cart.save(update_fields=("restaurant", "updated_at"))

        return order


class UpdateOrderStatusSerializer(serializers.Serializer):
    order_status = serializers.ChoiceField(choices=Order.OrderStatus.choices)


class CancelOrderSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)
