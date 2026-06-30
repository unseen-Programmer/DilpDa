from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("menu_item",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "restaurant",
        "is_active",
        "subtotal",
        "discount_amount",
        "total_payable",
        "updated_at",
    )
    list_filter = ("is_active", "restaurant")
    search_fields = ("customer__user__email", "restaurant__name")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("customer", "customer__user", "restaurant")
    inlines = (CartItemInline,)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cart",
        "menu_item",
        "quantity",
        "unit_price",
        "effective_price",
        "subtotal",
        "updated_at",
    )
    search_fields = (
        "cart__customer__user__email",
        "menu_item__name",
        "menu_item__restaurant__name",
    )
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("cart", "cart__customer", "cart__customer__user", "menu_item")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "menu_item_name",
        "quantity",
        "unit_price",
        "discount_price",
        "subtotal",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("menu_item",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer",
        "restaurant",
        "payment_method",
        "payment_status",
        "order_status",
        "grand_total",
        "estimated_delivery_time",
        "created_at",
    )
    list_filter = (
        "payment_method",
        "payment_status",
        "order_status",
        "restaurant",
        "created_at",
    )
    search_fields = (
        "order_number",
        "customer__user__email",
        "restaurant__name",
    )
    readonly_fields = ("order_number", "created_at", "updated_at")
    list_select_related = ("customer", "customer__user", "restaurant")
    inlines = (OrderItemInline,)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "menu_item_name",
        "quantity",
        "unit_price",
        "discount_price",
        "subtotal",
    )
    search_fields = ("order__order_number", "menu_item_name", "menu_item__name")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("order", "menu_item")
