# apps/b2b/api/views/b2b_views.py
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.utils import timezone

from apps.b2b.models import ColdStorage, ColdStorageProduct, B2BOrder, B2BOrderItem, LedgerEntry
from apps.b2b.api.serializers.serializers import (
    ColdStorageListSerializer,
    ColdStoragePrivateSerializer,
    ColdStorageProductSerializer,
    B2BOrderCreateSerializer,
    B2BOrderSerializer,
    SetPriceSerializer,
)
from apps.common.permissions import (
    IsShopOwner,
    IsColdStorage,
    IsShopOwnerOrColdStorage,
    IsColdStorageOrStaff,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _notify_order_update(order):
    """Push a WebSocket update — fails silently if channels is not configured."""
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        if channel_layer is None:
            return

        async_to_sync(channel_layer.group_send)(
            "orders",
            {
                "type": "send_order_update",
                "data": {
                    "id":          order.id,
                    "status":      order.status,
                    "total_price": str(order.total_price) if order.total_price else None,
                },
            },
        )
    except Exception:
        pass  # channels not installed / not configured


def _create_ledger_entry(order, user=None):
    """
    Create a credit LedgerEntry when order.total_price is known.
    Idempotent — skips if an entry already exists for this order.
    """
    if not order.total_price:
        return

    if LedgerEntry.objects.filter(order=order, entry_type="credit").exists():
        return

    total_credit = (
        LedgerEntry.objects.filter(shop=order.shop, entry_type="credit")
        .aggregate(total=Sum("amount"))["total"] or 0
    )
    total_payment = (
        LedgerEntry.objects.filter(shop=order.shop, entry_type="payment")
        .aggregate(total=Sum("amount"))["total"] or 0
    )
    new_balance = total_credit - total_payment + order.total_price

    LedgerEntry.objects.create(
        shop=order.shop,
        cold_storage=order.cold_storage,
        order=order,
        amount=order.total_price,
        entry_type="credit",
        balance_after=new_balance,
        note=f"{order.payment_type.upper()} order #{order.id}",
        weighted_by=user,   # ✅ always saved
    )


def _get_shop_balance(shop):
    credits = (
        LedgerEntry.objects.filter(shop=shop, entry_type="credit")
        .aggregate(total=Sum("amount"))["total"] or 0
    )
    payments = (
        LedgerEntry.objects.filter(shop=shop, entry_type="payment")
        .aggregate(total=Sum("amount"))["total"] or 0
    )
    return credits - payments


# ── Cold Storage public browsing ──────────────────────────────────────────────

class ColdStorageListView(generics.ListAPIView):
    serializer_class   = ColdStorageListSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopOwner]

    def get_queryset(self):
        qs       = ColdStorage.objects.filter(verified=True).prefetch_related("products")
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(products__category=category).distinct()
        return qs


class ColdStorageDetailView(generics.RetrieveAPIView):
    serializer_class   = ColdStorageListSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopOwner]
    queryset           = ColdStorage.objects.filter(verified=True)


# ── Cold Storage owner dashboard ──────────────────────────────────────────────

class MyColdStorageView(generics.RetrieveUpdateAPIView):
    serializer_class   = ColdStoragePrivateSerializer
    permission_classes = [permissions.IsAuthenticated, IsColdStorageOrStaff]

    def get_object(self):
        user  = self.request.user
        owner = user.owner if user.role == "staff" else user
        return get_object_or_404(ColdStorage, owner=owner)


class ColdStorageProductListCreateView(generics.ListCreateAPIView):
    serializer_class   = ColdStorageProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsColdStorageOrStaff]

    def get_queryset(self):
        user  = self.request.user
        owner = user.owner if user.role == "staff" else user
        return ColdStorageProduct.objects.filter(cold_storage__owner=owner)

    def perform_create(self, serializer):
        user  = self.request.user
        owner = user.owner if user.role == "staff" else user
        cold_storage = get_object_or_404(ColdStorage, owner=owner)
        serializer.save(cold_storage=cold_storage)


class ColdStorageProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = ColdStorageProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsColdStorageOrStaff]

    def get_queryset(self):
        user  = self.request.user
        owner = user.owner if user.role == "staff" else user
        return ColdStorageProduct.objects.filter(cold_storage__owner=owner)


# ── B2B Orders ────────────────────────────────────────────────────────────────

