from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AuthenticationAPITests(APITestCase):
    def register_user(self, email, role=User.Role.CUSTOMER):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "email": email,
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
                "first_name": "Test",
                "last_name": "User",
                "phone_number": "9876543210",
                "role": role,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data

    def authenticate(self, access_token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_register_customer_creates_customer_profile(self):
        data = self.register_user("customer@example.com")

        user = User.objects.get(email="customer@example.com")
        self.assertEqual(data["user"]["role"], User.Role.CUSTOMER)
        self.assertTrue(hasattr(user, "customer_profile"))
        self.assertIn("access", data["tokens"])
        self.assertIn("refresh", data["tokens"])

    def test_register_restaurant_owner_creates_owner_profile(self):
        self.register_user(
            "owner@example.com",
            role=User.Role.RESTAURANT_OWNER,
        )

        user = User.objects.get(email="owner@example.com")
        self.assertTrue(hasattr(user, "restaurant_owner_profile"))

    def test_register_delivery_partner_creates_delivery_profile(self):
        self.register_user(
            "delivery@example.com",
            role=User.Role.DELIVERY_PARTNER,
        )

        user = User.objects.get(email="delivery@example.com")
        self.assertTrue(hasattr(user, "delivery_partner_profile"))

    def test_public_admin_registration_is_rejected(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "email": "admin@example.com",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
                "role": User.Role.ADMIN,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email_is_rejected_case_insensitively(self):
        self.register_user("duplicate@example.com")

        response = self.client.post(
            reverse("accounts:register"),
            {
                "email": "Duplicate@Example.com",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
                "role": User.Role.CUSTOMER,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_refresh_logout_and_current_user(self):
        self.register_user("login@example.com")

        login_response = self.client.post(
            reverse("accounts:login"),
            {
                "email": "LOGIN@example.com",
                "password": "StrongPass123!",
            },
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertEqual(login_response.data["user"]["email"], "login@example.com")

        refresh_response = self.client.post(
            reverse("accounts:token-refresh"),
            {"refresh": login_response.data["refresh"]},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

        self.authenticate(login_response.data["access"])
        current_user_response = self.client.get(reverse("accounts:current-user"))
        self.assertEqual(current_user_response.status_code, status.HTTP_200_OK)
        self.assertEqual(current_user_response.data["email"], "login@example.com")

        logout_response = self.client.post(
            reverse("accounts:logout"),
            {"refresh": refresh_response.data["refresh"]},
            format="json",
        )
        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_profile(self):
        data = self.register_user("profile@example.com")
        self.authenticate(data["tokens"]["access"])

        response = self.client.patch(
            reverse("accounts:update-profile"),
            {
                "first_name": "Updated",
                "profile": {
                    "gender": "female",
                },
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Updated")
        self.assertEqual(response.data["profile"]["gender"], "female")

    def test_change_password(self):
        data = self.register_user("password@example.com")
        self.authenticate(data["tokens"]["access"])

        response = self.client.post(
            reverse("accounts:change-password"),
            {
                "current_password": "StrongPass123!",
                "new_password": "NewStrongPass123!",
                "new_password_confirm": "NewStrongPass123!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials()
        old_login_response = self.client.post(
            reverse("accounts:login"),
            {
                "email": "password@example.com",
                "password": "StrongPass123!",
            },
            format="json",
        )
        self.assertEqual(old_login_response.status_code, status.HTTP_401_UNAUTHORIZED)

        new_login_response = self.client.post(
            reverse("accounts:login"),
            {
                "email": "password@example.com",
                "password": "NewStrongPass123!",
            },
            format="json",
        )
        self.assertEqual(new_login_response.status_code, status.HTTP_200_OK)
