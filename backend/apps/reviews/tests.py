from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.menu.models import FoodCategory, MenuItem
from apps.orders.models import Order, OrderItem
from apps.restaurants.models import Restaurant

from .models import MenuItemReview, RestaurantReview, ReviewLike


User = get_user_model()


class ReviewsAndRatingsTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email="review-customer@example.com",
            password="StrongPass123!",
            role=User.Role.CUSTOMER,
        )
        self.other_customer = User.objects.create_user(
            email="review-other-customer@example.com",
            password="StrongPass123!",
            role=User.Role.CUSTOMER,
        )
        self.owner = User.objects.create_user(
            email="review-owner@example.com",
            password="StrongPass123!",
            role=User.Role.RESTAURANT_OWNER,
        )
        self.other_owner = User.objects.create_user(
            email="review-other-owner@example.com",
            password="StrongPass123!",
            role=User.Role.RESTAURANT_OWNER,
        )
        self.admin = User.objects.create_superuser(
            email="review-admin@example.com",
            password="StrongPass123!",
        )
        self.restaurant = self.create_restaurant(self.owner, "Review Restaurant")
        self.other_restaurant = self.create_restaurant(
            self.other_owner,
            "Other Review Restaurant",
        )
        self.category = FoodCategory.objects.create(
            restaurant=self.restaurant,
            name="Reviews",
        )
        self.menu_item = self.create_menu_item("Review Paneer")
        self.unpurchased_item = self.create_menu_item("Review Soup")
        self.order = self.create_order(
            self.customer,
            self.restaurant,
            Order.OrderStatus.DELIVERED,
        )
        self.pending_order = self.create_order(
            self.customer,
            self.restaurant,
            Order.OrderStatus.CONFIRMED,
        )
        self.other_order = self.create_order(
            self.other_customer,
            self.restaurant,
            Order.OrderStatus.DELIVERED,
        )
        OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item,
            menu_item_name=self.menu_item.name,
            quantity=1,
            unit_price="200.00",
            subtotal="200.00",
        )
        OrderItem.objects.create(
            order=self.other_order,
            menu_item=self.menu_item,
            menu_item_name=self.menu_item.name,
            quantity=1,
            unit_price="200.00",
            subtotal="200.00",
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

    def create_menu_item(self, name):
        return MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name=name,
            price="200.00",
            food_type=MenuItem.FoodType.VEG,
            preparation_time=20,
        )

    def create_order(self, customer, restaurant, order_status):
        return Order.objects.create(
            customer=customer.customer_profile,
            restaurant=restaurant,
            delivery_address="123 Delivery Lane",
            payment_method=Order.PaymentMethod.COD,
            payment_status=Order.PaymentStatus.PAID,
            order_status=order_status,
            subtotal="200.00",
            discount="0.00",
            delivery_charge="0.00",
            grand_total="200.00",
        )

    def create_restaurant_review(self, rating=5, order=None):
        self.authenticate(self.customer)
        return self.client.post(
            reverse("reviews:restaurant-review-list"),
            {
                "restaurant": self.restaurant.id,
                "order": (order or self.order).id,
                "rating": rating,
                "review_text": "Excellent food.",
            },
            format="json",
        )

    def create_menu_review(self, rating=4, menu_item=None, order=None):
        self.authenticate(self.customer)
        return self.client.post(
            reverse("reviews:menu-item-review-list"),
            {
                "menu_item": (menu_item or self.menu_item).id,
                "order": (order or self.order).id,
                "rating": rating,
                "review_text": "Loved it.",
            },
            format="json",
        )

    def test_customer_can_review_delivered_order_and_restaurant_rating_updates(self):
        response = self.create_restaurant_review(rating=5)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.rating, 5)
        self.assertEqual(self.restaurant.total_reviews, 1)

    def test_restaurant_review_requires_delivered_own_order_and_prevents_duplicates(self):
        pending_response = self.create_restaurant_review(order=self.pending_order)
        self.create_restaurant_review()
        duplicate_response = self.create_restaurant_review()

        self.authenticate(self.other_customer)
        other_customer_response = self.client.post(
            reverse("reviews:restaurant-review-list"),
            {
                "restaurant": self.restaurant.id,
                "order": self.order.id,
                "rating": 4,
            },
            format="json",
        )

        self.assertEqual(pending_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(other_customer_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_menu_review_requires_purchased_item_and_updates_rating(self):
        response = self.create_menu_review(rating=4)
        unpurchased_response = self.create_menu_review(menu_item=self.unpurchased_item)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(unpurchased_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.menu_item.refresh_from_db()
        self.assertEqual(self.menu_item.rating, 4)
        self.assertEqual(self.menu_item.total_reviews, 1)

    def test_duplicate_menu_review_is_rejected(self):
        self.create_menu_review()
        response = self.create_menu_review()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_can_edit_and_delete_own_restaurant_review(self):
        create_response = self.create_restaurant_review(rating=5)
        review_id = create_response.data["id"]

        patch_response = self.client.patch(
            reverse("reviews:restaurant-review-detail", args=(review_id,)),
            {"rating": 3, "review_text": "Updated."},
            format="json",
        )
        self.restaurant.refresh_from_db()
        rating_after_patch = self.restaurant.rating
        delete_response = self.client.delete(
            reverse("reviews:restaurant-review-detail", args=(review_id,)),
        )
        self.restaurant.refresh_from_db()

        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertTrue(patch_response.data["is_edited"])
        self.assertEqual(rating_after_patch, 3)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.restaurant.rating, 0)
        self.assertEqual(self.restaurant.total_reviews, 0)

    def test_customer_cannot_edit_other_customer_review(self):
        self.authenticate(self.other_customer)
        other_review = RestaurantReview.objects.create(
            restaurant=self.restaurant,
            customer=self.other_customer.customer_profile,
            order=self.other_order,
            rating=4,
        )
        self.authenticate(self.customer)

        response = self.client.patch(
            reverse("reviews:restaurant-review-detail", args=(other_review.id,)),
            {"rating": 2},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_restaurant_owner_can_view_but_not_modify_reviews(self):
        create_response = self.create_restaurant_review()
        review_id = create_response.data["id"]
        self.authenticate(self.owner)

        list_response = self.client.get(
            reverse("reviews:restaurant-review-list"),
            {"restaurant": self.restaurant.id},
        )
        patch_response = self.client.patch(
            reverse("reviews:restaurant-review-detail", args=(review_id,)),
            {"rating": 1},
            format="json",
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_hide_restore_and_delete_restaurant_review(self):
        create_response = self.create_restaurant_review(rating=5)
        review_id = create_response.data["id"]
        self.authenticate(self.admin)

        hide_response = self.client.post(
            reverse("reviews:restaurant-review-hide", args=(review_id,)),
        )
        self.restaurant.refresh_from_db()
        total_reviews_after_hide = self.restaurant.total_reviews
        restore_response = self.client.post(
            reverse("reviews:restaurant-review-restore", args=(review_id,)),
        )
        self.restaurant.refresh_from_db()
        total_reviews_after_restore = self.restaurant.total_reviews
        delete_response = self.client.delete(
            reverse("reviews:restaurant-review-detail", args=(review_id,)),
        )

        self.assertEqual(hide_response.status_code, status.HTTP_200_OK)
        self.assertEqual(total_reviews_after_hide, 0)
        self.assertEqual(restore_response.status_code, status.HTTP_200_OK)
        self.assertEqual(total_reviews_after_restore, 1)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_menu_review_edit_hide_restore_delete_recalculates_rating(self):
        first_response = self.create_menu_review(rating=5)
        self.authenticate(self.other_customer)
        second_response = self.client.post(
            reverse("reviews:menu-item-review-list"),
            {
                "menu_item": self.menu_item.id,
                "order": self.other_order.id,
                "rating": 3,
            },
            format="json",
        )
        self.assertEqual(second_response.status_code, status.HTTP_201_CREATED)

        self.authenticate(self.customer)
        patch_response = self.client.patch(
            reverse("reviews:menu-item-review-detail", args=(first_response.data["id"],)),
            {"rating": 1},
            format="json",
        )
        self.menu_item.refresh_from_db()
        rating_after_patch = self.menu_item.rating

        self.authenticate(self.admin)
        hide_response = self.client.post(
            reverse("reviews:menu-item-review-hide", args=(second_response.data["id"],)),
        )
        self.menu_item.refresh_from_db()
        rating_after_hide = self.menu_item.rating
        restore_response = self.client.post(
            reverse("reviews:menu-item-review-restore", args=(second_response.data["id"],)),
        )

        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(rating_after_patch, 2)
        self.assertEqual(hide_response.status_code, status.HTTP_200_OK)
        self.assertEqual(rating_after_hide, 1)
        self.assertEqual(restore_response.status_code, status.HTTP_200_OK)

    def test_review_likes_can_be_added_and_removed_without_duplicates(self):
        create_response = self.create_restaurant_review()
        self.authenticate(self.other_customer)

        like_response = self.client.post(
            reverse("reviews:review-like-like"),
            {"restaurant_review": create_response.data["id"]},
            format="json",
        )
        duplicate_response = self.client.post(
            reverse("reviews:review-like-like"),
            {"restaurant_review": create_response.data["id"]},
            format="json",
        )
        likes_after_duplicate = ReviewLike.objects.count()
        unlike_response = self.client.post(
            reverse("reviews:review-like-unlike"),
            {"restaurant_review": create_response.data["id"]},
            format="json",
        )

        self.assertEqual(like_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(duplicate_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(likes_after_duplicate, 1)
        self.assertEqual(unlike_response.status_code, status.HTTP_200_OK)
        self.assertEqual(ReviewLike.objects.count(), 0)

    def test_rating_validation_rejects_out_of_range_values(self):
        self.authenticate(self.customer)
        response = self.client.post(
            reverse("reviews:restaurant-review-list"),
            {
                "restaurant": self.restaurant.id,
                "order": self.order.id,
                "rating": 6,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
