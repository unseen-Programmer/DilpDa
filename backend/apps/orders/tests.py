from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.menu.models import FoodCategory, MenuItem
from apps.restaurants.models import Restaurant

from .models import Cart, CartItem


User = get_user_model()


class CartManagementAPITests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email="customer@example.com",
            password="StrongPass123!",
            role=User.Role.CUSTOMER,
        )
        self.other_customer = User.objects.create_user(
            email="othercustomer@example.com",
            password="StrongPass123!",
            role=User.Role.CUSTOMER,
        )
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="StrongPass123!",
            role=User.Role.RESTAURANT_OWNER,
        )
        self.other_owner = User.objects.create_user(
            email="otherowner@example.com",
            password="StrongPass123!",
            role=User.Role.RESTAURANT_OWNER,
        )

        self.restaurant = self.create_restaurant(
            self.owner,
            "Approved Restaurant",
            Restaurant.Status.APPROVED,
        )
        self.other_restaurant = self.create_restaurant(
            self.other_owner,
            "Other Restaurant",
            Restaurant.Status.APPROVED,
        )
        self.pending_restaurant = self.create_restaurant(
            self.owner,
            "Pending Restaurant",
            Restaurant.Status.PENDING,
        )

        self.category = FoodCategory.objects.create(
            restaurant=self.restaurant,
            name="Starters",
        )
        self.other_category = FoodCategory.objects.create(
            restaurant=self.other_restaurant,
            name="Mains",
        )
        self.pending_category = FoodCategory.objects.create(
            restaurant=self.pending_restaurant,
            name="Hidden",
        )

        self.menu_item = self.create_menu_item(
            restaurant=self.restaurant,
            category=self.category,
            name="Paneer Tikka",
            price="200.00",
            discount_price="150.00",
        )
        self.full_price_item = self.create_menu_item(
            restaurant=self.restaurant,
            category=self.category,
            name="Veg Roll",
            price="100.00",
            discount_price=None,
        )
        self.other_restaurant_item = self.create_menu_item(
            restaurant=self.other_restaurant,
            category=self.other_category,
            name="Other Curry",
            price="180.00",
            discount_price="160.00",
        )
        self.unavailable_item = self.create_menu_item(
            restaurant=self.restaurant,
            category=self.category,
            name="Unavailable Soup",
            is_available=False,
        )
        self.out_of_stock_item = self.create_menu_item(
            restaurant=self.restaurant,
            category=self.category,
            name="Sold Out Dessert",
            stock_status=MenuItem.StockStatus.OUT_OF_STOCK,
        )
        self.pending_restaurant_item = self.create_menu_item(
            restaurant=self.pending_restaurant,
            category=self.pending_category,
            name="Pending Item",
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
        is_available=True,
        stock_status=MenuItem.StockStatus.IN_STOCK,
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
            is_available=is_available,
            stock_status=stock_status,
            display_order=1,
        )

    def add_to_cart(self, menu_item=None, quantity=1):
        menu_item = menu_item or self.menu_item
        return self.client.post(
            reverse("orders:cart-add"),
            {"menu_item": menu_item.id, "quantity": quantity},
            format="json",
        )

    def test_get_current_cart_creates_one_active_cart_for_customer(self):
        self.authenticate(self.customer)

        first_response = self.client.get(reverse("orders:cart-current"))
        second_response = self.client.get(reverse("orders:cart-current"))

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(first_response.data["id"], second_response.data["id"])
        self.assertEqual(
            Cart.objects.filter(
                customer=self.customer.customer_profile,
                is_active=True,
            ).count(),
            1,
        )

    def test_only_customers_can_access_cart_apis(self):
        anonymous_response = self.client.get(reverse("orders:cart-current"))
        self.authenticate(self.owner)
        owner_response = self.client.get(reverse("orders:cart-current"))

        self.assertEqual(anonymous_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(owner_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_to_cart_calculates_totals(self):
        self.authenticate(self.customer)

        response = self.add_to_cart(quantity=2)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(response.data["items"][0]["quantity"], 2)
        self.assertEqual(response.data["items"][0]["unit_price"], "200.00")
        self.assertEqual(response.data["items"][0]["effective_price"], "150.00")
        self.assertEqual(response.data["items"][0]["discount_amount"], "100.00")
        self.assertEqual(response.data["items"][0]["subtotal"], "300.00")
        self.assertEqual(response.data["subtotal"], "400.00")
        self.assertEqual(response.data["discount_amount"], "100.00")
        self.assertEqual(response.data["total_payable"], "300.00")
        self.assertEqual(response.data["restaurant"], self.restaurant.id)

    def test_add_same_item_increments_quantity(self):
        self.authenticate(self.customer)

        self.add_to_cart(quantity=1)
        response = self.add_to_cart(quantity=3)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(response.data["items"][0]["quantity"], 4)

    def test_update_quantity_recalculates_totals(self):
        self.authenticate(self.customer)
        add_response = self.add_to_cart(quantity=1)
        item_id = add_response.data["items"][0]["id"]

        response = self.client.patch(
            reverse("orders:cart-update-quantity"),
            {"item_id": item_id, "quantity": 3},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["items"][0]["quantity"], 3)
        self.assertEqual(response.data["subtotal"], "600.00")
        self.assertEqual(response.data["discount_amount"], "150.00")
        self.assertEqual(response.data["total_payable"], "450.00")

    def test_remove_item_and_clear_cart(self):
        self.authenticate(self.customer)
        first_response = self.add_to_cart(self.menu_item, quantity=1)
        self.add_to_cart(self.full_price_item, quantity=1)
        item_id = first_response.data["items"][0]["id"]

        remove_response = self.client.delete(
            reverse("orders:cart-remove-item"),
            {"item_id": item_id},
            format="json",
        )
        clear_response = self.client.post(reverse("orders:cart-clear"))

        self.assertEqual(remove_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(remove_response.data["items"]), 1)
        self.assertEqual(remove_response.data["restaurant"], self.restaurant.id)
        self.assertEqual(clear_response.status_code, status.HTTP_200_OK)
        self.assertEqual(clear_response.data["items"], [])
        self.assertIsNone(clear_response.data["restaurant"])
        self.assertEqual(clear_response.data["total_payable"], "0.00")

    def test_cart_rejects_unavailable_out_of_stock_and_unapproved_items(self):
        self.authenticate(self.customer)

        unavailable_response = self.add_to_cart(self.unavailable_item)
        out_of_stock_response = self.add_to_cart(self.out_of_stock_item)
        pending_response = self.add_to_cart(self.pending_restaurant_item)

        self.assertEqual(unavailable_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(out_of_stock_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(pending_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cart_rejects_items_from_multiple_restaurants(self):
        self.authenticate(self.customer)

        first_response = self.add_to_cart(self.menu_item)
        second_response = self.add_to_cart(self.other_restaurant_item)

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("menu_item", second_response.data)

    def test_customers_have_separate_active_carts(self):
        self.authenticate(self.customer)
        first_response = self.add_to_cart(self.menu_item)

        self.authenticate(self.other_customer)
        second_response = self.add_to_cart(self.menu_item)

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(first_response.data["id"], second_response.data["id"])
        self.assertEqual(Cart.objects.filter(is_active=True).count(), 2)

    def test_update_and_remove_reject_unknown_cart_items(self):
        self.authenticate(self.customer)

        update_response = self.client.patch(
            reverse("orders:cart-update-quantity"),
            {"item_id": 9999, "quantity": 2},
            format="json",
        )
        remove_response = self.client.delete(
            reverse("orders:cart-remove-item"),
            {"item_id": 9999},
            format="json",
        )

        self.assertEqual(update_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(remove_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_database_enforces_single_menu_item_per_cart(self):
        self.authenticate(self.customer)
        self.add_to_cart(self.menu_item)
        cart = Cart.objects.get(customer=self.customer.customer_profile)

        self.assertEqual(CartItem.objects.filter(cart=cart, menu_item=self.menu_item).count(), 1)
