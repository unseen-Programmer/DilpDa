from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Restaurant


User = get_user_model()


class RestaurantAPITests(APITestCase):
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

    def restaurant_payload(self, name="Test Restaurant"):
        return {
            "name": name,
            "description": "A clean test restaurant.",
            "address": "123 Food Street",
            "city": "Kolkata",
            "state": "West Bengal",
            "pincode": "700001",
            "latitude": "22.572600",
            "longitude": "88.363900",
            "contact_number": "9876543210",
            "email": "restaurant@example.com",
            "cuisine_type": "Bengali",
            "opening_time": "09:00:00",
            "closing_time": "22:00:00",
            "gst_number": "19ABCDE1234F1Z5",
            "fssai_number": "12345678901234",
        }

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def create_restaurant(self, owner=None, status_value=Restaurant.Status.PENDING):
        owner = owner or self.owner
        return Restaurant.objects.create(
            owner=owner.restaurant_owner_profile,
            status=status_value,
            **self.restaurant_payload(),
        )

    def test_restaurant_owner_can_create_restaurant(self):
        self.authenticate(self.owner)

        response = self.client.post(
            reverse("restaurants:restaurant-list"),
            self.restaurant_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Restaurant.Status.PENDING)
        self.assertEqual(Restaurant.objects.count(), 1)
        self.assertEqual(
            Restaurant.objects.first().owner,
            self.owner.restaurant_owner_profile,
        )

    def test_customer_cannot_create_restaurant(self):
        self.authenticate(self.customer)

        response = self.client.post(
            reverse("restaurants:restaurant-list"),
            self.restaurant_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_public_list_only_returns_approved_restaurants(self):
        self.create_restaurant(status_value=Restaurant.Status.PENDING)
        approved = self.create_restaurant(
            owner=self.other_owner,
            status_value=Restaurant.Status.APPROVED,
        )

        response = self.client.get(reverse("restaurants:restaurant-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], approved.id)

    def test_public_detail_only_allows_approved_restaurants(self):
        pending = self.create_restaurant(status_value=Restaurant.Status.PENDING)
        approved = self.create_restaurant(
            owner=self.other_owner,
            status_value=Restaurant.Status.APPROVED,
        )

        pending_response = self.client.get(
            reverse("restaurants:restaurant-detail", args=(pending.id,)),
        )
        approved_response = self.client.get(
            reverse("restaurants:restaurant-detail", args=(approved.id,)),
        )

        self.assertEqual(pending_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(approved_response.status_code, status.HTTP_200_OK)
        self.assertEqual(approved_response.data["id"], approved.id)

    def test_owner_my_restaurants_returns_only_owned_restaurants(self):
        owned = self.create_restaurant(owner=self.owner)
        self.create_restaurant(owner=self.other_owner)
        self.authenticate(self.owner)

        response = self.client.get(reverse("restaurants:restaurant-my-restaurants"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], owned.id)

    def test_owner_can_manage_multiple_restaurants(self):
        first = self.create_restaurant(owner=self.owner, status_value=Restaurant.Status.PENDING)
        second = self.create_restaurant(
            owner=self.owner,
            status_value=Restaurant.Status.APPROVED,
        )
        self.authenticate(self.owner)

        response = self.client.get(reverse("restaurants:restaurant-my-restaurants"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            [restaurant["id"] for restaurant in response.data],
            [first.id, second.id],
        )

    def test_owner_cannot_update_other_owner_restaurant(self):
        restaurant = self.create_restaurant(owner=self.other_owner)
        self.authenticate(self.owner)

        response = self.client.patch(
            reverse("restaurants:restaurant-detail", args=(restaurant.id,)),
            {"name": "Hacked Name"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        restaurant.refresh_from_db()
        self.assertNotEqual(restaurant.name, "Hacked Name")

    def test_owner_can_update_owned_restaurant(self):
        restaurant = self.create_restaurant(owner=self.owner)
        self.authenticate(self.owner)

        response = self.client.patch(
            reverse("restaurants:restaurant-detail", args=(restaurant.id,)),
            {"name": "Updated Restaurant"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        restaurant.refresh_from_db()
        self.assertEqual(restaurant.name, "Updated Restaurant")

    def test_owner_can_delete_owned_restaurant(self):
        restaurant = self.create_restaurant(owner=self.owner)
        self.authenticate(self.owner)

        response = self.client.delete(
            reverse("restaurants:restaurant-detail", args=(restaurant.id,)),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Restaurant.objects.filter(id=restaurant.id).exists())

    def test_admin_can_approve_and_reject_restaurant(self):
        restaurant = self.create_restaurant()
        self.authenticate(self.admin)

        approve_response = self.client.post(
            reverse("restaurants:restaurant-approve", args=(restaurant.id,)),
        )
        self.assertEqual(approve_response.status_code, status.HTTP_200_OK)
        restaurant.refresh_from_db()
        self.assertEqual(restaurant.status, Restaurant.Status.APPROVED)

        reject_response = self.client.post(
            reverse("restaurants:restaurant-reject", args=(restaurant.id,)),
        )
        self.assertEqual(reject_response.status_code, status.HTTP_200_OK)
        restaurant.refresh_from_db()
        self.assertEqual(restaurant.status, Restaurant.Status.REJECTED)

    def test_owner_cannot_approve_restaurant(self):
        restaurant = self.create_restaurant()
        self.authenticate(self.owner)

        response = self.client.post(
            reverse("restaurants:restaurant-approve", args=(restaurant.id,)),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
