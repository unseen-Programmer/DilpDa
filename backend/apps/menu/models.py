from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Lower

from apps.restaurants.models import Restaurant


class FoodCategory(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="food_categories",
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("display_order", "name")
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                "restaurant",
                name="unique_food_category_name_per_restaurant",
            ),
        ]
        indexes = [
            models.Index(fields=("restaurant", "display_order")),
            models.Index(fields=("restaurant", "is_active")),
        ]
        verbose_name_plural = "food categories"

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"


class MenuItem(models.Model):
    class FoodType(models.TextChoices):
        VEG = "VEG", "Veg"
        NON_VEG = "NON_VEG", "Non-Veg"
        VEGAN = "VEGAN", "Vegan"

    class StockStatus(models.TextChoices):
        IN_STOCK = "IN_STOCK", "In Stock"
        OUT_OF_STOCK = "OUT_OF_STOCK", "Out of Stock"

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="menu_items",
    )
    category = models.ForeignKey(
        FoodCategory,
        on_delete=models.PROTECT,
        related_name="menu_items",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="menu/items/", blank=True, null=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    food_type = models.CharField(
        max_length=20,
        choices=FoodType.choices,
        default=FoodType.VEG,
        db_index=True,
    )
    preparation_time = models.PositiveIntegerField(
        help_text="Preparation time in minutes.",
    )
    is_available = models.BooleanField(default=True, db_index=True)
    stock_status = models.CharField(
        max_length=20,
        choices=StockStatus.choices,
        default=StockStatus.IN_STOCK,
        db_index=True,
    )
    stock_quantity = models.PositiveIntegerField(default=100)
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
    is_featured = models.BooleanField(default=False, db_index=True)
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("display_order", "name")
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                "restaurant",
                name="unique_menu_item_name_per_restaurant",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(discount_price__isnull=True)
                    | models.Q(discount_price__lt=models.F("price"))
                ),
                name="discount_price_less_than_price",
            ),
        ]
        indexes = [
            models.Index(fields=("restaurant", "category")),
            models.Index(fields=("restaurant", "is_available", "stock_status")),
            models.Index(fields=("restaurant", "is_featured")),
        ]

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"
