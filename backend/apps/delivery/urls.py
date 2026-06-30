from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DeliveryAssignmentViewSet, DeliveryEarningsViewSet, DeliveryTrackingViewSet


app_name = "delivery"

router = DefaultRouter()
router.register("assignments", DeliveryAssignmentViewSet, basename="assignment")
router.register("earnings", DeliveryEarningsViewSet, basename="earnings")
router.register("tracking", DeliveryTrackingViewSet, basename="tracking")

urlpatterns = [
    path("", include(router.urls)),
]
