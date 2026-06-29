from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import (
    CustomerProfile,
    DeliveryPartnerProfile,
    RestaurantOwnerProfile,
)


User = get_user_model()


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ("date_of_birth", "gender", "default_credit_limit")
        read_only_fields = ("default_credit_limit",)


class RestaurantOwnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantOwnerProfile
        fields = ("business_name", "gst_number", "is_verified_owner")
        read_only_fields = ("is_verified_owner",)


class DeliveryPartnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryPartnerProfile
        fields = (
            "vehicle_type",
            "vehicle_number",
            "is_available",
            "is_verified_partner",
        )
        read_only_fields = ("is_verified_partner",)


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "is_email_verified",
            "date_joined",
            "profile",
        )
        read_only_fields = ("id", "email", "role", "is_email_verified", "date_joined")

    def get_profile(self, obj):
        if obj.role == User.Role.CUSTOMER and hasattr(obj, "customer_profile"):
            return CustomerProfileSerializer(obj.customer_profile).data
        if (
            obj.role == User.Role.RESTAURANT_OWNER
            and hasattr(obj, "restaurant_owner_profile")
        ):
            return RestaurantOwnerProfileSerializer(obj.restaurant_owner_profile).data
        if (
            obj.role == User.Role.DELIVERY_PARTNER
            and hasattr(obj, "delivery_partner_profile")
        ):
            return DeliveryPartnerProfileSerializer(obj.delivery_partner_profile).data
        return None


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone_number",
            "role",
        )

    def validate_role(self, value):
        if value == User.Role.ADMIN:
            raise serializers.ValidationError("Admin users cannot register publicly.")
        return value

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["role"] = user.role
        return token

    def validate(self, attrs):
        if self.username_field in attrs:
            attrs[self.username_field] = attrs[self.username_field].lower()
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class ProfileUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    phone_number = serializers.CharField(required=False, allow_blank=True, max_length=20)
    profile = serializers.DictField(required=False)

    def validate_profile(self, value):
        user = self.context["request"].user

        if user.role == User.Role.CUSTOMER:
            serializer = CustomerProfileSerializer(
                instance=user.customer_profile,
                data=value,
                partial=True,
            )
        elif user.role == User.Role.RESTAURANT_OWNER:
            serializer = RestaurantOwnerProfileSerializer(
                instance=user.restaurant_owner_profile,
                data=value,
                partial=True,
            )
        elif user.role == User.Role.DELIVERY_PARTNER:
            serializer = DeliveryPartnerProfileSerializer(
                instance=user.delivery_partner_profile,
                data=value,
                partial=True,
            )
        else:
            raise serializers.ValidationError("Admin users do not have a profile.")

        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    @transaction.atomic
    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save(update_fields=[*validated_data.keys()] or None)

        if profile_data is not None:
            if instance.role == User.Role.CUSTOMER:
                profile = instance.customer_profile
            elif instance.role == User.Role.RESTAURANT_OWNER:
                profile = instance.restaurant_owner_profile
            elif instance.role == User.Role.DELIVERY_PARTNER:
                profile = instance.delivery_partner_profile
            else:
                profile = None

            if profile is not None:
                for field, value in profile_data.items():
                    setattr(profile, field, value)
                profile.save(update_fields=[*profile_data.keys()] or None)

        return instance


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Passwords do not match."}
            )
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user
