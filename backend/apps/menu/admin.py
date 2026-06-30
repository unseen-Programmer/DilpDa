from django.contrib import admin

from .models import FoodCategory, MenuItem


@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "restaurant",
        "display_order",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "restaurant__city", "restaurant")
    search_fields = ("name", "restaurant__name", "restaurant__owner__user__email")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("restaurant", "restaurant__owner", "restaurant__owner__user")


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "restaurant",
        "category",
        "price",
        "discount_price",
        "food_type",
        "is_available",
        "stock_status",
        "stock_quantity",
        "is_featured",
        "display_order",
    )
    list_filter = (
        "food_type",
        "is_available",
        "stock_status",
        "is_featured",
        "restaurant__city",
        "restaurant",
        "category",
    )
    search_fields = (
        "name",
        "restaurant__name",
        "category__name",
        "restaurant__owner__user__email",
    )
    readonly_fields = ("created_at", "updated_at")
    list_select_related = (
        "restaurant",
        "restaurant__owner",
        "restaurant__owner__user",
        "category",
    )
