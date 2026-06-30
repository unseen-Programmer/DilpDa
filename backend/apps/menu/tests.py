from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.restaurants.models import Restaurant

from .models import FoodCategory, MenuItem


User = get_user_model()


class MenuManagementAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="StrongPass123!",
            role=User.Role.RESTAURANT_OWNER,
        )
        self.other_owner = User.objects.create_user(
            email="other@example.com",
            password="StrongPass123!",
            role=User.Role.RESTAURANT_OWNER,
        )
        self.customer = User.objects.create_user(
            email="customer@example.com",
            password="StrongPass123!",
            role=User.Role.CUSTOMER,
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="StrongPass123!",
        )
        self.restaurant = self.create_restaurant(
            self.owner,
            name="Owner Restaurant",
            status_value=Restaurant.Status.APPROVED,
        )
        self.pending_restaurant = self.create_restaurant(
            self.owner,
            name="Pending Restaurant",
            status_value=Restaurant.Status.PENDING,
        )
        self.other_restaurant = self.create_restaurant(
            self.other_owner,
            name="Other Restaurant",
            status_value=Restaurant.Status.APPROVED,
        )
        self.category = FoodCategory.objects.create(
            restaurant=self.restaurant,
            name="Starters",
            display_order=1,
        )
        self.other_category = FoodCategory.objects.create(
            restaurant=self.other_restaurant,
            name="Mains",
            display_order=1,
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def create_restaurant(
        self,
        owner,
        name="Test Restaurant",
        status_value=Restaurant.Status.APPROVED,
    ):
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

    def menu_payload(self, name="Paneer Tikka", restaurant=None, category=None, **overrides):
        restaurant = restaurant or self.restaurant
        category = category or self.category
        payload = {
            "restaurant": restaurant.id,
            "category": category.id,
            "name": name,
            "description": "Smoky and spicy.",
            "price": "249.00",
            "discount_price": "199.00",
            "food_type": MenuItem.FoodType.VEG,
            "preparation_time": 20,
            "is_available": True,
            "stock_status": MenuItem.StockStatus.IN_STOCK,
            "is_featured": True,
            "display_order": 1,
        }
        payload.update(overrides)
        return payload

    def create_menu_item(
        self,
        name="Paneer Tikka",
        restaurant=None,
        category=None,
        **overrides,
    ):
        data = self.menu_payload(name=name, restaurant=restaurant, category=category)
        data.update(overrides)
        data["restaurant"] = Restaurant.objects.get(id=data["restaurant"])
        data["category"] = FoodCategory.objects.get(id=data["category"])
        return MenuItem.objects.create(**data)

    def result_ids(self, response):
        return [item["id"] for item in response.data["results"]]

    def test_owner_can_create_category_and_menu_item(self):
        self.authenticate(self.owner)

        category_response = self.client.post(
            reverse("menu:food-category-list"),
            {
                "restaurant": self.restaurant.id,
                "name": "Desserts",
                "description": "Sweet dishes.",
                "display_order": 2,
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(category_response.status_code, status.HTTP_201_CREATED)

        item_response = self.client.post(
            reverse("menu:menu-item-list"),
            self.menu_payload(category=FoodCategory.objects.get(name="Desserts")),
            format="json",
        )
        self.assertEqual(item_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MenuItem.objects.count(), 1)

    def test_customer_cannot_create_menu_item(self):
        self.authenticate(self.customer)

        response = self.client.post(
            reverse("menu:menu-item-list"),
            self.menu_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_cannot_create_or_update_other_owner_category(self):
        self.authenticate(self.owner)

        create_response = self.client.post(
            reverse("menu:food-category-list"),
            {
                "restaurant": self.other_restaurant.id,
                "name": "Unauthorized",
                "display_order": 1,
            },
            format="json",
        )
        update_response = self.client.patch(
            reverse("menu:food-category-detail", args=(self.other_category.id,)),
            {"name": "Changed"},
            format="json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(update_response.status_code, status.HTTP_404_NOT_FOUND)
        self.other_category.refresh_from_db()
        self.assertEqual(self.other_category.name, "Mains")

    def test_duplicate_category_names_are_rejected_within_same_restaurant(self):
        self.authenticate(self.owner)

        duplicate_response = self.client.post(
            reverse("menu:food-category-list"),
            {
                "restaurant": self.restaurant.id,
                "name": "starters",
                "display_order": 2,
            },
            format="json",
        )

        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", duplicate_response.data)

    def test_owner_cannot_manage_other_owner_menu_item(self):
        item = self.create_menu_item(
            name="Other Curry",
            restaurant=self.other_restaurant,
            category=self.other_category,
        )
        self.authenticate(self.owner)

        update_response = self.client.patch(
            reverse("menu:menu-item-detail", args=(item.id,)),
            {"name": "Changed"},
            format="json",
        )
        delete_response = self.client.delete(
            reverse("menu:menu-item-detail", args=(item.id,)),
        )

        self.assertEqual(update_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(delete_response.status_code, status.HTTP_404_NOT_FOUND)
        item.refresh_from_db()
        self.assertEqual(item.name, "Other Curry")

    def test_owner_can_update_and_delete_owned_menu_item(self):
        item = self.create_menu_item()
        self.authenticate(self.owner)

        update_response = self.client.patch(
            reverse("menu:menu-item-detail", args=(item.id,)),
            {"price": "299.00", "is_available": False},
            format="json",
        )
        delete_response = self.client.delete(
            reverse("menu:menu-item-detail", args=(item.id,)),
        )

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["price"], "299.00")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(MenuItem.objects.filter(id=item.id).exists())

    def test_public_only_sees_menu_items_from_approved_restaurants(self):
        approved_item = self.create_menu_item(name="Approved Item")
        pending_category = FoodCategory.objects.create(
            restaurant=self.pending_restaurant,
            name="Pending Starters",
        )
        pending_item = self.create_menu_item(
            name="Pending Item",
            restaurant=self.pending_restaurant,
            category=pending_category,
        )

        list_response = self.client.get(reverse("menu:menu-item-list"))
        pending_detail_response = self.client.get(
            reverse("menu:menu-item-detail", args=(pending_item.id,)),
        )
        approved_detail_response = self.client.get(
            reverse("menu:menu-item-detail", args=(approved_item.id,)),
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.result_ids(list_response), [approved_item.id])
        self.assertEqual(pending_detail_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(approved_detail_response.status_code, status.HTTP_200_OK)

        self.authenticate(self.customer)
        customer_list_response = self.client.get(reverse("menu:menu-item-list"))
        customer_pending_detail_response = self.client.get(
            reverse("menu:menu-item-detail", args=(pending_item.id,)),
        )

        self.assertEqual(customer_list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.result_ids(customer_list_response), [approved_item.id])
        self.assertEqual(
            customer_pending_detail_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_duplicate_menu_item_names_are_rejected_within_same_restaurant(self):
        self.create_menu_item(name="Masala Dosa")
        self.authenticate(self.owner)

        duplicate_response = self.client.post(
            reverse("menu:menu-item-list"),
            self.menu_payload(name="masala dosa"),
            format="json",
        )
        self.authenticate(self.other_owner)
        other_restaurant_response = self.client.post(
            reverse("menu:menu-item-list"),
            self.menu_payload(
                name="Masala Dosa",
                restaurant=self.other_restaurant,
                category=self.other_category,
            ),
            format="json",
        )

        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", duplicate_response.data)
        self.assertEqual(other_restaurant_response.status_code, status.HTTP_201_CREATED)

    def test_category_must_belong_to_menu_item_restaurant(self):
        self.authenticate(self.owner)

        response = self.client.post(
            reverse("menu:menu-item-list"),
            self.menu_payload(category=self.other_category),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("category", response.data)

    def test_discount_price_must_be_less_than_price(self):
        self.authenticate(self.owner)

        response = self.client.post(
            reverse("menu:menu-item-list"),
            self.menu_payload(discount_price="249.00"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("discount_price", response.data)

    def test_search_filter_ordering_and_pagination(self):
        first = self.create_menu_item(
            name="Zesty Soup",
            price="150.00",
            discount_price="120.00",
            food_type=MenuItem.FoodType.VEGAN,
            display_order=2,
        )
        second = self.create_menu_item(
            name="Aloo Roll",
            price="90.00",
            discount_price="80.00",
            food_type=MenuItem.FoodType.VEG,
            display_order=1,
            is_featured=False,
        )

        response = self.client.get(
            reverse("menu:menu-item-list"),
            {
                "search": "o",
                "food_type": MenuItem.FoodType.VEG,
                "ordering": "price",
                "page_size": 1,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(self.result_ids(response), [second.id])
        self.assertNotIn(first.id, self.result_ids(response))

    def test_category_list_is_paginated_and_limited_to_approved_restaurants(self):
        pending_category = FoodCategory.objects.create(
            restaurant=self.pending_restaurant,
            name="Hidden",
        )

        response = self.client.get(reverse("menu:food-category-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = self.result_ids(response)
        self.assertIn(self.category.id, ids)
        self.assertNotIn(pending_category.id, ids)
