from django.contrib import admin

from .models import MenuItemReview, RestaurantReview, ReviewLike


@admin.register(RestaurantReview)
class RestaurantReviewAdmin(admin.ModelAdmin):
    list_display = (
        "restaurant",
        "customer",
        "order",
        "rating",
        "is_visible",
        "is_edited",
        "created_at",
    )
    list_filter = (
        "rating",
        "restaurant",
        "customer",
        "is_visible",
        "created_at",
    )
    search_fields = (
        "restaurant__name",
        "customer__user__email",
        "order__order_number",
        "review_text",
    )
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("restaurant", "customer", "customer__user", "order")


@admin.register(MenuItemReview)
class MenuItemReviewAdmin(admin.ModelAdmin):
    list_display = (
        "menu_item",
        "restaurant_name",
        "customer",
        "order",
        "rating",
        "is_visible",
        "created_at",
    )
    list_filter = (
        "rating",
        "menu_item__restaurant",
        "customer",
        "is_visible",
        "created_at",
    )
    search_fields = (
        "menu_item__name",
        "menu_item__restaurant__name",
        "customer__user__email",
        "order__order_number",
        "review_text",
    )
    readonly_fields = ("created_at", "updated_at")
    list_select_related = (
        "menu_item",
        "menu_item__restaurant",
        "customer",
        "customer__user",
        "order",
    )

    def restaurant_name(self, obj):
        return obj.menu_item.restaurant.name


@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "restaurant_review",
        "menu_item_review",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = (
        "user__email",
        "restaurant_review__restaurant__name",
        "menu_item_review__menu_item__name",
    )
    list_select_related = ("user", "restaurant_review", "menu_item_review")
