from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.orders.models import Order

from .models import (
    CreditAccount,
    CreditTransaction,
    MonthlyStatement,
    Payment,
    Repayment,
)


class GatewayResult:
    def __init__(self, success, transaction_id, gateway, response):
        self.success = success
        self.transaction_id = transaction_id
        self.gateway = gateway
        self.response = response


class MockPaymentGateway:
    gateway_name = "internal_mock"

    def charge(self, payment):
        return GatewayResult(
            success=True,
            transaction_id=f"TXN{uuid4().hex[:16].upper()}",
            gateway=self.gateway_name,
            response={"provider": self.gateway_name, "status": "captured"},
        )

    def verify(self, payment):
        return GatewayResult(
            success=True,
            transaction_id=payment.transaction_id or f"TXN{uuid4().hex[:16].upper()}",
            gateway=payment.payment_gateway or self.gateway_name,
            response={"provider": self.gateway_name, "status": "verified"},
        )

    def refund(self, payment):
        return GatewayResult(
            success=True,
            transaction_id=payment.transaction_id,
            gateway=payment.payment_gateway or self.gateway_name,
            response={"provider": self.gateway_name, "status": "refunded"},
        )


def get_gateway(payment_method):
    return MockPaymentGateway()


def current_billing_month(today=None):
    today = today or timezone.localdate()
    return date(today.year, today.month, 1)


def statement_due_date(billing_month):
    last_day = monthrange(billing_month.year, billing_month.month)[1]
    next_month = billing_month + timedelta(days=last_day)
    return date(next_month.year, next_month.month, 15)


def minimum_due(outstanding_amount):
    if outstanding_amount <= 0:
        return Decimal("0.00")
    due = (outstanding_amount * Decimal("0.10")).quantize(Decimal("0.01"))
    return max(due, min(outstanding_amount, Decimal("100.00")))


def get_or_create_statement(credit_account, billing_month=None):
    billing_month = billing_month or current_billing_month()
    statement, _ = MonthlyStatement.objects.get_or_create(
        credit_account=credit_account,
        billing_month=billing_month,
        defaults={"due_date": statement_due_date(billing_month)},
    )
    return statement


def apply_purchase_to_statement(credit_account, amount):
    statement = get_or_create_statement(credit_account)
    statement.total_purchases += amount
    statement.outstanding_amount += amount
    statement.minimum_due = minimum_due(statement.outstanding_amount)
    statement.statement_status = MonthlyStatement.StatementStatus.PENDING
    statement.save(
        update_fields=(
            "total_purchases",
            "outstanding_amount",
            "minimum_due",
            "statement_status",
        )
    )
    return statement


def apply_repayment_to_statements(credit_account, amount):
    remaining = amount
    statements = credit_account.statements.exclude(
        statement_status=MonthlyStatement.StatementStatus.PAID,
    ).order_by("billing_month")

    for statement in statements:
        if remaining <= 0:
            break
        applied = min(statement.outstanding_amount, remaining)
        statement.total_repayments += applied
        statement.outstanding_amount -= applied
        remaining -= applied
        statement.minimum_due = minimum_due(statement.outstanding_amount)
        if statement.outstanding_amount == 0:
            statement.statement_status = MonthlyStatement.StatementStatus.PAID
        statement.save(
            update_fields=(
                "total_repayments",
                "outstanding_amount",
                "minimum_due",
                "statement_status",
            )
        )


@transaction.atomic
def approve_credit_account(account, approved_by, credit_limit):
    account = CreditAccount.objects.select_for_update().get(id=account.id)
    account.credit_limit = credit_limit
    account.available_credit = credit_limit - account.used_credit
    account.credit_status = CreditAccount.CreditStatus.APPROVED
    account.approved_by = approved_by
    account.approved_at = timezone.now()
    account.save(
        update_fields=(
            "credit_limit",
            "available_credit",
            "credit_status",
            "approved_by",
            "approved_at",
            "updated_at",
        )
    )
    return account


