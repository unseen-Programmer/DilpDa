from decimal import Decimal
from uuid import uuid4

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.accounts.models import CustomerProfile
from apps.menu.models import MenuItem
from apps.restaurants.models import Restaurant


class Cart(models.Model):
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="carts",
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        related_name="carts",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("customer",),
                condition=models.Q(is_active=True),
                name="unique_active_cart_per_customer",
            ),
        ]
        indexes = [
            models.Index(fields=("customer", "is_active")),
            models.Index(fields=("restaurant", "is_active")),
        ]

    def __str__(self):
        return f"Cart #{self.id} - {self.customer.user.email}"

    @property
    def subtotal(self):
        return sum((item.original_subtotal for item in self.items.all()), Decimal("0.00"))

    @property
    def discount_amount(self):
        return sum((item.discount_amount for item in self.items.all()), Decimal("0.00"))

    @property
    def total_payable(self):
        return self.subtotal - self.discount_amount

    def refresh_restaurant(self):
        first_item = self.items.select_related("menu_item__restaurant").first()
        restaurant = first_item.menu_item.restaurant if first_item else None
        if self.restaurant_id != getattr(restaurant, "id", None):
            self.restaurant = restaurant
            self.save(update_fields=("restaurant", "updated_at"))


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("cart", "menu_item"),
                name="unique_menu_item_per_cart",
            ),
        ]
        indexes = [
            models.Index(fields=("cart", "menu_item")),
        ]

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"

    @property
    def unit_price(self):
        return self.menu_item.price

    @property
    def effective_price(self):
        return self.menu_item.discount_price or self.menu_item.price

    @property
    def original_subtotal(self):
        return self.unit_price * self.quantity

    @property
    def discount_amount(self):
        return (self.unit_price - self.effective_price) * self.quantity

    @property
    def subtotal(self):
        return self.effective_price * self.quantity


class Order(models.Model):
    class PaymentMethod(models.TextChoices):
        COD = "COD", "Cash on Delivery"
        ONLINE = "ONLINE", "Online"
        WALLET = "WALLET", "Wallet"

    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    class OrderStatus(models.TextChoices):
        PLACED = "PLACED", "Placed"
        CONFIRMED = "CONFIRMED", "Confirmed"
        PREPARING = "PREPARING", "Preparing"
        OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY", "Out for Delivery"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    order_number = models.CharField(max_length=32, unique=True, editable=False)
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    delivery_address = models.TextField()
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
    )
    order_status = models.CharField(
        max_length=24,
        choices=OrderStatus.choices,
        default=OrderStatus.PLACED,
        db_index=True,
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("customer", "order_status")),
            models.Index(fields=("restaurant", "order_status")),
            models.Index(fields=("order_number",)),
        ]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
            self.order_number = f"ORD{timestamp}{uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.SET_NULL,
        related_name="order_items",
        null=True,
        blank=True,
    )
    menu_item_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("created_at",)
        indexes = [
            models.Index(fields=("order", "menu_item")),
        ]

    def __str__(self):
        return f"{self.menu_item_name} x {self.quantity}"
