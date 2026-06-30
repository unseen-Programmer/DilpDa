from rest_framework import serializers

from apps.accounts.models import User
from apps.menu.models import MenuItem
from apps.orders.models import Order
from apps.restaurants.models import Restaurant

from . import services
from .models import MenuItemReview, RestaurantReview, ReviewLike


class RestaurantReviewSerializer(serializers.ModelSerializer):
    customer_email = serializers.EmailField(source="customer.user.email", read_only=True)
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)

    class Meta:
        model = RestaurantReview
        fields = (
            "id",
            "restaurant",
            "restaurant_name",
            "customer",
            "customer_email",
            "order",
            "rating",
            "review_text",
            "is_edited",
            "is_visible",
            "likes_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "customer",
            "customer_email",
            "restaurant_name",
            "is_edited",
            "is_visible",
            "likes_count",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        request = self.context["request"]
        customer = request.user.customer_profile
        restaurant = attrs.get("restaurant", getattr(self.instance, "restaurant", None))
        order = attrs.get("order", getattr(self.instance, "order", None))

        if self.instance is not None:
            return attrs

        services.ensure_delivered_order(order, customer, restaurant)
        if RestaurantReview.objects.filter(restaurant=restaurant, order=order).exists():
            raise serializers.ValidationError(
                {"order": "This restaurant has already been reviewed for this order."}
            )
        return attrs

    def create(self, validated_data):
        validated_data["customer"] = self.context["request"].user.customer_profile
        review = super().create(validated_data)
        services.recalculate_restaurant_rating(review.restaurant)
        return review

    def update(self, instance, validated_data):
        review = super().update(instance, validated_data)
        review.is_edited = True
        review.save(update_fields=("is_edited", "updated_at"))
        services.recalculate_restaurant_rating(review.restaurant)
        return review


class MenuItemReviewSerializer(serializers.ModelSerializer):
    customer_email = serializers.EmailField(source="customer.user.email", read_only=True)
    menu_item_name = serializers.CharField(source="menu_item.name", read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)

    class Meta:
        model = MenuItemReview
        fields = (
            "id",
            "menu_item",
            "menu_item_name",
            "customer",
            "customer_email",
            "order",
            "rating",
            "review_text",
            "is_visible",
            "likes_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "customer",
            "customer_email",
            "menu_item_name",
            "is_visible",
            "likes_count",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        request = self.context["request"]
        customer = request.user.customer_profile
        menu_item = attrs.get("menu_item", getattr(self.instance, "menu_item", None))
        order = attrs.get("order", getattr(self.instance, "order", None))

        if self.instance is not None:
            return attrs

        services.ensure_delivered_order(order, customer)
        services.ensure_menu_item_was_purchased(order, menu_item)
        if MenuItemReview.objects.filter(menu_item=menu_item, order=order).exists():
            raise serializers.ValidationError(
                {"order": "This menu item has already been reviewed for this order."}
            )
        return attrs

    def create(self, validated_data):
        validated_data["customer"] = self.context["request"].user.customer_profile
        review = super().create(validated_data)
        services.recalculate_menu_item_rating(review.menu_item)
        return review

    def update(self, instance, validated_data):
        review = super().update(instance, validated_data)
        services.recalculate_menu_item_rating(review.menu_item)
        return review


class ReviewLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewLike
        fields = (
            "id",
            "user",
            "restaurant_review",
            "menu_item_review",
            "created_at",
        )
        read_only_fields = ("id", "user", "created_at")

    def validate(self, attrs):
        restaurant_review = attrs.get("restaurant_review")
        menu_item_review = attrs.get("menu_item_review")
        if bool(restaurant_review) == bool(menu_item_review):
            raise serializers.ValidationError(
                "Exactly one review target is required."
            )
        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        like, _ = ReviewLike.objects.get_or_create(**validated_data)
        return like


class ReviewLikeRequestSerializer(serializers.Serializer):
    restaurant_review = serializers.PrimaryKeyRelatedField(
        queryset=RestaurantReview.objects.filter(is_visible=True),
        required=False,
    )
    menu_item_review = serializers.PrimaryKeyRelatedField(
        queryset=MenuItemReview.objects.filter(is_visible=True),
        required=False,
    )

    def validate(self, attrs):
        if bool(attrs.get("restaurant_review")) == bool(attrs.get("menu_item_review")):
            raise serializers.ValidationError("Exactly one review target is required.")
        return attrs