@transaction.atomic
def change_credit_limit(account, credit_limit):
    account = CreditAccount.objects.select_for_update().get(id=account.id)
    if credit_limit < account.used_credit:
        raise serializers.ValidationError(
            {"credit_limit": "Credit limit cannot be less than used credit."}
        )
    account.credit_limit = credit_limit
    account.available_credit = credit_limit - account.used_credit
    account.save(update_fields=("credit_limit", "available_credit", "updated_at"))
    return account


@transaction.atomic
def charge_pay_later(order):
    account = (
        CreditAccount.objects.select_for_update()
        .filter(customer=order.customer)
        .first()
    )
    if account is None:
        raise serializers.ValidationError("Pay Later account is required.")
    if account.credit_status != CreditAccount.CreditStatus.APPROVED:
        raise serializers.ValidationError("Pay Later account is not approved.")
    if account.available_credit < order.grand_total:
        raise serializers.ValidationError("Insufficient available credit.")

    account.available_credit -= order.grand_total
    account.used_credit += order.grand_total
    account.outstanding_balance += order.grand_total
    account.save(
        update_fields=(
            "available_credit",
            "used_credit",
            "outstanding_balance",
            "updated_at",
        )
    )
    CreditTransaction.objects.create(
        credit_account=account,
        order=order,
        amount=order.grand_total,
        transaction_type=CreditTransaction.TransactionType.PURCHASE,
        balance_after_transaction=account.outstanding_balance,
    )
    apply_purchase_to_statement(account, order.grand_total)
    return account


@transaction.atomic
def repay_statement(statement, customer, amount, payment_method):
    statement = MonthlyStatement.objects.select_for_update().select_related(
        "credit_account",
    ).get(id=statement.id)
    account = CreditAccount.objects.select_for_update().get(id=statement.credit_account_id)

    if customer.id != account.customer_id:
        raise serializers.ValidationError("This statement does not belong to the customer.")
    if amount > account.outstanding_balance:
        raise serializers.ValidationError(
            {"amount": "Repayment cannot exceed outstanding balance."}
        )
    if amount > statement.outstanding_amount:
        raise serializers.ValidationError(
            {"amount": "Repayment cannot exceed statement outstanding amount."}
        )

    account.outstanding_balance -= amount
    account.used_credit -= amount
    account.available_credit += amount
    account.save(
        update_fields=(
            "outstanding_balance",
            "used_credit",
            "available_credit",
            "updated_at",
        )
    )
    statement.total_repayments += amount
    statement.outstanding_amount -= amount
    statement.minimum_due = minimum_due(statement.outstanding_amount)
    if statement.outstanding_amount == 0:
        statement.statement_status = MonthlyStatement.StatementStatus.PAID
    statement.save(
        update_fields=(
            "total_repayments",
            "outstanding_amount",
            "minimum_due",
            "statement_status",
        )
    )

    repayment = Repayment.objects.create(
        statement=statement,
        customer=customer,
        amount=amount,
        payment_method=payment_method,
        transaction_id=f"RPY{uuid4().hex[:16].upper()}",
    )
    CreditTransaction.objects.create(
        credit_account=account,
        amount=amount,
        transaction_type=CreditTransaction.TransactionType.REPAYMENT,
        balance_after_transaction=account.outstanding_balance,
    )
    return repayment