class B2BOrderCreateView(generics.CreateAPIView):
    serializer_class   = B2BOrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopOwnerOrColdStorage]

    def perform_create(self, serializer):
        user = self.request.user

        if user.role == "shop_owner":
            cold_storage_id = self.request.data.get("cold_storage")
            cold_storage    = get_object_or_404(ColdStorage, id=cold_storage_id, verified=True)
            order           = serializer.save(cold_storage=cold_storage)

        elif user.role == "cold_storage":
            cold_storage = get_object_or_404(ColdStorage, owner=user)
            order        = serializer.save(cold_storage=cold_storage)

        else:
            raise ValidationError("Invalid role")

        _create_ledger_entry(order, user)

        if (
            order.payment_type == "cash"
            and order.delivery_type == "pickup"
            and user.role == "cold_storage"
        ):
            order.paid_amount = order.total_price or 0
        else:
            order.paid_amount = 0

        order.save(update_fields=["paid_amount"])
        _notify_order_update(order)


class ShopB2BOrderListView(generics.ListAPIView):
    serializer_class   = B2BOrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopOwner]

    def get_queryset(self):
        return (
            B2BOrder.objects.filter(shop__owner=self.request.user)
            .select_related("cold_storage")
            .prefetch_related("items__product")
            .order_by("-created_at")
        )


class ColdStorageIncomingOrderListView(generics.ListAPIView):
    serializer_class   = B2BOrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsColdStorageOrStaff]

    def get_queryset(self):
        user  = self.request.user
        owner = user.owner if user.role == "staff" else user
        return (
            B2BOrder.objects.filter(cold_storage__owner=owner)
            .select_related("shop")
            .prefetch_related("items__product")
            .order_by("-created_at")
        )

    def get(self, request, *args, **kwargs):
        if request.user.role == "staff" and not request.user.can_view_orders:
            return Response({"error": "No permission to view orders"}, status=403)
        return super().get(request, *args, **kwargs)


class B2BOrderDetailView(RetrieveAPIView):
    serializer_class   = B2BOrderSerializer
    permission_classes = [IsAuthenticated, IsColdStorageOrStaff]

    def get_queryset(self):
        user  = self.request.user
        owner = user.owner if user.role == "staff" else user
        return B2BOrder.objects.filter(cold_storage__owner=owner)


class B2BOrderStatusUpdateView(generics.UpdateAPIView):
    serializer_class   = B2BOrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsColdStorageOrStaff]
    http_method_names  = ["patch"]

    def get_queryset(self):
        user  = self.request.user
        owner = user.owner if user.role == "staff" else user
        return B2BOrder.objects.filter(cold_storage__owner=owner)

    def partial_update(self, request, *args, **kwargs):
        if request.user.role == "staff" and not request.user.can_deliver_orders:
            return Response({"error": "No permission"}, status=403)

        order      = self.get_object()
        new_status = request.data.get("status")

        valid_statuses = [s[0] for s in B2BOrder.Status.choices]
        if new_status not in valid_statuses:
            return Response({"error": f"Invalid status. Choices: {valid_statuses}"}, status=400)

        if request.user.role == "staff":
            if new_status not in ["processing", "dispatched", "delivered"]:
                return Response({"error": "Staff can only update delivery status"}, status=403)
        else:
            if not order.can_transition_to(new_status):
                return Response(
                    {"error": f"Cannot transition from '{order.status}' to '{new_status}'."},
                    status=400,
                )

        old_status    = order.status
        order.status  = new_status
        order.save(update_fields=["status"])
        _notify_order_update(order)

        # Restore stock on cancellation
        if new_status == "cancelled" and old_status != "cancelled":
            for item in order.items.all():
                if item.unit_type == "kg":
                    item.product.stock_kg += item.quantity
                    item.product.save(update_fields=["stock_kg"])
                elif item.unit_type == "piece" and item.product.stock_pieces is not None:
                    item.product.stock_pieces += int(item.quantity)
                    item.product.save(update_fields=["stock_pieces"])

        return Response(B2BOrderSerializer(order).data)


