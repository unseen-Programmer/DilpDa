from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.orders.models import Order
from apps.restaurants.models import Restaurant

from .models import DeliveryAssignment, DeliveryEarnings, DeliveryTracking


User = get_user_model()


class DeliveryManagementTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email="delivery-customer@example.com",
            password="StrongPass123!",
            role=User.Role.CUSTOMER,
        )
        self.other_customer = User.objects.create_user(
            email="other-delivery-customer@example.com",
            password="StrongPass123!",
            role=User.Role.CUSTOMER,
        )
        self.owner = User.objects.create_user(
            email="delivery-owner@example.com",
            password="StrongPass123!",
            role=User.Role.RESTAURANT_OWNER,
        )
        self.other_owner = User.objects.create_user(
            email="other-delivery-owner@example.com",
            password="StrongPass123!",
            role=User.Role.RESTAURANT_OWNER,
        )
        self.partner = User.objects.create_user(
            email="partner@example.com",
            password="StrongPass123!",
            role=User.Role.DELIVERY_PARTNER,
        )
        self.other_partner = User.objects.create_user(
            email="other-partner@example.com",
            password="StrongPass123!",
            role=User.Role.DELIVERY_PARTNER,
        )
        self.admin = User.objects.create_superuser(
            email="delivery-admin@example.com",
            password="StrongPass123!",
        )
        self.restaurant = self.create_restaurant(self.owner, "Delivery Restaurant")
        self.other_restaurant = self.create_restaurant(
            self.other_owner,
            "Other Delivery Restaurant",
        )
        self.order = self.create_order(self.customer, self.restaurant)
        self.other_order = self.create_order(self.other_customer, self.other_restaurant)

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

    def create_order(self, customer, restaurant, status_value=Order.OrderStatus.CONFIRMED):
        return Order.objects.create(
            customer=customer.customer_profile,
            restaurant=restaurant,
            delivery_address="123 Delivery Lane",
            payment_method=Order.PaymentMethod.COD,
            payment_status=Order.PaymentStatus.PAID,
            order_status=status_value,
            subtotal="500.00",
            discount="0.00",
            delivery_charge="50.00",
            grand_total="550.00",
        )

    def assign_delivery(self, order=None, partner=None):
        self.authenticate(self.admin)
        return self.client.post(
            reverse("delivery:assignment-assign"),
            {
                "order": (order or self.order).id,
                "delivery_partner": (partner or self.partner).delivery_partner_profile.id,
                "delivery_notes": "Handle carefully.",
            },
            format="json",
        )

    def test_admin_can_assign_and_reassign_delivery_partner(self):
        assign_response = self.assign_delivery()
        assignment_id = assign_response.data["id"]

        reassign_response = self.client.post(
            reverse("delivery:assignment-reassign", args=(assignment_id,)),
            {
                "delivery_partner": self.other_partner.delivery_partner_profile.id,
                "delivery_notes": "Reassigned.",
            },
            format="json",
        )

        self.assertEqual(assign_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(assign_response.data["status"], DeliveryAssignment.Status.ASSIGNED)
        self.assertEqual(assign_response.data["assigned_by"], self.admin.id)
        self.assertEqual(reassign_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            reassign_response.data["delivery_partner"],
            self.other_partner.delivery_partner_profile.id,
        )

    def test_only_admin_can_assign_delivery(self):
        self.authenticate(self.owner)
        owner_response = self.client.post(
            reverse("delivery:assignment-assign"),
            {
                "order": self.order.id,
                "delivery_partner": self.partner.delivery_partner_profile.id,
            },
            format="json",
        )
        self.authenticate(self.partner)
        partner_response = self.client.post(
            reverse("delivery:assignment-assign"),
            {
                "order": self.order.id,
                "delivery_partner": self.partner.delivery_partner_profile.id,
            },
            format="json",
        )

        self.assertEqual(owner_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(partner_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assignment_requires_confirmed_order_and_one_active_assignment(self):
        placed_order = self.create_order(
            self.customer,
            self.restaurant,
            status_value=Order.OrderStatus.PLACED,
        )
        invalid_response = self.assign_delivery(order=placed_order)
        valid_response = self.assign_delivery()
        duplicate_response = self.assign_delivery()

        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(valid_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delivery_partner_can_accept_and_progress_delivery(self):
        assignment_id = self.assign_delivery().data["id"]
        self.authenticate(self.partner)

        accept_response = self.client.post(
            reverse("delivery:assignment-accept", args=(assignment_id,)),
        )
        picked_up_response = self.client.patch(
            reverse("delivery:assignment-update-status", args=(assignment_id,)),
            {"status": DeliveryAssignment.Status.PICKED_UP},
            format="json",
        )
        out_response = self.client.patch(
            reverse("delivery:assignment-update-status", args=(assignment_id,)),
            {"status": DeliveryAssignment.Status.OUT_FOR_DELIVERY},
            format="json",
        )
        delivered_response = self.client.patch(
            reverse("delivery:assignment-update-status", args=(assignment_id,)),
            {"status": DeliveryAssignment.Status.DELIVERED},
            format="json",
        )

        self.assertEqual(accept_response.status_code, status.HTTP_200_OK)
        self.assertEqual(accept_response.data["status"], DeliveryAssignment.Status.ACCEPTED)
        self.assertEqual(picked_up_response.data["status"], DeliveryAssignment.Status.PICKED_UP)
        self.assertEqual(out_response.data["status"], DeliveryAssignment.Status.OUT_FOR_DELIVERY)
        self.assertEqual(delivered_response.data["status"], DeliveryAssignment.Status.DELIVERED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.order_status, Order.OrderStatus.DELIVERED)
        self.assertTrue(
            DeliveryEarnings.objects.filter(
                order=self.order,
                delivery_partner=self.partner.delivery_partner_profile,
            ).exists()
        )
        earnings = DeliveryEarnings.objects.get(order=self.order)
        self.assertEqual(earnings.delivery_fee, self.order.delivery_charge)
        self.assertEqual(earnings.total_earnings, self.order.delivery_charge)

    def test_invalid_workflow_transition_is_rejected(self):
        assignment_id = self.assign_delivery().data["id"]
        self.authenticate(self.partner)

        response = self.client.patch(
            reverse("delivery:assignment-update-status", args=(assignment_id,)),
            {"status": DeliveryAssignment.Status.DELIVERED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        assignment = DeliveryAssignment.objects.get(id=assignment_id)
        self.assertEqual(assignment.status, DeliveryAssignment.Status.ASSIGNED)

    def test_delivery_partner_can_reject_assigned_delivery(self):
        assignment_id = self.assign_delivery().data["id"]
        self.authenticate(self.partner)

        response = self.client.post(
            reverse("delivery:assignment-reject", args=(assignment_id,)),
            {"delivery_notes": "Vehicle issue."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], DeliveryAssignment.Status.CANCELLED)
        self.assertIn("Vehicle issue.", response.data["delivery_notes"])

    def test_delivery_partner_cannot_access_other_partner_assignment(self):
        assignment_id = self.assign_delivery().data["id"]
        self.authenticate(self.other_partner)

        detail_response = self.client.get(
            reverse("delivery:assignment-detail", args=(assignment_id,)),
        )
        accept_response = self.client.post(
            reverse("delivery:assignment-accept", args=(assignment_id,)),
        )

        self.assertEqual(detail_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(accept_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_and_owner_can_only_view_their_own_delivery_status(self):
        assignment_id = self.assign_delivery().data["id"]
        other_assignment_id = self.assign_delivery(
            order=self.other_order,
            partner=self.other_partner,
        ).data["id"]

        self.authenticate(self.customer)
        own_track_response = self.client.get(
            reverse("delivery:assignment-track"),
            {"order": self.order.id},
        )
        other_track_response = self.client.get(
            reverse("delivery:assignment-track"),
            {"order": self.other_order.id},
        )

        self.authenticate(self.owner)
        owner_detail_response = self.client.get(
            reverse("delivery:assignment-detail", args=(assignment_id,)),
        )
        other_owner_detail_response = self.client.get(
            reverse("delivery:assignment-detail", args=(other_assignment_id,)),
        )

        self.assertEqual(own_track_response.status_code, status.HTTP_200_OK)
        self.assertEqual(other_track_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(owner_detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(other_owner_detail_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tracking_updates_are_created_and_visible_to_allowed_roles(self):
        assignment_id = self.assign_delivery().data["id"]
        self.authenticate(self.partner)
        tracking_response = self.client.post(
            reverse("delivery:assignment-add-tracking", args=(assignment_id,)),
            {
                "latitude": "22.572600",
                "longitude": "88.363900",
                "current_location": "Park Street",
            },
            format="json",
        )

        self.authenticate(self.customer)
        track_response = self.client.get(
            reverse("delivery:assignment-track"),
            {"order": self.order.id},
        )

        self.assertEqual(tracking_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DeliveryTracking.objects.count(), 1)
        self.assertEqual(track_response.status_code, status.HTTP_200_OK)
        self.assertEqual(track_response.data["latest_tracking"]["current_location"], "Park Street")

    def test_partner_history_and_earnings(self):
        assignment_id = self.assign_delivery().data["id"]
        self.authenticate(self.partner)
        self.client.post(reverse("delivery:assignment-accept", args=(assignment_id,)))
        self.client.patch(
            reverse("delivery:assignment-update-status", args=(assignment_id,)),
            {"status": DeliveryAssignment.Status.PICKED_UP},
            format="json",
        )
        self.client.patch(
            reverse("delivery:assignment-update-status", args=(assignment_id,)),
            {"status": DeliveryAssignment.Status.OUT_FOR_DELIVERY},
            format="json",
        )
        self.client.patch(
            reverse("delivery:assignment-update-status", args=(assignment_id,)),
            {"status": DeliveryAssignment.Status.DELIVERED},
            format="json",
        )

        history_response = self.client.get(reverse("delivery:assignment-history"))
        earnings_response = self.client.get(reverse("delivery:earnings-list"))

        self.assertEqual(history_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(history_response.data), 1)
        self.assertEqual(earnings_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(earnings_response.data), 1)

    def test_admin_can_view_all_deliveries(self):
        self.assign_delivery()
        self.assign_delivery(order=self.other_order, partner=self.other_partner)
        self.authenticate(self.admin)

        response = self.client.get(reverse("delivery:assignment-all-deliveries"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
