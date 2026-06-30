from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.accounts.models import CustomerProfile
from apps.orders.models import Order


class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        UPI = "UPI", "UPI"
        CREDIT_CARD = "CREDIT_CARD", "Credit Card"
        DEBIT_CARD = "DEBIT_CARD", "Debit Card"
        NET_BANKING = "NET_BANKING", "Net Banking"
        WALLET = "WALLET", "Wallet"
        COD = "COD", "Cash on Delivery"
        DILPDA_PAY_LATER = "DILPDA_PAY_LATER", "DilpDa Pay Later"

    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
    )
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.PROTECT,
        related_name="payments",
    )
    payment_method = models.CharField(max_length=32, choices=PaymentMethod.choices)
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
    )
    transaction_id = models.CharField(max_length=120, unique=True, blank=True, null=True)
    payment_gateway = models.CharField(max_length=80, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    currency = models.CharField(max_length=3, default="INR")
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("customer", "payment_status")),
            models.Index(fields=("order", "payment_status")),
            models.Index(fields=("transaction_id",)),
        ]

    def __str__(self):
        return f"Payment #{self.id} - {self.order.order_number}"


class CreditAccount(models.Model):
    class CreditStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        SUSPENDED = "SUSPENDED", "Suspended"

    customer = models.OneToOneField(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="credit_account",
    )
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    available_credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    used_credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    outstanding_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit_status = models.CharField(
        max_length=20,
        choices=CreditStatus.choices,
        default=CreditStatus.PENDING,
        db_index=True,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_credit_accounts",
        null=True,
        blank=True,
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("credit_status",))]

    def __str__(self):
        return f"Credit account - {self.customer.user.email}"


class CreditTransaction(models.Model):
    class TransactionType(models.TextChoices):
        PURCHASE = "PURCHASE", "Purchase"
        REPAYMENT = "REPAYMENT", "Repayment"
        ADJUSTMENT = "ADJUSTMENT", "Adjustment"

    credit_account = models.ForeignKey(
        CreditAccount,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        related_name="credit_transactions",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    balance_after_transaction = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("credit_account", "transaction_type")),
            models.Index(fields=("order",)),
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"


class MonthlyStatement(models.Model):
    class StatementStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        OVERDUE = "OVERDUE", "Overdue"

    credit_account = models.ForeignKey(
        CreditAccount,
        on_delete=models.CASCADE,
        related_name="statements",
    )
    billing_month = models.DateField()
    total_purchases = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_repayments = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    outstanding_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    minimum_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    statement_status = models.CharField(
        max_length=20,
        choices=StatementStatus.choices,
        default=StatementStatus.PENDING,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-billing_month",)
        constraints = [
            models.UniqueConstraint(
                fields=("credit_account", "billing_month"),
                name="unique_statement_per_account_month",
            ),
        ]
        indexes = [models.Index(fields=("credit_account", "statement_status"))]

    def __str__(self):
        return f"{self.credit_account.customer.user.email} - {self.billing_month:%Y-%m}"


class Repayment(models.Model):
    statement = models.ForeignKey(
        MonthlyStatement,
        on_delete=models.PROTECT,
        related_name="repayments",
    )
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.PROTECT,
        related_name="repayments",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    payment_method = models.CharField(max_length=32, choices=Payment.PaymentMethod.choices)
    transaction_id = models.CharField(max_length=120, unique=True)
    paid_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("customer", "paid_at"))]

    def __str__(self):
        return f"Repayment #{self.id} - {self.amount}"
