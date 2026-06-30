from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.menu.models import FoodCategory, MenuItem
from apps.orders.models import Order
from apps.restaurants.models import Restaurant

from .models import CreditAccount, CreditTransaction, MonthlyStatement, Payment, Repayment


User = get_user_model()


class PaymentAndPayLaterTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email="pay-customer@example.com",
            password="StrongPass123!",
            role=User.Role.CUSTOMER,
        )
        self.other_customer = User.objects.create_user(
            email="pay-other-customer@example.com",
            password="StrongPass123!",
            role=User.Role.CUSTOMER,
        )
        self.owner = User.objects.create_user(
            email="pay-owner@example.com",
            password="StrongPass123!",
            role=User.Role.RESTAURANT_OWNER,
        )
        self.other_owner = User.objects.create_user(
            email="pay-other-owner@example.com",
            password="StrongPass123!",
            role=User.Role.RESTAURANT_OWNER,
        )
        self.admin = User.objects.create_superuser(
            email="pay-admin@example.com",
            password="StrongPass123!",
        )
        self.restaurant = self.create_restaurant(self.owner, "Payment Restaurant")
        self.other_restaurant = self.create_restaurant(
            self.other_owner,
            "Other Payment Restaurant",
        )
        self.category = FoodCategory.objects.create(
            restaurant=self.restaurant,
            name="Payments",
        )
        self.menu_item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name="Payment Item",
            price="120.00",
            food_type=MenuItem.FoodType.VEG,
            preparation_time=20,
            stock_quantity=10,
        )
        self.order = self.create_order(self.customer, self.restaurant, "500.00")
        self.other_order = self.create_order(
            self.other_customer,
            self.other_restaurant,
            "200.00",
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def create_restaurant(self, owner, name):
        return Restaurant.objects.create(
            owner=owner.restaurant_owner_profile,
            name=name,
            description="A test restaurant.",
            address="123 Food Street",
            city="Kolkata",
            state="West Bengal",
            pincode="700001",
            latitude="22.572600",
            longitude="88.363900",
            contact_number="9876543210",
            email=f"{name.lower().replace(' ', '')}@example.com",
            cuisine_type="Bengali",
            opening_time="09:00:00",
            closing_time="22:00:00",
            gst_number="19ABCDE1234F1Z5",
            fssai_number="12345678901234",
            status=Restaurant.Status.APPROVED,
        )

    def create_order(self, customer, restaurant, amount):
        return Order.objects.create(
            customer=customer.customer_profile,
            restaurant=restaurant,
            delivery_address="123 Delivery Lane",
            payment_method=Order.PaymentMethod.COD,
            subtotal=amount,
            discount="0.00",
            delivery_charge="0.00",
            grand_total=amount,
        )

    def pay(self, order=None, method=Payment.PaymentMethod.UPI):
        return self.client.post(
            reverse("payments:payment-pay"),
            {
                "order": (order or self.order).id,
                "payment_method": method,
            },
            format="json",
        )

    def test_customer_can_pay_order_and_view_payment_history(self):
        self.authenticate(self.customer)

        pay_response = self.pay(method=Payment.PaymentMethod.UPI)
        history_response = self.client.get(reverse("payments:payment-history"))
        detail_response = self.client.get(
            reverse("payments:payment-detail", args=(pay_response.data["id"],)),
        )

        self.assertEqual(pay_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(pay_response.data["payment_status"], Payment.PaymentStatus.SUCCESS)
        self.assertEqual(pay_response.data["paid_amount"], "500.00")
        self.assertTrue(pay_response.data["transaction_id"].startswith("TXN"))
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, Order.PaymentStatus.PAID)
        self.assertEqual(history_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(history_response.data), 1)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)

    def test_cash_on_delivery_payment_remains_pending(self):
        self.authenticate(self.customer)

        response = self.pay(method=Payment.PaymentMethod.COD)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["payment_status"], Payment.PaymentStatus.PENDING)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, Order.PaymentStatus.PENDING)

    def test_customer_cannot_pay_another_customer_order(self):
        self.authenticate(self.customer)

        response = self.pay(order=self.other_order)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_restaurant_owner_can_view_only_own_restaurant_payments(self):
        Payment.objects.create(
            order=self.order,
            customer=self.customer.customer_profile,
            payment_method=Payment.PaymentMethod.UPI,
            payment_status=Payment.PaymentStatus.SUCCESS,
            transaction_id="TXNOWNER1",
            paid_amount=self.order.grand_total,
        )
        other_payment = Payment.objects.create(
            order=self.other_order,
            customer=self.other_customer.customer_profile,
            payment_method=Payment.PaymentMethod.UPI,
            payment_status=Payment.PaymentStatus.SUCCESS,
            transaction_id="TXNOWNER2",
            paid_amount=self.other_order.grand_total,
        )
        self.authenticate(self.owner)

        history_response = self.client.get(reverse("payments:payment-history"))
        other_detail_response = self.client.get(
            reverse("payments:payment-detail", args=(other_payment.id,)),
        )

        self.assertEqual(history_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(history_response.data), 1)
        self.assertEqual(other_detail_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_verify_and_refund_payment(self):
        self.authenticate(self.customer)
        pay_response = self.pay()
        payment_id = pay_response.data["id"]

        self.authenticate(self.admin)
        verify_response = self.client.post(
            reverse("payments:payment-verify", args=(payment_id,)),
        )
        refund_response = self.client.post(
            reverse("payments:payment-refund", args=(payment_id,)),
        )

        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        self.assertEqual(refund_response.status_code, status.HTTP_200_OK)
        self.assertEqual(refund_response.data["payment_status"], Payment.PaymentStatus.REFUNDED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, Order.PaymentStatus.REFUNDED)

    def test_customer_cannot_refund_payment(self):
        self.authenticate(self.customer)
        pay_response = self.pay()

        response = self.client.post(
            reverse("payments:payment-refund", args=(pay_response.data["id"],)),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_can_apply_for_credit_and_admin_can_approve_change_suspend_reject(self):
        self.authenticate(self.customer)
        apply_response = self.client.post(reverse("payments:credit-account-apply"))

        self.authenticate(self.admin)
        approve_response = self.client.post(
            reverse("payments:credit-account-approve", args=(apply_response.data["id"],)),
            {"credit_limit": "1000.00"},
            format="json",
        )
        change_response = self.client.patch(
            reverse("payments:credit-account-change-limit", args=(apply_response.data["id"],)),
            {"credit_limit": "1200.00"},
            format="json",
        )
        suspend_response = self.client.post(
            reverse("payments:credit-account-suspend", args=(apply_response.data["id"],)),
        )

        self.assertEqual(apply_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(approve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(approve_response.data["credit_status"], CreditAccount.CreditStatus.APPROVED)
        self.assertEqual(approve_response.data["available_credit"], "1000.00")
        self.assertEqual(change_response.data["credit_limit"], "1200.00")
        self.assertEqual(change_response.data["available_credit"], "1200.00")
        self.assertEqual(suspend_response.data["credit_status"], CreditAccount.CreditStatus.SUSPENDED)

    def approve_credit(self, limit="1000.00"):
        account = CreditAccount.objects.create(customer=self.customer.customer_profile)
        self.authenticate(self.admin)
        self.client.post(
            reverse("payments:credit-account-approve", args=(account.id,)),
            {"credit_limit": limit},
            format="json",
        )
        account.refresh_from_db()
        return account

    def test_pay_later_purchase_reduces_credit_and_generates_statement(self):
        account = self.approve_credit("1000.00")
        self.authenticate(self.customer)

        response = self.pay(method=Payment.PaymentMethod.DILPDA_PAY_LATER)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["payment_status"], Payment.PaymentStatus.SUCCESS)
        account.refresh_from_db()
        self.assertEqual(account.available_credit, 500)
        self.assertEqual(account.used_credit, 500)
        self.assertEqual(account.outstanding_balance, 500)
        self.assertEqual(CreditTransaction.objects.count(), 1)
        transaction = CreditTransaction.objects.first()
        self.assertEqual(transaction.transaction_type, CreditTransaction.TransactionType.PURCHASE)
        statement = MonthlyStatement.objects.get(credit_account=account)
        self.assertEqual(statement.total_purchases, 500)
        self.assertEqual(statement.outstanding_amount, 500)
        self.assertEqual(statement.minimum_due, 100)

    def test_pay_later_rejects_insufficient_or_suspended_credit(self):
        account = self.approve_credit("100.00")
        self.authenticate(self.customer)
        insufficient_response = self.pay(method=Payment.PaymentMethod.DILPDA_PAY_LATER)

        account.credit_limit = "1000.00"
        account.available_credit = "1000.00"
        account.credit_status = CreditAccount.CreditStatus.SUSPENDED
        account.save()
        suspended_response = self.pay(method=Payment.PaymentMethod.DILPDA_PAY_LATER)

        self.assertEqual(insufficient_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(suspended_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(CreditTransaction.objects.count(), 0)

    def test_repayment_increases_available_credit_and_rejects_overpayment(self):
        account = self.approve_credit("1000.00")
        self.authenticate(self.customer)
        self.pay(method=Payment.PaymentMethod.DILPDA_PAY_LATER)
        statement = MonthlyStatement.objects.get(credit_account=account)

        repay_response = self.client.post(
            reverse("payments:repayment-repay"),
            {
                "statement": statement.id,
                "amount": "200.00",
                "payment_method": Payment.PaymentMethod.UPI,
            },
            format="json",
        )
        overpay_response = self.client.post(
            reverse("payments:repayment-repay"),
            {
                "statement": statement.id,
                "amount": "1000.00",
                "payment_method": Payment.PaymentMethod.UPI,
            },
            format="json",
        )

        self.assertEqual(repay_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(overpay_response.status_code, status.HTTP_400_BAD_REQUEST)
        account.refresh_from_db()
        statement.refresh_from_db()
        self.assertEqual(account.available_credit, 700)
        self.assertEqual(account.outstanding_balance, 300)
        self.assertEqual(statement.total_repayments, 200)
        self.assertEqual(statement.outstanding_amount, 300)
        self.assertEqual(Repayment.objects.count(), 1)
        self.assertEqual(CreditTransaction.objects.count(), 2)

    def test_customer_and_admin_statement_transaction_repayment_visibility(self):
        account = self.approve_credit("1000.00")
        self.authenticate(self.customer)
        self.pay(method=Payment.PaymentMethod.DILPDA_PAY_LATER)
        statement = MonthlyStatement.objects.get(credit_account=account)
        self.client.post(
            reverse("payments:repayment-repay"),
            {
                "statement": statement.id,
                "amount": "100.00",
                "payment_method": Payment.PaymentMethod.UPI,
            },
            format="json",
        )

        customer_statements = self.client.get(reverse("payments:monthly-statement-list"))
        customer_transactions = self.client.get(reverse("payments:credit-transaction-list"))
        customer_repayments = self.client.get(reverse("payments:repayment-list"))

        self.authenticate(self.admin)
        admin_statements = self.client.get(reverse("payments:monthly-statement-list"))
        admin_repayments = self.client.get(reverse("payments:repayment-list"))

        self.assertEqual(customer_statements.status_code, status.HTTP_200_OK)
        self.assertEqual(len(customer_statements.data), 1)
        self.assertEqual(len(customer_transactions.data), 2)
        self.assertEqual(len(customer_repayments.data), 1)
        self.assertEqual(admin_statements.status_code, status.HTTP_200_OK)
        self.assertEqual(len(admin_statements.data), 1)
        self.assertEqual(admin_repayments.status_code, status.HTTP_200_OK)
        self.assertEqual(len(admin_repayments.data), 1)
