from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MenuItemReviewViewSet, RestaurantReviewViewSet, ReviewLikeViewSet


app_name = "reviews"

router = DefaultRouter()
router.register("restaurants", RestaurantReviewViewSet, basename="restaurant-review")
router.register("menu-items", MenuItemReviewViewSet, basename="menu-item-review")
router.register("likes", ReviewLikeViewSet, basename="review-like")

urlpatterns = [
    path("", include(router.urls)),
]
