from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/restaurants/", include("apps.restaurants.urls")),
    path("api/menu/", include("apps.menu.urls")),
    path("api/orders/", include("apps.orders.urls")),
    path("api/payments/", include("apps.payments.urls")),
    path("api/delivery/", include("apps.delivery.urls")),
    path("api/reviews/", include("apps.reviews.urls")),
    path("api/adminpanel/", include("apps.adminpanel.urls")),
]