@transaction.atomic
def create_payment(order, payment_method):
    order = Order.objects.select_for_update().get(id=order.id)
    if Payment.objects.filter(
        order=order,
        payment_status=Payment.PaymentStatus.SUCCESS,
    ).exists():
        raise serializers.ValidationError("This order has already been paid.")

    payment = Payment.objects.create(
        order=order,
        customer=order.customer,
        payment_method=payment_method,
        paid_amount=order.grand_total,
        currency="INR",
    )

    if payment_method == Payment.PaymentMethod.COD:
        payment.payment_gateway = "cash"
        payment.gateway_response = {"status": "pending_collection"}
        payment.save(update_fields=("payment_gateway", "gateway_response", "updated_at"))
        return payment

    if payment_method == Payment.PaymentMethod.DILPDA_PAY_LATER:
        charge_pay_later(order)
        payment.payment_status = Payment.PaymentStatus.SUCCESS
        payment.transaction_id = f"DPL{uuid4().hex[:16].upper()}"
        payment.payment_gateway = "dilpda_pay_later"
        payment.gateway_response = {"status": "credit_charged"}
        payment.paid_at = timezone.now()
        payment.save(
            update_fields=(
                "payment_status",
                "transaction_id",
                "payment_gateway",
                "gateway_response",
                "paid_at",
                "updated_at",
            )
        )
        order.payment_status = Order.PaymentStatus.PAID
        order.save(update_fields=("payment_status", "updated_at"))
        return payment

    gateway = get_gateway(payment_method)
    result = gateway.charge(payment)
    payment.transaction_id = result.transaction_id
    payment.payment_gateway = result.gateway
    payment.gateway_response = result.response
    if result.success:
        payment.payment_status = Payment.PaymentStatus.SUCCESS
        payment.paid_at = timezone.now()
        order.payment_status = Order.PaymentStatus.PAID
        order.save(update_fields=("payment_status", "updated_at"))
    else:
        payment.payment_status = Payment.PaymentStatus.FAILED
        order.payment_status = Order.PaymentStatus.FAILED
        order.save(update_fields=("payment_status", "updated_at"))
    payment.save()
    return payment


@transaction.atomic
def verify_payment(payment):
    payment = Payment.objects.select_for_update().select_related("order").get(id=payment.id)
    if payment.payment_status == Payment.PaymentStatus.REFUNDED:
        raise serializers.ValidationError("Refunded payments cannot be verified.")
    result = get_gateway(payment.payment_method).verify(payment)
    payment.transaction_id = result.transaction_id
    payment.payment_gateway = result.gateway
    payment.gateway_response = result.response
    if result.success:
        payment.payment_status = Payment.PaymentStatus.SUCCESS
        payment.paid_at = payment.paid_at or timezone.now()
        payment.order.payment_status = Order.PaymentStatus.PAID
        payment.order.save(update_fields=("payment_status", "updated_at"))
    payment.save()
    return payment


@transaction.atomic
def refund_payment(payment):
    payment = Payment.objects.select_for_update().select_related("order").get(id=payment.id)
    if payment.payment_status != Payment.PaymentStatus.SUCCESS:
        raise serializers.ValidationError("Only successful payments can be refunded.")
    if payment.payment_method == Payment.PaymentMethod.DILPDA_PAY_LATER:
        account = CreditAccount.objects.select_for_update().get(customer=payment.customer)
        account.outstanding_balance -= payment.paid_amount
        account.used_credit -= payment.paid_amount
        account.available_credit += payment.paid_amount
        account.save(
            update_fields=(
                "outstanding_balance",
                "used_credit",
                "available_credit",
                "updated_at",
            )
        )
        CreditTransaction.objects.create(
            credit_account=account,
            order=payment.order,
            amount=payment.paid_amount,
            transaction_type=CreditTransaction.TransactionType.ADJUSTMENT,
            balance_after_transaction=account.outstanding_balance,
        )
        apply_repayment_to_statements(account, payment.paid_amount)
    else:
        result = get_gateway(payment.payment_method).refund(payment)
        payment.gateway_response = result.response

    payment.payment_status = Payment.PaymentStatus.REFUNDED
    payment.order.payment_status = Order.PaymentStatus.REFUNDED
    payment.order.save(update_fields=("payment_status", "updated_at"))
    payment.save(update_fields=("payment_status", "gateway_response", "updated_at"))
    return payment
