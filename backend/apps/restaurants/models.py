from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.accounts.models import RestaurantOwnerProfile


class Restaurant(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        SUSPENDED = "SUSPENDED", "Suspended"

    owner = models.ForeignKey(
        RestaurantOwnerProfile,
        on_delete=models.CASCADE,
        related_name="restaurants",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="restaurants/logos/", blank=True, null=True)
    cover_image = models.ImageField(
        upload_to="restaurants/covers/",
        blank=True,
        null=True,
    )
    address = models.TextField()
    city = models.CharField(max_length=120, db_index=True)
    state = models.CharField(max_length=120, db_index=True)
    pincode = models.CharField(max_length=12, db_index=True)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("-90.000000")),
            MaxValueValidator(Decimal("90.000000")),
        ],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("-180.000000")),
            MaxValueValidator(Decimal("180.000000")),
        ],
    )
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    cuisine_type = models.CharField(max_length=120, db_index=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    gst_number = models.CharField(max_length=32)
    fssai_number = models.CharField(max_length=32, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("5.00")),
        ],
    )
    total_reviews = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("status", "city")),
            models.Index(fields=("status", "cuisine_type")),
        ]

    def __str__(self):
        return self.name
