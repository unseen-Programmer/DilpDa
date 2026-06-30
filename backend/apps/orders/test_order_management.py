from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.menu.models import FoodCategory, MenuItem
from apps.restaurants.models import Restaurant

from .models import Cart, CartItem, Order, OrderItem


User = get_user_model()


class OrderManagementAPITests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email="customer-order@example.com",
            password="StrongPass123!",
            role=User.Role.CUSTOMER,
        )
        self.other_customer = User.objects.create_user(
            email="other-customer-order@example.com",
            password="StrongPass123!",
            role=User.Role.CUSTOMER,
        )
        self.owner = User.objects.create_user(
            email="owner-order@example.com",
            password="StrongPass123!",
            role=User.Role.RESTAURANT_OWNER,
        )
        self.other_owner = User.objects.create_user(
            email="other-owner-order@example.com",
            password="StrongPass123!",
            role=User.Role.RESTAURANT_OWNER,
        )
        self.admin = User.objects.create_superuser(
            email="admin-order@example.com",
            password="StrongPass123!",
        )
        self.restaurant = self.create_restaurant(
            self.owner,
            "Order Restaurant",
            Restaurant.Status.APPROVED,
        )
        self.other_restaurant = self.create_restaurant(
            self.other_owner,
            "Other Order Restaurant",
            Restaurant.Status.APPROVED,
        )
        self.category = FoodCategory.objects.create(
            restaurant=self.restaurant,
            name="Mains",
        )
        self.other_category = FoodCategory.objects.create(
            restaurant=self.other_restaurant,
            name="Other Mains",
        )
        self.menu_item = self.create_menu_item(
            restaurant=self.restaurant,
            category=self.category,
            name="Order Paneer",
            price="200.00",
            discount_price="150.00",
            stock_quantity=5,
        )
        self.second_item = self.create_menu_item(
            restaurant=self.restaurant,
            category=self.category,
            name="Order Roll",
            price="100.00",
            discount_price=None,
            stock_quantity=2,
        )
        self.other_item = self.create_menu_item(
            restaurant=self.other_restaurant,
            category=self.other_category,
            name="Other Item",
            stock_quantity=5,
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def create_restaurant(self, owner, name, status_value):
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
            status=status_value,
        )

    def create_menu_item(
        self,
        restaurant,
        category,
        name,
        price="120.00",
        discount_price="100.00",
        stock_quantity=10,
    ):
        return MenuItem.objects.create(
            restaurant=restaurant,
            category=category,
            name=name,
            description="A test item.",
            price=price,
            discount_price=discount_price,
            food_type=MenuItem.FoodType.VEG,
            preparation_time=20,
            stock_quantity=stock_quantity,
            is_available=True,
            stock_status=MenuItem.StockStatus.IN_STOCK,
            display_order=1,
        )

    def add_cart_item(self, menu_item, quantity):
        cart, _ = Cart.objects.get_or_create(
            customer=self.customer.customer_profile,
            is_active=True,
            defaults={"restaurant": menu_item.restaurant},
        )
        cart.restaurant = menu_item.restaurant
        cart.save(update_fields=("restaurant", "updated_at"))
        return CartItem.objects.create(
            cart=cart,
            menu_item=menu_item,
            quantity=quantity,
        )

    def place_payload(self):
        return {
            "delivery_address": "221B Food Lane, Kolkata",
            "payment_method": Order.PaymentMethod.COD,
            "delivery_charge": "30.00",
            "notes": "Leave at the door.",
        }

    def place_order(self):
        return self.client.post(
            reverse("orders:order-place"),
            self.place_payload(),
            format="json",
        )

    def test_customer_can_place_order_from_active_cart(self):
        self.add_cart_item(self.menu_item, 2)
        self.add_cart_item(self.second_item, 1)
        self.authenticate(self.customer)

        response = self.place_order()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["order_number"].startswith("ORD"))
        self.assertEqual(response.data["restaurant"], self.restaurant.id)
        self.assertEqual(response.data["subtotal"], "500.00")
        self.assertEqual(response.data["discount"], "100.00")
        self.assertEqual(response.data["delivery_charge"], "30.00")
        self.assertEqual(response.data["grand_total"], "430.00")
        self.assertEqual(len(response.data["items"]), 2)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 2)

        self.menu_item.refresh_from_db()
        self.second_item.refresh_from_db()
        self.assertEqual(self.menu_item.stock_quantity, 3)
        self.assertEqual(self.second_item.stock_quantity, 1)
        cart = Cart.objects.get(customer=self.customer.customer_profile)
        self.assertEqual(cart.items.count(), 0)
        self.assertIsNone(cart.restaurant)

    def test_order_sets_item_out_of_stock_when_quantity_reaches_zero(self):
        self.add_cart_item(self.second_item, 2)
        self.authenticate(self.customer)

        response = self.place_order()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.second_item.refresh_from_db()
        self.assertEqual(self.second_item.stock_quantity, 0)
        self.assertEqual(self.second_item.stock_status, MenuItem.StockStatus.OUT_OF_STOCK)

    def test_place_order_rejects_empty_cart_and_insufficient_stock(self):
        self.authenticate(self.customer)
        empty_response = self.place_order()

        self.add_cart_item(self.second_item, 3)
        insufficient_response = self.place_order()

        self.assertEqual(empty_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(insufficient_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

    def test_only_customers_can_place_orders(self):
        self.add_cart_item(self.menu_item, 1)

        anonymous_response = self.client.post(
            reverse("orders:order-place"),
            self.place_payload(),
            format="json",
        )
        self.authenticate(self.owner)
        owner_response = self.client.post(
            reverse("orders:order-place"),
            self.place_payload(),
            format="json",
        )

        self.assertEqual(anonymous_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(owner_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_history_and_details_are_scoped_to_customer(self):
        self.add_cart_item(self.menu_item, 1)
        self.authenticate(self.customer)
        placed_response = self.place_order()

        other_order = Order.objects.create(
            customer=self.other_customer.customer_profile,
            restaurant=self.restaurant,
            delivery_address="Other address",
            payment_method=Order.PaymentMethod.COD,
            subtotal="100.00",
            discount="0.00",
            delivery_charge="0.00",
            grand_total="100.00",
        )

        history_response = self.client.get(reverse("orders:order-history"))
        own_detail_response = self.client.get(
            reverse("orders:order-detail", args=(placed_response.data["id"],)),
        )
        other_detail_response = self.client.get(
            reverse("orders:order-detail", args=(other_order.id,)),
        )

        self.assertEqual(history_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(history_response.data), 1)
        self.assertEqual(own_detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(other_detail_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_can_cancel_own_order_before_delivery(self):
        self.add_cart_item(self.menu_item, 1)
        self.authenticate(self.customer)
        placed_response = self.place_order()

        cancel_response = self.client.post(
            reverse("orders:order-cancel", args=(placed_response.data["id"],)),
            {"reason": "Changed my mind."},
            format="json",
        )

        self.assertEqual(cancel_response.status_code, status.HTTP_200_OK)
        self.assertEqual(cancel_response.data["order_status"], Order.OrderStatus.CANCELLED)
        self.assertIn("Changed my mind.", cancel_response.data["notes"])

    def test_customer_cannot_cancel_delivered_order(self):
        self.add_cart_item(self.menu_item, 1)
        self.authenticate(self.customer)
        placed_response = self.place_order()
        order = Order.objects.get(id=placed_response.data["id"])
        order.order_status = Order.OrderStatus.DELIVERED
        order.save(update_fields=("order_status", "updated_at"))

        response = self.client.post(
            reverse("orders:order-cancel", args=(order.id,)),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_restaurant_owner_can_view_and_update_own_restaurant_orders(self):
        self.add_cart_item(self.menu_item, 1)
        self.authenticate(self.customer)
        placed_response = self.place_order()

        self.authenticate(self.owner)
        restaurant_orders_response = self.client.get(
            reverse("orders:order-restaurant-orders"),
        )
        update_response = self.client.patch(
            reverse("orders:order-update-status", args=(placed_response.data["id"],)),
            {"order_status": Order.OrderStatus.PREPARING},
            format="json",
        )

        self.assertEqual(restaurant_orders_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(restaurant_orders_response.data), 1)
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["order_status"], Order.OrderStatus.PREPARING)

    def test_restaurant_owner_cannot_access_other_restaurant_order(self):
        self.add_cart_item(self.menu_item, 1)
        self.authenticate(self.customer)
        placed_response = self.place_order()

        self.authenticate(self.other_owner)
        detail_response = self.client.get(
            reverse("orders:order-detail", args=(placed_response.data["id"],)),
        )
        update_response = self.client.patch(
            reverse("orders:order-update-status", args=(placed_response.data["id"],)),
            {"order_status": Order.OrderStatus.CONFIRMED},
            format="json",
        )

        self.assertEqual(detail_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(update_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_view_and_update_any_order(self):
        self.add_cart_item(self.menu_item, 1)
        self.authenticate(self.customer)
        placed_response = self.place_order()

        self.authenticate(self.admin)
        detail_response = self.client.get(
            reverse("orders:order-detail", args=(placed_response.data["id"],)),
        )
        update_response = self.client.patch(
            reverse("orders:order-update-status", args=(placed_response.data["id"],)),
            {"order_status": Order.OrderStatus.DELIVERED},
            format="json",
        )

        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["order_status"], Order.OrderStatus.DELIVERED)

    def test_restaurant_orders_can_filter_by_restaurant_for_admin(self):
        self.add_cart_item(self.menu_item, 1)
        self.authenticate(self.customer)
        self.place_order()
        other_order = Order.objects.create(
            customer=self.other_customer.customer_profile,
            restaurant=self.other_restaurant,
            delivery_address="Other address",
            payment_method=Order.PaymentMethod.COD,
            subtotal="100.00",
            discount="0.00",
            delivery_charge="0.00",
            grand_total="100.00",
        )

        self.authenticate(self.admin)
        response = self.client.get(
            reverse("orders:order-restaurant-orders"),
            {"restaurant": self.other_restaurant.id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], other_order.id)
