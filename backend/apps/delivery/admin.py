from django.contrib import admin

from .models import DeliveryAssignment, DeliveryEarnings, DeliveryTracking


class DeliveryTrackingInline(admin.TabularInline):
    model = DeliveryTracking
    extra = 0
    readonly_fields = ("timestamp",)


@admin.register(DeliveryAssignment)
class DeliveryAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "restaurant_name",
        "customer_email",
        "delivery_partner",
        "status",
        "assigned_by",
        "assigned_at",
        "delivered_at",
    )
    list_filter = (
        "status",
        "delivery_partner",
        "assigned_at",
        "order__restaurant",
        "order__customer",
    )
    search_fields = (
        "order__order_number",
        "order__customer__user__email",
        "order__restaurant__name",
        "delivery_partner__user__email",
    )
    readonly_fields = ("created_at", "updated_at")
    list_select_related = (
        "order",
        "order__customer",
        "order__customer__user",
        "order__restaurant",
        "delivery_partner",
        "delivery_partner__user",
        "assigned_by",
    )
    inlines = (DeliveryTrackingInline,)

    def restaurant_name(self, obj):
        return obj.order.restaurant.name

    def customer_email(self, obj):
        return obj.order.customer.user.email


@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    list_display = (
        "delivery_assignment",
        "current_location",
        "latitude",
        "longitude",
        "status",
        "timestamp",
    )
    list_filter = (
        "status",
        "timestamp",
        "delivery_assignment__delivery_partner",
        "delivery_assignment__order__restaurant",
        "delivery_assignment__order__customer",
    )
    search_fields = (
        "current_location",
        "delivery_assignment__order__order_number",
        "delivery_assignment__delivery_partner__user__email",
    )
    list_select_related = (
        "delivery_assignment",
        "delivery_assignment__order",
        "delivery_assignment__delivery_partner",
    )


@admin.register(DeliveryEarnings)
class DeliveryEarningsAdmin(admin.ModelAdmin):
    list_display = (
        "delivery_partner",
        "order",
        "restaurant_name",
        "delivery_fee",
        "incentive",
        "total_earnings",
        "payment_status",
        "created_at",
    )
    list_filter = (
        "payment_status",
        "delivery_partner",
        "created_at",
        "order__restaurant",
        "order__customer",
    )
    search_fields = (
        "order__order_number",
        "delivery_partner__user__email",
        "order__restaurant__name",
    )
    list_select_related = (
        "delivery_partner",
        "delivery_partner__user",
        "order",
        "order__restaurant",
    )

    def restaurant_name(self, obj):
        return obj.order.restaurant.name
