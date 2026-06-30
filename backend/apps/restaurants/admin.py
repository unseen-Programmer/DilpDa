from django.contrib import admin

from .models import Restaurant


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "city",
        "cuisine_type",
        "status",
        "rating",
        "total_reviews",
        "created_at",
    )
    list_filter = ("status", "city", "state", "cuisine_type")
    search_fields = (
        "name",
        "owner__user__email",
        "city",
        "gst_number",
        "fssai_number",
    )
    readonly_fields = ("rating", "total_reviews", "created_at", "updated_at")
    list_select_related = ("owner", "owner__user")
    actions = ("approve_restaurants", "reject_restaurants", "suspend_restaurants")

    @admin.action(description="Approve selected restaurants")
    def approve_restaurants(self, request, queryset):
        queryset.update(status=Restaurant.Status.APPROVED)

    @admin.action(description="Reject selected restaurants")
    def reject_restaurants(self, request, queryset):
        queryset.update(status=Restaurant.Status.REJECTED)

    @admin.action(description="Suspend selected restaurants")
    def suspend_restaurants(self, request, queryset):
        queryset.update(status=Restaurant.Status.SUSPENDED)
