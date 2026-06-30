from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.orders.models import Order

from .models import DeliveryAssignment, DeliveryEarnings, DeliveryTracking


ORDER_STATUS_BY_DELIVERY_STATUS = {
    DeliveryAssignment.Status.ACCEPTED: Order.OrderStatus.CONFIRMED,
    DeliveryAssignment.Status.PICKED_UP: Order.OrderStatus.PREPARING,
    DeliveryAssignment.Status.OUT_FOR_DELIVERY: Order.OrderStatus.OUT_FOR_DELIVERY,
    DeliveryAssignment.Status.DELIVERED: Order.OrderStatus.DELIVERED,
    DeliveryAssignment.Status.CANCELLED: Order.OrderStatus.CANCELLED,
}

NEXT_STATUS = {
    DeliveryAssignment.Status.ASSIGNED: DeliveryAssignment.Status.ACCEPTED,
    DeliveryAssignment.Status.ACCEPTED: DeliveryAssignment.Status.PICKED_UP,
    DeliveryAssignment.Status.PICKED_UP: DeliveryAssignment.Status.OUT_FOR_DELIVERY,
    DeliveryAssignment.Status.OUT_FOR_DELIVERY: DeliveryAssignment.Status.DELIVERED,
}


def ensure_order_can_be_assigned(order):
    if order.order_status != Order.OrderStatus.CONFIRMED:
        raise serializers.ValidationError(
            {"order": "Only confirmed orders can be assigned for delivery."}
        )


@transaction.atomic
def assign_delivery(order, delivery_partner, assigned_by, notes=""):
    order = Order.objects.select_for_update().get(id=order.id)
    ensure_order_can_be_assigned(order)
    if DeliveryAssignment.objects.filter(
        order=order,
    ).exclude(
        status__in=(
            DeliveryAssignment.Status.DELIVERED,
            DeliveryAssignment.Status.CANCELLED,
        )
    ).exists():
        raise serializers.ValidationError(
            {"order": "This order already has an active delivery assignment."}
        )

    return DeliveryAssignment.objects.create(
        order=order,
        delivery_partner=delivery_partner,
        assigned_by=assigned_by,
        assigned_at=timezone.now(),
        delivery_notes=notes,
    )


@transaction.atomic
def reassign_delivery(assignment, delivery_partner, assigned_by, notes=""):
    assignment = DeliveryAssignment.objects.select_for_update().select_related("order").get(
        id=assignment.id
    )
    if assignment.status in (
        DeliveryAssignment.Status.DELIVERED,
        DeliveryAssignment.Status.CANCELLED,
    ):
        raise serializers.ValidationError(
            "Delivered or cancelled assignments cannot be reassigned."
        )

    assignment.delivery_partner = delivery_partner
    assignment.assigned_by = assigned_by
    assignment.assigned_at = timezone.now()
    assignment.accepted_at = None
    assignment.picked_up_at = None
    assignment.delivered_at = None
    assignment.cancelled_at = None
    assignment.status = DeliveryAssignment.Status.ASSIGNED
    if notes:
        assignment.delivery_notes = notes
    assignment.save(
        update_fields=(
            "delivery_partner",
            "assigned_by",
            "assigned_at",
            "accepted_at",
            "picked_up_at",
            "delivered_at",
            "cancelled_at",
            "status",
            "delivery_notes",
            "updated_at",
        )
    )
    return assignment


@transaction.atomic
def update_delivery_status(assignment, new_status, notes=""):
    assignment = DeliveryAssignment.objects.select_for_update().select_related("order").get(
        id=assignment.id
    )
    expected_status = NEXT_STATUS.get(assignment.status)
    if new_status != expected_status:
        raise serializers.ValidationError(
            {"status": f"Invalid transition from {assignment.status} to {new_status}."}
        )

    now = timezone.now()
    assignment.status = new_status
    update_fields = ["status", "updated_at"]
    if notes:
        assignment.delivery_notes = notes
        update_fields.append("delivery_notes")
    if new_status == DeliveryAssignment.Status.ACCEPTED:
        assignment.accepted_at = now
        update_fields.append("accepted_at")
    elif new_status == DeliveryAssignment.Status.PICKED_UP:
        assignment.picked_up_at = now
        update_fields.append("picked_up_at")
    elif new_status == DeliveryAssignment.Status.DELIVERED:
        assignment.delivered_at = now
        update_fields.append("delivered_at")
    assignment.save(update_fields=update_fields)

    order_status = ORDER_STATUS_BY_DELIVERY_STATUS.get(new_status)
    if order_status and assignment.order.order_status != order_status:
        assignment.order.order_status = order_status
        assignment.order.save(update_fields=("order_status", "updated_at"))

    if new_status == DeliveryAssignment.Status.DELIVERED:
        generate_earnings(assignment)

    return assignment


@transaction.atomic
def reject_delivery(assignment, notes=""):
    assignment = DeliveryAssignment.objects.select_for_update().select_related("order").get(
        id=assignment.id
    )
    if assignment.status != DeliveryAssignment.Status.ASSIGNED:
        raise serializers.ValidationError("Only assigned deliveries can be rejected.")
    assignment.status = DeliveryAssignment.Status.CANCELLED
    assignment.cancelled_at = timezone.now()
    if notes:
        assignment.delivery_notes = notes
    assignment.save(
        update_fields=("status", "cancelled_at", "delivery_notes", "updated_at")
    )
    return assignment


def generate_earnings(assignment):
    delivery_fee = assignment.order.delivery_charge or Decimal("0.00")
    if delivery_fee == 0:
        delivery_fee = Decimal("40.00")
    incentive = Decimal("0.00")
    earnings, _ = DeliveryEarnings.objects.update_or_create(
        order=assignment.order,
        defaults={
            "delivery_partner": assignment.delivery_partner,
            "delivery_fee": delivery_fee,
            "incentive": incentive,
            "total_earnings": delivery_fee + incentive,
        },
    )
    return earnings


def create_tracking_update(assignment, latitude, longitude, current_location, status=None):
    return DeliveryTracking.objects.create(
        delivery_assignment=assignment,
        latitude=latitude,
        longitude=longitude,
        current_location=current_location,
        status=status or assignment.status,
    )