class SetPriceView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsColdStorageOrStaff]

    def post(self, request, pk):
        user  = request.user
        owner = user.owner if user.role == "staff" else user

        order = get_object_or_404(B2BOrder, pk=pk, cold_storage__owner=owner)

        if order.status not in [B2BOrder.Status.PENDING_PRICE]:
            return Response(
                {"error": f"Cannot set price on an order with status '{order.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SetPriceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item_id  = serializer.validated_data["item_id"]
        weight   = serializer.validated_data["actual_weight_kg"]
        price_kg = serializer.validated_data["price_per_kg"]

        item = get_object_or_404(B2BOrderItem, pk=item_id, order=order)

        if item.unit_type != "piece":
            return Response(
                {"error": "This item is kg-based and already has a price."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item.actual_weight_kg   = weight
        item.price_per_kg_final = price_kg
        item.line_total         = weight * price_kg
        item.save(update_fields=["actual_weight_kg", "price_per_kg_final", "line_total"])

        # Update weighted_by on any existing credit entry for this order
        LedgerEntry.objects.filter(order=order, entry_type="credit").update(weighted_by=request.user)

        _notify_order_update(order)

        unpriced_count = order.items.filter(unit_type="piece", line_total__isnull=True).count()

        if unpriced_count == 0:
            order.status = B2BOrder.Status.CONFIRMED
            order.save(update_fields=["status"])
            order.recalculate_total()
            order.refresh_from_db()

            _create_ledger_entry(order, request.user)
            _notify_order_update(order)

        return Response(B2BOrderSerializer(order).data, status=status.HTTP_200_OK)


class ShopOrderConfirmView(APIView):
    permission_classes = [IsAuthenticated, IsShopOwner]

    def patch(self, request, pk):
        order = get_object_or_404(B2BOrder, pk=pk, shop__owner=request.user)

        if order.status != B2BOrder.Status.PRICED:
            return Response(
                {"error": "Only priced orders can be confirmed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = B2BOrder.Status.CONFIRMED
        order.save(update_fields=["status"])
        _notify_order_update(order)

        return Response(B2BOrderSerializer(order).data)


# ── Map API ───────────────────────────────────────────────────────────────────

class MapLocationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.shops.models import Shop

        role = request.user.role

        if role == "customer":
            shops = list(Shop.objects.filter(is_verified=True).values("id", "name", "latitude", "longitude"))
            return Response({"shops": shops, "cold_storages": []})

        elif role in ["shop_owner"]:
            shops = list(Shop.objects.filter(is_verified=True).values("id", "name", "address", "city", "latitude", "longitude"))
            cold_storages = list(ColdStorage.objects.filter(verified=True).values("id", "name", "address", "latitude", "longitude"))
            return Response({"shops": shops, "cold_storages": cold_storages})

        elif role in ["cold_storage", "staff"]:
            shops = list(Shop.objects.filter(is_verified=True).values("id", "name", "address", "city", "latitude", "longitude"))
            return Response({"shops": shops, "cold_storages": []})

        else:
            shops = list(Shop.objects.filter(is_verified=True).values("id", "name", "latitude", "longitude"))
            return Response({"shops": shops, "cold_storages": []})


# ── Daily report ──────────────────────────────────────────────────────────────

class DailyReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user  = request.user
        owner = user.owner if user.role == "staff" else user

        try:
            cold_storage = owner.cold_storage
        except ColdStorage.DoesNotExist:
            return Response({"error": "Cold storage not found"}, status=404)

        today = timezone.now().date()

        orders      = B2BOrder.objects.filter(cold_storage=cold_storage, created_at__date=today)
        total_sales = orders.aggregate(total=Sum("total_price"))["total"] or 0

        cash_collected = (
            LedgerEntry.objects.filter(cold_storage=cold_storage, entry_type="payment", created_at__date=today)
            .aggregate(total=Sum("amount"))["total"] or 0
        )
        credit_given = (
            LedgerEntry.objects.filter(cold_storage=cold_storage, entry_type="credit", created_at__date=today)
            .aggregate(total=Sum("amount"))["total"] or 0
        )

        total_credit = (
            LedgerEntry.objects.filter(cold_storage=cold_storage, entry_type="credit")
            .aggregate(total=Sum("amount"))["total"] or 0
        )
        total_paid = (
            LedgerEntry.objects.filter(cold_storage=cold_storage, entry_type="payment")
            .aggregate(total=Sum("amount"))["total"] or 0
        )

        return Response({
            "orders": orders.count(),
            "sales":  total_sales,
            "cash":   cash_collected,
            "credit": credit_given,
            "balance": total_credit - total_paid,
        })
