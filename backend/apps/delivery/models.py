from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from apps.accounts.models import DeliveryPartnerProfile
from apps.orders.models import Order


class DeliveryAssignment(models.Model):
    class Status(models.TextChoices):
        ASSIGNED = "ASSIGNED", "Assigned"
        ACCEPTED = "ACCEPTED", "Accepted"
        PICKED_UP = "PICKED_UP", "Picked Up"
        OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY", "Out for Delivery"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="delivery_assignments",
    )
    delivery_partner = models.ForeignKey(
        DeliveryPartnerProfile,
        on_delete=models.PROTECT,
        related_name="delivery_assignments",
    )
    status = models.CharField(
        max_length=24,
        choices=Status.choices,
        default=Status.ASSIGNED,
        db_index=True,
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="delivery_assignments_made",
        null=True,
        blank=True,
    )
    assigned_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    delivery_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("order",),
                condition=~Q(status__in=("DELIVERED", "CANCELLED")),
                name="unique_active_delivery_assignment_per_order",
            ),
        ]
        indexes = [
            models.Index(fields=("delivery_partner", "status")),
            models.Index(fields=("order", "status")),
            models.Index(fields=("assigned_at",)),
        ]

    def __str__(self):
        return f"{self.order.order_number} - {self.delivery_partner.user.email}"


class DeliveryTracking(models.Model):
    delivery_assignment = models.ForeignKey(
        DeliveryAssignment,
        on_delete=models.CASCADE,
        related_name="tracking_updates",
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(Decimal("-90.000000")),
            MaxValueValidator(Decimal("90.000000")),
        ],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(Decimal("-180.000000")),
            MaxValueValidator(Decimal("180.000000")),
        ],
    )
    current_location = models.CharField(max_length=255)
    status = models.CharField(max_length=24, choices=DeliveryAssignment.Status.choices)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-timestamp",)
        indexes = [
            models.Index(fields=("delivery_assignment", "timestamp")),
            models.Index(fields=("status", "timestamp")),
        ]

    def __str__(self):
        return f"{self.delivery_assignment_id} - {self.current_location}"


class DeliveryEarnings(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"

    delivery_partner = models.ForeignKey(
        DeliveryPartnerProfile,
        on_delete=models.PROTECT,
        related_name="earnings",
    )
    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name="delivery_earnings",
    )
    delivery_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    incentive = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("delivery_partner", "payment_status")),
            models.Index(fields=("created_at",)),
        ]
        verbose_name_plural = "delivery earnings"

    def __str__(self):
        return f"{self.delivery_partner.user.email} - {self.order.order_number}"
