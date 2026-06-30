from decimal import Decimal

from rest_framework import serializers

from apps.accounts.models import DeliveryPartnerProfile
from apps.orders.models import Order

from .models import DeliveryAssignment, DeliveryEarnings, DeliveryTracking
from . import services


class DeliveryTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryTracking
        fields = (
            "id",
            "delivery_assignment",
            "latitude",
            "longitude",
            "current_location",
            "status",
            "timestamp",
        )
        read_only_fields = ("id", "delivery_assignment", "status", "timestamp")


class DeliveryAssignmentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source="order.order_number", read_only=True)
    restaurant = serializers.IntegerField(source="order.restaurant_id", read_only=True)
    restaurant_name = serializers.CharField(source="order.restaurant.name", read_only=True)
    customer = serializers.IntegerField(source="order.customer_id", read_only=True)
    customer_email = serializers.EmailField(source="order.customer.user.email", read_only=True)
    delivery_partner_email = serializers.EmailField(
        source="delivery_partner.user.email",
        read_only=True,
    )
    assigned_by_email = serializers.EmailField(source="assigned_by.email", read_only=True)
    latest_tracking = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryAssignment
        fields = (
            "id",
            "order",
            "order_number",
            "restaurant",
            "restaurant_name",
            "customer",
            "customer_email",
            "delivery_partner",
            "delivery_partner_email",
            "status",
            "assigned_by",
            "assigned_by_email",
            "assigned_at",
            "accepted_at",
            "picked_up_at",
            "delivered_at",
            "cancelled_at",
            "delivery_notes",
            "latest_tracking",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_latest_tracking(self, obj):
        tracking = obj.tracking_updates.first()
        if tracking is None:
            return None
        return DeliveryTrackingSerializer(tracking).data


class AssignDeliverySerializer(serializers.Serializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    delivery_partner = serializers.PrimaryKeyRelatedField(
        queryset=DeliveryPartnerProfile.objects.select_related("user").all()
    )
    delivery_notes = serializers.CharField(required=False, allow_blank=True)

    def save(self, **kwargs):
        return services.assign_delivery(
            order=self.validated_data["order"],
            delivery_partner=self.validated_data["delivery_partner"],
            assigned_by=self.context["request"].user,
            notes=self.validated_data.get("delivery_notes", ""),
        )


class ReassignDeliverySerializer(serializers.Serializer):
    delivery_partner = serializers.PrimaryKeyRelatedField(
        queryset=DeliveryPartnerProfile.objects.select_related("user").all()
    )
    delivery_notes = serializers.CharField(required=False, allow_blank=True)

    def save(self, **kwargs):
        return services.reassign_delivery(
            assignment=self.context["assignment"],
            delivery_partner=self.validated_data["delivery_partner"],
            assigned_by=self.context["request"].user,
            notes=self.validated_data.get("delivery_notes", ""),
        )


class UpdateDeliveryStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=(
            (DeliveryAssignment.Status.PICKED_UP, "Picked Up"),
            (DeliveryAssignment.Status.OUT_FOR_DELIVERY, "Out for Delivery"),
            (DeliveryAssignment.Status.DELIVERED, "Delivered"),
        )
    )
    delivery_notes = serializers.CharField(required=False, allow_blank=True)

    def save(self, **kwargs):
        return services.update_delivery_status(
            assignment=self.context["assignment"],
            new_status=self.validated_data["status"],
            notes=self.validated_data.get("delivery_notes", ""),
        )


class DeliveryDecisionSerializer(serializers.Serializer):
    delivery_notes = serializers.CharField(required=False, allow_blank=True)


class TrackingUpdateSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=Decimal("-90.000000"),
        max_value=Decimal("90.000000"),
    )
    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        min_value=Decimal("-180.000000"),
        max_value=Decimal("180.000000"),
    )
    current_location = serializers.CharField(max_length=255)

    def save(self, **kwargs):
        return services.create_tracking_update(
            assignment=self.context["assignment"],
            latitude=self.validated_data["latitude"],
            longitude=self.validated_data["longitude"],
            current_location=self.validated_data["current_location"],
        )


class DeliveryEarningsSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source="order.order_number", read_only=True)
    delivery_partner_email = serializers.EmailField(
        source="delivery_partner.user.email",
        read_only=True,
    )

    class Meta:
        model = DeliveryEarnings
        fields = (
            "id",
            "delivery_partner",
            "delivery_partner_email",
            "order",
            "order_number",
            "delivery_fee",
            "incentive",
            "total_earnings",
            "payment_status",
            "created_at",
        )
        read_only_fields = fields
