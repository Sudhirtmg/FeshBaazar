# apps/orders/api/views/order_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from apps.orders.models import Order
from apps.orders.api.serializers.order_serializers import (
    OrderSerializer, CheckoutSerializer, StatusUpdateSerializer
)
from apps.orders.api.services.checkout_service import place_order, CheckoutError
from apps.orders.api.services.status_service import advance_order_status, StatusTransitionError
from apps.common.permissions import IsShopOwner


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            orders = place_order(request.user, serializer.validated_data)
        except CheckoutError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            OrderSerializer(orders, many=True).data,
            status=status.HTTP_201_CREATED,
        )


class CustomerOrderListView(generics.ListAPIView):
    serializer_class   = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            customer=self.request.user
        ).prefetch_related("items", "history").order_by("-created_at")


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class   = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_shop_owner():
            return Order.objects.filter(shop__owner=user)
        return Order.objects.filter(customer=user)


class ShopOrderListView(generics.ListAPIView):
    serializer_class   = OrderSerializer
    permission_classes = [IsAuthenticated, IsShopOwner]

    def get_queryset(self):
        return Order.objects.filter(
            shop__owner=self.request.user
        ).prefetch_related("items", "history").order_by("-created_at")


class OrderStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            if request.user.is_shop_owner():
                order = Order.objects.get(pk=pk, shop__owner=request.user)
            else:
                order = Order.objects.get(pk=pk, customer=request.user)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = StatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = advance_order_status(
                order,
                serializer.validated_data["status"],
                changed_by=request.user,
                note=serializer.validated_data.get("note", ""),
            )
        except StatusTransitionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data)