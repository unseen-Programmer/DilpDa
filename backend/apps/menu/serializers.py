from django.db.models.functions import Lower
from rest_framework import serializers

from apps.accounts.models import User
from apps.restaurants.models import Restaurant

from .models import FoodCategory, MenuItem


class FoodCategorySerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)

    class Meta:
        model = FoodCategory
        fields = (
            "id",
            "restaurant",
            "restaurant_name",
            "name",
            "description",
            "display_order",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "restaurant_name", "created_at", "updated_at")

    def validate_restaurant(self, restaurant):
        request = self.context["request"]
        user = request.user

        if user.role == User.Role.ADMIN:
            return restaurant
        if restaurant.owner.user_id != user.id:
            raise serializers.ValidationError(
                "You can only manage categories for your own restaurants."
            )
        return restaurant

    def validate(self, attrs):
        restaurant = attrs.get("restaurant", getattr(self.instance, "restaurant", None))
        name = attrs.get("name", getattr(self.instance, "name", None))

        if restaurant and name:
            duplicate = FoodCategory.objects.filter(
                restaurant=restaurant,
            ).annotate(name_lower=Lower("name")).filter(name_lower=name.lower())
            if self.instance is not None:
                duplicate = duplicate.exclude(pk=self.instance.pk)
            if duplicate.exists():
                raise serializers.ValidationError(
                    {"name": "A category with this name already exists for this restaurant."}
                )

        return attrs


class MenuItemSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = MenuItem
        fields = (
            "id",
            "restaurant",
            "restaurant_name",
            "category",
            "category_name",
            "name",
            "description",
            "image",
            "price",
            "discount_price",
            "food_type",
            "preparation_time",
            "is_available",
            "stock_status",
            "stock_quantity",
            "rating",
            "total_reviews",
            "is_featured",
            "display_order",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "restaurant_name",
            "category_name",
            "rating",
            "total_reviews",
            "created_at",
            "updated_at",
        )

    def validate_restaurant(self, restaurant):
        request = self.context["request"]
        user = request.user

        if user.role == User.Role.ADMIN:
            return restaurant
        if restaurant.owner.user_id != user.id:
            raise serializers.ValidationError(
                "You can only manage menu items for your own restaurants."
            )
        return restaurant

    def validate(self, attrs):
        restaurant = attrs.get("restaurant", getattr(self.instance, "restaurant", None))
        category = attrs.get("category", getattr(self.instance, "category", None))
        name = attrs.get("name", getattr(self.instance, "name", None))
        price = attrs.get("price", getattr(self.instance, "price", None))
        discount_price = attrs.get(
            "discount_price",
            getattr(self.instance, "discount_price", None),
        )

        if restaurant and category and category.restaurant_id != restaurant.id:
            raise serializers.ValidationError(
                {"category": "Category must belong to the selected restaurant."}
            )

        if restaurant and name:
            duplicate = MenuItem.objects.filter(
                restaurant=restaurant,
            ).annotate(name_lower=Lower("name")).filter(name_lower=name.lower())
            if self.instance is not None:
                duplicate = duplicate.exclude(pk=self.instance.pk)
            if duplicate.exists():
                raise serializers.ValidationError(
                    {"name": "A menu item with this name already exists for this restaurant."}
                )

        if price is not None and discount_price is not None and discount_price >= price:
            raise serializers.ValidationError(
                {"discount_price": "Discount price must be less than price."}
            )

        return attrs
