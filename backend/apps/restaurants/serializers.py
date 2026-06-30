from rest_framework import serializers

from .models import Restaurant


class RestaurantSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.user.email", read_only=True)

    class Meta:
        model = Restaurant
        fields = (
            "id",
            "owner",
            "owner_email",
            "name",
            "description",
            "logo",
            "cover_image",
            "address",
            "city",
            "state",
            "pincode",
            "latitude",
            "longitude",
            "contact_number",
            "email",
            "cuisine_type",
            "opening_time",
            "closing_time",
            "gst_number",
            "fssai_number",
            "status",
            "rating",
            "total_reviews",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "owner",
            "owner_email",
            "status",
            "rating",
            "total_reviews",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        opening_time = attrs.get(
            "opening_time",
            getattr(self.instance, "opening_time", None),
        )
        closing_time = attrs.get(
            "closing_time",
            getattr(self.instance, "closing_time", None),
        )

        if opening_time and closing_time and opening_time == closing_time:
            raise serializers.ValidationError(
                {"closing_time": "Closing time must be different from opening time."}
            )

        return attrs


class RestaurantStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ("id", "name", "status", "updated_at")
        read_only_fields = ("id", "name", "status", "updated_at")
