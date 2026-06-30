from decimal import Decimal

from rest_framework import serializers

from apps.accounts.models import User
from apps.orders.models import Order

from .models import (
    CreditAccount,
    CreditTransaction,
    MonthlyStatement,
    Payment,
    Repayment,
)
from . import services


class PaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source="order.order_number", read_only=True)
    customer_email = serializers.EmailField(source="customer.user.email", read_only=True)
    restaurant = serializers.IntegerField(source="order.restaurant_id", read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "order",
            "order_number",
            "customer",
            "customer_email",
            "restaurant",
            "payment_method",
            "payment_status",
            "transaction_id",
            "payment_gateway",
            "gateway_response",
            "paid_amount",
            "currency",
            "paid_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class PaySerializer(serializers.Serializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    payment_method = serializers.ChoiceField(choices=Payment.PaymentMethod.choices)

    def validate_order(self, order):
        request = self.context["request"]
        if request.user.role != User.Role.ADMIN and order.customer.user_id != request.user.id:
            raise serializers.ValidationError("You can only pay for your own orders.")
        if order.order_status == Order.OrderStatus.CANCELLED:
            raise serializers.ValidationError("Cancelled orders cannot be paid.")
        return order

    def save(self, **kwargs):
        return services.create_payment(
            order=self.validated_data["order"],
            payment_method=self.validated_data["payment_method"],
        )


class CreditAccountSerializer(serializers.ModelSerializer):
    customer_email = serializers.EmailField(source="customer.user.email", read_only=True)
    approved_by_email = serializers.EmailField(source="approved_by.email", read_only=True)

    class Meta:
        model = CreditAccount
        fields = (
            "id",
            "customer",
            "customer_email",
            "credit_limit",
            "available_credit",
            "used_credit",
            "outstanding_balance",
            "credit_status",
            "approved_by",
            "approved_by_email",
            "approved_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class ApplyCreditSerializer(serializers.Serializer):
    def save(self, **kwargs):
        customer = self.context["request"].user.customer_profile
        account, _ = CreditAccount.objects.get_or_create(customer=customer)
        return account


class CreditDecisionSerializer(serializers.Serializer):
    credit_limit = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.00"),
        required=False,
    )


class ChangeCreditLimitSerializer(serializers.Serializer):
    credit_limit = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.00"),
    )


class CreditTransactionSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source="order.order_number", read_only=True)

    class Meta:
        model = CreditTransaction
        fields = (
            "id",
            "credit_account",
            "order",
            "order_number",
            "amount",
            "transaction_type",
            "balance_after_transaction",
            "created_at",
        )
        read_only_fields = fields


class MonthlyStatementSerializer(serializers.ModelSerializer):
    customer = serializers.IntegerField(source="credit_account.customer_id", read_only=True)
    customer_email = serializers.EmailField(
        source="credit_account.customer.user.email",
        read_only=True,
    )

    class Meta:
        model = MonthlyStatement
        fields = (
            "id",
            "credit_account",
            "customer",
            "customer_email",
            "billing_month",
            "total_purchases",
            "total_repayments",
            "outstanding_amount",
            "minimum_due",
            "due_date",
            "statement_status",
            "created_at",
        )
        read_only_fields = fields


class RepaymentSerializer(serializers.ModelSerializer):
    customer_email = serializers.EmailField(source="customer.user.email", read_only=True)

    class Meta:
        model = Repayment
        fields = (
            "id",
            "statement",
            "customer",
            "customer_email",
            "amount",
            "payment_method",
            "transaction_id",
            "paid_at",
            "created_at",
        )
        read_only_fields = fields


class RepaySerializer(serializers.Serializer):
    statement = serializers.PrimaryKeyRelatedField(queryset=MonthlyStatement.objects.all())
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )
    payment_method = serializers.ChoiceField(
        choices=[
            (Payment.PaymentMethod.UPI, "UPI"),
            (Payment.PaymentMethod.CREDIT_CARD, "Credit Card"),
            (Payment.PaymentMethod.DEBIT_CARD, "Debit Card"),
            (Payment.PaymentMethod.NET_BANKING, "Net Banking"),
            (Payment.PaymentMethod.WALLET, "Wallet"),
        ],
    )

    def validate_statement(self, statement):
        customer = self.context["request"].user.customer_profile
        if statement.credit_account.customer_id != customer.id:
            raise serializers.ValidationError("This statement does not belong to you.")
        return statement

    def save(self, **kwargs):
        return services.repay_statement(
            statement=self.validated_data["statement"],
            customer=self.context["request"].user.customer_profile,
            amount=self.validated_data["amount"],
            payment_method=self.validated_data["payment_method"],
        )
