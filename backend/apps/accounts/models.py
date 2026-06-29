from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        RESTAURANT_OWNER = "RESTAURANT_OWNER", "Restaurant Owner"
        DELIVERY_PARTNER = "DELIVERY_PARTNER", "Delivery Partner"
        ADMIN = "ADMIN", "Administrator"

    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.CUSTOMER,
        db_index=True,
    )
    phone_number = models.CharField(max_length=20, blank=True)
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=30, blank=True)
    default_credit_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    def __str__(self):
        return f"Customer profile: {self.user.email}"


class RestaurantOwnerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="restaurant_owner_profile",
    )
    business_name = models.CharField(max_length=255, blank=True)
    gst_number = models.CharField(max_length=32, blank=True)
    is_verified_owner = models.BooleanField(default=False)

    def __str__(self):
        return f"Restaurant owner profile: {self.user.email}"


class DeliveryPartnerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="delivery_partner_profile",
    )
    vehicle_type = models.CharField(max_length=50, blank=True)
    vehicle_number = models.CharField(max_length=30, blank=True)
    is_available = models.BooleanField(default=False)
    is_verified_partner = models.BooleanField(default=False)

    def __str__(self):
        return f"Delivery partner profile: {self.user.email}"
