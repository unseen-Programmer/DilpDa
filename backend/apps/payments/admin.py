from django.contrib import admin

from .models import (
    CreditAccount,
    CreditTransaction,
    MonthlyStatement,
    Payment,
    Repayment,
)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "customer",
        "payment_method",
        "payment_status",
        "paid_amount",
        "currency",
        "payment_gateway",
        "paid_at",
    )
    list_filter = ("payment_method", "payment_status", "currency", "payment_gateway")
    search_fields = (
        "order__order_number",
        "customer__user__email",
        "transaction_id",
    )
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("order", "customer", "customer__user")


@admin.register(CreditAccount)
class CreditAccountAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "credit_limit",
        "available_credit",
        "used_credit",
        "outstanding_balance",
        "credit_status",
        "approved_by",
        "approved_at",
    )
    list_filter = ("credit_status",)
    search_fields = ("customer__user__email", "approved_by__email")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("customer", "customer__user", "approved_by")


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "credit_account",
        "order",
        "amount",
        "transaction_type",
        "balance_after_transaction",
        "created_at",
    )
    list_filter = ("transaction_type",)
    search_fields = (
        "credit_account__customer__user__email",
        "order__order_number",
    )
    list_select_related = ("credit_account", "credit_account__customer", "order")


@admin.register(MonthlyStatement)
class MonthlyStatementAdmin(admin.ModelAdmin):
    list_display = (
        "credit_account",
        "billing_month",
        "total_purchases",
        "total_repayments",
        "outstanding_amount",
        "minimum_due",
        "due_date",
        "statement_status",
    )
    list_filter = ("statement_status", "billing_month", "due_date")
    search_fields = ("credit_account__customer__user__email",)
    list_select_related = ("credit_account", "credit_account__customer")


@admin.register(Repayment)
class RepaymentAdmin(admin.ModelAdmin):
    list_display = (
        "statement",
        "customer",
        "amount",
        "payment_method",
        "transaction_id",
        "paid_at",
    )
    list_filter = ("payment_method", "paid_at")
    search_fields = (
        "statement__credit_account__customer__user__email",
        "customer__user__email",
        "transaction_id",
    )
    list_select_related = ("statement", "customer", "customer__user")
