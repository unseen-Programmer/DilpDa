from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FoodCategoryViewSet, MenuItemViewSet


app_name = "menu"

router = DefaultRouter()
router.register("categories", FoodCategoryViewSet, basename="food-category")
router.register("items", MenuItemViewSet, basename="menu-item")

urlpatterns = [
    path("", include(router.urls)),
]
