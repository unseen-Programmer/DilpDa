from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CreditAccountViewSet,
    CreditTransactionViewSet,
    MonthlyStatementViewSet,
    PaymentViewSet,
    RepaymentViewSet,
)


app_name = "payments"

router = DefaultRouter()
router.register("", PaymentViewSet, basename="payment")
router.register("credit/accounts", CreditAccountViewSet, basename="credit-account")
router.register("credit/transactions", CreditTransactionViewSet, basename="credit-transaction")
router.register("credit/statements", MonthlyStatementViewSet, basename="monthly-statement")
router.register("credit/repayments", RepaymentViewSet, basename="repayment")

urlpatterns = [
    path("", include(router.urls)),
]
