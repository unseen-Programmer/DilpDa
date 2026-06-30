from decimal import Decimal

from django.db.models import Avg, Count
from rest_framework import serializers

from apps.orders.models import Order


def ensure_delivered_order(order, customer, restaurant=None):
    if order.customer_id != customer.id:
        raise serializers.ValidationError({"order": "Order does not belong to this customer."})
    if order.order_status != Order.OrderStatus.DELIVERED:
        raise serializers.ValidationError({"order": "Only delivered orders can be reviewed."})
    if restaurant is not None and order.restaurant_id != restaurant.id:
        raise serializers.ValidationError(
            {"restaurant": "Restaurant does not match this order."}
        )


def ensure_menu_item_was_purchased(order, menu_item):
    if not order.items.filter(menu_item=menu_item).exists():
        raise serializers.ValidationError(
            {"menu_item": "This item was not purchased in the selected order."}
        )


def recalculate_restaurant_rating(restaurant):
    aggregate = restaurant.reviews.filter(is_visible=True).aggregate(
        average=Avg("rating"),
        count=Count("id"),
    )
    average = aggregate["average"] or Decimal("0.00")
    restaurant.rating = Decimal(str(average)).quantize(Decimal("0.01"))
    restaurant.total_reviews = aggregate["count"]
    restaurant.save(update_fields=("rating", "total_reviews", "updated_at"))


def recalculate_menu_item_rating(menu_item):
    aggregate = menu_item.reviews.filter(is_visible=True).aggregate(
        average=Avg("rating"),
        count=Count("id"),
    )
    average = aggregate["average"] or Decimal("0.00")
    menu_item.rating = Decimal(str(average)).quantize(Decimal("0.01"))
    menu_item.total_reviews = aggregate["count"]
    menu_item.save(update_fields=("rating", "total_reviews", "updated_at"))
