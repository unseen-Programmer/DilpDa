from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import User

from . import services
from .models import DeliveryAssignment, DeliveryEarnings, DeliveryTracking
from .permissions import IsAdminRole, IsDeliveryActor, IsDeliveryPartnerRole
from .serializers import (
    AssignDeliverySerializer,
    DeliveryAssignmentSerializer,
    DeliveryDecisionSerializer,
    DeliveryEarningsSerializer,
    DeliveryTrackingSerializer,
    ReassignDeliverySerializer,
    TrackingUpdateSerializer,
    UpdateDeliveryStatusSerializer,
)


class DeliveryAssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DeliveryAssignmentSerializer
    permission_classes = (IsDeliveryActor,)

    def get_queryset(self):
        queryset = DeliveryAssignment.objects.select_related(
            "order",
            "order__customer",
            "order__customer__user",
            "order__restaurant",
            "order__restaurant__owner",
            "order__restaurant__owner__user",
            "delivery_partner",
            "delivery_partner__user",
            "assigned_by",
        ).prefetch_related("tracking_updates")
        user = self.request.user

        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.DELIVERY_PARTNER:
            return queryset.filter(delivery_partner__user=user)
        if user.role == User.Role.CUSTOMER:
            return queryset.filter(order__customer__user=user)
        if user.role == User.Role.RESTAURANT_OWNER:
            return queryset.filter(order__restaurant__owner__user=user)
        return queryset.none()

    @action(detail=False, methods=("post",), permission_classes=(IsAdminRole,), url_path="assign")
    def assign(self, request):
        serializer = AssignDeliverySerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        assignment = serializer.save()
        return Response(self.get_serializer(assignment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=("post",), permission_classes=(IsAdminRole,), url_path="reassign")
    def reassign(self, request, pk=None):
        assignment = self.get_object()
        serializer = ReassignDeliverySerializer(
            data=request.data,
            context={"request": request, "assignment": assignment},
        )
        serializer.is_valid(raise_exception=True)
        assignment = serializer.save()
        return Response(self.get_serializer(assignment).data)

    @action(detail=False, methods=("get",), permission_classes=(IsAdminRole,), url_path="all")
    def all_deliveries(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=("get",),
        permission_classes=(IsDeliveryPartnerRole,),
        url_path="assigned",
    )
    def assigned(self, request):
        queryset = self.get_queryset().exclude(
            status__in=(
                DeliveryAssignment.Status.DELIVERED,
                DeliveryAssignment.Status.CANCELLED,
            )
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=("get",),
        permission_classes=(IsDeliveryPartnerRole,),
        url_path="history",
    )
    def history(self, request):
        queryset = self.get_queryset().filter(
            status__in=(
                DeliveryAssignment.Status.DELIVERED,
                DeliveryAssignment.Status.CANCELLED,
            )
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=("post",),
        permission_classes=(IsDeliveryPartnerRole,),
        url_path="accept",
    )
    def accept(self, request, pk=None):
        assignment = self.get_object()
        serializer = DeliveryDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignment = services.update_delivery_status(
            assignment,
            DeliveryAssignment.Status.ACCEPTED,
            serializer.validated_data.get("delivery_notes", ""),
        )
        return Response(self.get_serializer(assignment).data)

    @action(
        detail=True,
        methods=("post",),
        permission_classes=(IsDeliveryPartnerRole,),
        url_path="reject",
    )
    def reject(self, request, pk=None):
        assignment = self.get_object()
        serializer = DeliveryDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignment = services.reject_delivery(
            assignment,
            serializer.validated_data.get("delivery_notes", ""),
        )
        return Response(self.get_serializer(assignment).data)

    @action(
        detail=True,
        methods=("patch",),
        permission_classes=(IsDeliveryPartnerRole,),
        url_path="update-status",
    )
    def update_status(self, request, pk=None):
        assignment = self.get_object()
        serializer = UpdateDeliveryStatusSerializer(
            data=request.data,
            context={"assignment": assignment},
        )
        serializer.is_valid(raise_exception=True)
        assignment = serializer.save()
        return Response(self.get_serializer(assignment).data)

    @action(
        detail=True,
        methods=("post",),
        permission_classes=(IsDeliveryPartnerRole,),
        url_path="tracking",
    )
    def add_tracking(self, request, pk=None):
        assignment = self.get_object()
        serializer = TrackingUpdateSerializer(
            data=request.data,
            context={"assignment": assignment},
        )
        serializer.is_valid(raise_exception=True)
        tracking = serializer.save()
        return Response(DeliveryTrackingSerializer(tracking).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=("get",), url_path="track")
    def track(self, request):
        order_id = request.query_params.get("order")
        if not order_id:
            return Response(
                {"detail": "order query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        assignment = self.get_queryset().filter(order_id=order_id).first()
        if assignment is None:
            return Response(
                {"detail": "Delivery assignment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(self.get_serializer(assignment).data)


class DeliveryEarningsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DeliveryEarningsSerializer
    permission_classes = (IsDeliveryActor,)

    def get_queryset(self):
        queryset = DeliveryEarnings.objects.select_related(
            "delivery_partner",
            "delivery_partner__user",
            "order",
            "order__restaurant",
        )
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.DELIVERY_PARTNER:
            return queryset.filter(delivery_partner__user=user)
        return queryset.none()


class DeliveryTrackingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DeliveryTrackingSerializer
    permission_classes = (IsDeliveryActor,)

    def get_queryset(self):
        queryset = DeliveryTracking.objects.select_related(
            "delivery_assignment",
            "delivery_assignment__order",
            "delivery_assignment__order__customer",
            "delivery_assignment__order__customer__user",
            "delivery_assignment__order__restaurant",
            "delivery_assignment__order__restaurant__owner",
            "delivery_assignment__order__restaurant__owner__user",
            "delivery_assignment__delivery_partner",
            "delivery_assignment__delivery_partner__user",
        )
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.DELIVERY_PARTNER:
            return queryset.filter(delivery_assignment__delivery_partner__user=user)
        if user.role == User.Role.CUSTOMER:
            return queryset.filter(delivery_assignment__order__customer__user=user)
        if user.role == User.Role.RESTAURANT_OWNER:
            return queryset.filter(delivery_assignment__order__restaurant__owner__user=user)
        return queryset.none()
