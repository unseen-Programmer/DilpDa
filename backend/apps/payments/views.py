from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import User

from . import services
from .models import CreditAccount, CreditTransaction, MonthlyStatement, Payment, Repayment
from .permissions import IsAdminRole, IsCustomer, IsPaymentActor
from .serializers import (
    ApplyCreditSerializer,
    ChangeCreditLimitSerializer,
    CreditAccountSerializer,
    CreditDecisionSerializer,
    CreditTransactionSerializer,
    MonthlyStatementSerializer,
    PaySerializer,
    PaymentSerializer,
    RepaySerializer,
    RepaymentSerializer,
)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = (IsPaymentActor,)

    def get_queryset(self):
        queryset = Payment.objects.select_related(
            "order",
            "order__restaurant",
            "order__restaurant__owner",
            "order__restaurant__owner__user",
            "customer",
            "customer__user",
        )
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.RESTAURANT_OWNER:
            return queryset.filter(order__restaurant__owner__user=user)
        return queryset.filter(customer__user=user)

    @action(detail=False, methods=("post",), permission_classes=(IsCustomer,), url_path="pay")
    def pay(self, request):
        serializer = PaySerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=("get",), url_path="history")
    def history(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=("post",), url_path="verify")
    def verify(self, request, pk=None):
        payment = services.verify_payment(self.get_object())
        return Response(self.get_serializer(payment).data)

    @action(detail=True, methods=("post",), permission_classes=(IsAdminRole,), url_path="refund")
    def refund(self, request, pk=None):
        payment = services.refund_payment(self.get_object())
        return Response(self.get_serializer(payment).data)


class CreditAccountViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CreditAccountSerializer
    permission_classes = (IsPaymentActor,)

    def get_queryset(self):
        queryset = CreditAccount.objects.select_related("customer", "customer__user", "approved_by")
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.CUSTOMER:
            return queryset.filter(customer__user=user)
        return queryset.none()

    @action(detail=False, methods=("post",), permission_classes=(IsCustomer,), url_path="apply")
    def apply(self, request):
        serializer = ApplyCreditSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        account = serializer.save()
        return Response(self.get_serializer(account).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=("get",), permission_classes=(IsCustomer,), url_path="me")
    def me(self, request):
        account = CreditAccount.objects.filter(customer=request.user.customer_profile).first()
        if account is None:
            return Response({"detail": "Credit account not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(account).data)

    @action(detail=True, methods=("post",), permission_classes=(IsAdminRole,), url_path="approve")
    def approve(self, request, pk=None):
        account = self.get_object()
        serializer = CreditDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        credit_limit = serializer.validated_data.get("credit_limit", account.credit_limit)
        account = services.approve_credit_account(account, request.user, credit_limit)
        return Response(self.get_serializer(account).data)

    @action(detail=True, methods=("post",), permission_classes=(IsAdminRole,), url_path="reject")
    def reject(self, request, pk=None):
        account = self.get_object()
        account.credit_status = CreditAccount.CreditStatus.REJECTED
        account.save(update_fields=("credit_status", "updated_at"))
        return Response(self.get_serializer(account).data)

    @action(detail=True, methods=("post",), permission_classes=(IsAdminRole,), url_path="suspend")
    def suspend(self, request, pk=None):
        account = self.get_object()
        account.credit_status = CreditAccount.CreditStatus.SUSPENDED
        account.save(update_fields=("credit_status", "updated_at"))
        return Response(self.get_serializer(account).data)

    @action(detail=True, methods=("patch",), permission_classes=(IsAdminRole,), url_path="change-limit")
    def change_limit(self, request, pk=None):
        account = self.get_object()
        serializer = ChangeCreditLimitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = services.change_credit_limit(account, serializer.validated_data["credit_limit"])
        return Response(self.get_serializer(account).data)


class CreditTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CreditTransactionSerializer
    permission_classes = (IsPaymentActor,)

    def get_queryset(self):
        queryset = CreditTransaction.objects.select_related(
            "credit_account",
            "credit_account__customer",
            "credit_account__customer__user",
            "order",
        )
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.CUSTOMER:
            return queryset.filter(credit_account__customer__user=user)
        return queryset.none()


class MonthlyStatementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MonthlyStatementSerializer
    permission_classes = (IsPaymentActor,)

    def get_queryset(self):
        queryset = MonthlyStatement.objects.select_related(
            "credit_account",
            "credit_account__customer",
            "credit_account__customer__user",
        )
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.CUSTOMER:
            return queryset.filter(credit_account__customer__user=user)
        return queryset.none()


class RepaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RepaymentSerializer
    permission_classes = (IsPaymentActor,)

    def get_queryset(self):
        queryset = Repayment.objects.select_related("statement", "customer", "customer__user")
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.CUSTOMER:
            return queryset.filter(customer__user=user)
        return queryset.none()

    @action(detail=False, methods=("post",), permission_classes=(IsCustomer,), url_path="repay")
    def repay(self, request):
        serializer = RepaySerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        repayment = serializer.save()
        return Response(self.get_serializer(repayment).data, status=status.HTTP_201_CREATED)
