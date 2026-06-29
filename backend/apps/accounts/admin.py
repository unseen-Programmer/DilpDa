from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    CustomerProfile,
    DeliveryPartnerProfile,
    RestaurantOwnerProfile,
    User,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    ordering = ("email",)
    list_display = (
        "email",
        "role",
        "phone_number",
        "is_active",
        "is_staff",
        "date_joined",
    )
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("email", "first_name", "last_name", "phone_number")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "phone_number")},
        ),
        ("Role", {"fields": ("role", "is_email_verified")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "role",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                ),
            },
        ),
    )


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "date_of_birth", "gender", "default_credit_limit")
    search_fields = ("user__email", "user__first_name", "user__last_name")


@admin.register(RestaurantOwnerProfile)
class RestaurantOwnerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "business_name", "gst_number", "is_verified_owner")
    list_filter = ("is_verified_owner",)
    search_fields = ("user__email", "business_name", "gst_number")


@admin.register(DeliveryPartnerProfile)
class DeliveryPartnerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "vehicle_type",
        "vehicle_number",
        "is_available",
        "is_verified_partner",
    )
    list_filter = ("is_available", "is_verified_partner")
    search_fields = ("user__email", "vehicle_number")
