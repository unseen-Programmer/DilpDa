from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.accounts.models import CustomerProfile
from apps.menu.models import MenuItem
from apps.orders.models import Order
from apps.restaurants.models import Restaurant


class RestaurantReview(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="restaurant_reviews",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="restaurant_reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    review_text = models.TextField(blank=True)
    is_edited = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("restaurant", "order"),
                name="unique_restaurant_review_per_order",
            ),
        ]
        indexes = [
            models.Index(fields=("restaurant", "is_visible")),
            models.Index(fields=("customer", "created_at")),
            models.Index(fields=("rating",)),
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.rating}"


class MenuItemReview(models.Model):
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="menu_item_reviews",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="menu_item_reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    review_text = models.TextField(blank=True)
    is_visible = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("menu_item", "order"),
                name="unique_menu_item_review_per_order",
            ),
        ]
        indexes = [
            models.Index(fields=("menu_item", "is_visible")),
            models.Index(fields=("customer", "created_at")),
            models.Index(fields=("rating",)),
        ]

    def __str__(self):
        return f"{self.menu_item.name} - {self.rating}"


class ReviewLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="review_likes",
    )
    restaurant_review = models.ForeignKey(
        RestaurantReview,
        on_delete=models.CASCADE,
        related_name="likes",
        null=True,
        blank=True,
    )
    menu_item_review = models.ForeignKey(
        MenuItemReview,
        on_delete=models.CASCADE,
        related_name="likes",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("user", "restaurant_review"),
                name="unique_restaurant_review_like",
            ),
            models.UniqueConstraint(
                fields=("user", "menu_item_review"),
                name="unique_menu_item_review_like",
            ),
            models.CheckConstraint(
                check=(
                    (
                        models.Q(restaurant_review__isnull=False)
                        & models.Q(menu_item_review__isnull=True)
                    )
                    | (
                        models.Q(restaurant_review__isnull=True)
                        & models.Q(menu_item_review__isnull=False)
                    )
                ),
                name="review_like_targets_exactly_one_review",
            ),
        ]

    def __str__(self):
        return f"Like by {self.user.email}"
