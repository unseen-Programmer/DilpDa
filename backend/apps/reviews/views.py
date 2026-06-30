from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import User

from . import services
from .models import MenuItemReview, RestaurantReview, ReviewLike
from .permissions import IsAdminRole, IsCustomer, IsReviewActor
from .serializers import (
    MenuItemReviewSerializer,
    RestaurantReviewSerializer,
    ReviewLikeRequestSerializer,
    ReviewLikeSerializer,
)


class RestaurantReviewViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantReviewSerializer
    permission_classes = (IsReviewActor,)

    def get_permissions(self):
        if self.action == "create":
            return (IsCustomer(),)
        if self.action in ("hide", "restore"):
            return (IsAdminRole(),)
        return super().get_permissions()

    def get_queryset(self):
        queryset = RestaurantReview.objects.select_related(
            "restaurant",
            "restaurant__owner",
            "restaurant__owner__user",
            "customer",
            "customer__user",
            "order",
        ).prefetch_related("likes")
        user = self.request.user

        restaurant_id = self.request.query_params.get("restaurant")
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)

        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.RESTAURANT_OWNER:
            return queryset.filter(restaurant__owner__user=user)
        if user.role == User.Role.CUSTOMER:
            return queryset.filter(is_visible=True) | queryset.filter(customer__user=user)
        return queryset.none()

    def perform_destroy(self, instance):
        restaurant = instance.restaurant
        instance.delete()
        services.recalculate_restaurant_rating(restaurant)

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        if request.user.role != User.Role.ADMIN and review.customer.user_id != request.user.id:
            return Response(
                {"detail": "You can only edit your own reviews."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        if request.user.role not in (User.Role.ADMIN, User.Role.CUSTOMER):
            return Response(
                {"detail": "You cannot delete customer reviews."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if request.user.role == User.Role.CUSTOMER and review.customer.user_id != request.user.id:
            return Response(
                {"detail": "You can only delete your own reviews."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=("post",), url_path="hide")
    def hide(self, request, pk=None):
        review = self.get_object()
        review.is_visible = False
        review.save(update_fields=("is_visible", "updated_at"))
        services.recalculate_restaurant_rating(review.restaurant)
        return Response(self.get_serializer(review).data)

    @action(detail=True, methods=("post",), url_path="restore")
    def restore(self, request, pk=None):
        review = self.get_object()
        review.is_visible = True
        review.save(update_fields=("is_visible", "updated_at"))
        services.recalculate_restaurant_rating(review.restaurant)
        return Response(self.get_serializer(review).data)


class MenuItemReviewViewSet(viewsets.ModelViewSet):
    serializer_class = MenuItemReviewSerializer
    permission_classes = (IsReviewActor,)

    def get_permissions(self):
        if self.action == "create":
            return (IsCustomer(),)
        if self.action in ("hide", "restore"):
            return (IsAdminRole(),)
        return super().get_permissions()

    def get_queryset(self):
        queryset = MenuItemReview.objects.select_related(
            "menu_item",
            "menu_item__restaurant",
            "menu_item__restaurant__owner",
            "menu_item__restaurant__owner__user",
            "customer",
            "customer__user",
            "order",
        ).prefetch_related("likes")
        user = self.request.user

        menu_item_id = self.request.query_params.get("menu_item")
        if menu_item_id:
            queryset = queryset.filter(menu_item_id=menu_item_id)

        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.RESTAURANT_OWNER:
            return queryset.filter(menu_item__restaurant__owner__user=user)
        if user.role == User.Role.CUSTOMER:
            return queryset.filter(is_visible=True) | queryset.filter(customer__user=user)
        return queryset.none()

    def perform_destroy(self, instance):
        menu_item = instance.menu_item
        instance.delete()
        services.recalculate_menu_item_rating(menu_item)

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        if request.user.role != User.Role.ADMIN and review.customer.user_id != request.user.id:
            return Response(
                {"detail": "You can only edit your own reviews."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        if request.user.role not in (User.Role.ADMIN, User.Role.CUSTOMER):
            return Response(
                {"detail": "You cannot delete customer reviews."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if request.user.role == User.Role.CUSTOMER and review.customer.user_id != request.user.id:
            return Response(
                {"detail": "You can only delete your own reviews."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=("post",), url_path="hide")
    def hide(self, request, pk=None):
        review = self.get_object()
        review.is_visible = False
        review.save(update_fields=("is_visible", "updated_at"))
        services.recalculate_menu_item_rating(review.menu_item)
        return Response(self.get_serializer(review).data)

    @action(detail=True, methods=("post",), url_path="restore")
    def restore(self, request, pk=None):
        review = self.get_object()
        review.is_visible = True
        review.save(update_fields=("is_visible", "updated_at"))
        services.recalculate_menu_item_rating(review.menu_item)
        return Response(self.get_serializer(review).data)


class ReviewLikeViewSet(viewsets.GenericViewSet):
    serializer_class = ReviewLikeSerializer
    permission_classes = (IsReviewActor,)

    def get_queryset(self):
        return ReviewLike.objects.filter(user=self.request.user)

    @action(detail=False, methods=("post",), permission_classes=(IsReviewActor,), url_path="like")
    def like(self, request):
        serializer = ReviewLikeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        like, _ = ReviewLike.objects.get_or_create(
            user=request.user,
            restaurant_review=serializer.validated_data.get("restaurant_review"),
            menu_item_review=serializer.validated_data.get("menu_item_review"),
        )
        return Response(ReviewLikeSerializer(like).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=("post",), permission_classes=(IsReviewActor,), url_path="unlike")
    def unlike(self, request):
        serializer = ReviewLikeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        deleted, _ = ReviewLike.objects.filter(
            user=request.user,
            restaurant_review=serializer.validated_data.get("restaurant_review"),
            menu_item_review=serializer.validated_data.get("menu_item_review"),
        ).delete()
        return Response({"removed": bool(deleted)})
