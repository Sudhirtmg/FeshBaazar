# b2b/views.py
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from django.db.models import Q
from apps.b2b.models import ColdStorage, ColdStorageProduct, B2BOrder,B2BOrderItem
from apps.b2b.api.serializers.serializers import (
    ColdStorageListSerializer,
    ColdStoragePrivateSerializer,
    ColdStorageProductSerializer,
    B2BOrderCreateSerializer,
    B2BOrderSerializer,
    SetPriceSerializer, 
)
from apps.common.permissions import IsShopOwner, IsColdStorage, IsShopOwnerOrColdStorage,IsColdStorageOrStaff
from django.db.models import Sum
from django.utils import timezone

#--------------Add-Start----------------
def _create_ledger_entry(order, user=None):
    """
    Create ledger entry ONLY when total_price is available.
    Prevent duplicate entries.
    """

    from apps.b2b.models import LedgerEntry
    from django.db.models import Sum

    # ❌ Skip if no price yet (piece order not priced)
    if not order.total_price:
        return

    # ❌ Prevent duplicate ledger entries
    if LedgerEntry.objects.filter(order=order, entry_type="credit").exists():
        return

    total_credit = LedgerEntry.objects.filter(
        shop=order.shop,
        entry_type="credit"
    ).aggregate(total=Sum("amount"))["total"] or 0

    total_payment = LedgerEntry.objects.filter(
        shop=order.shop,
        entry_type="payment"
    ).aggregate(total=Sum("amount"))["total"] or 0

    current_balance = total_credit - total_payment
    new_balance = current_balance + order.total_price

    LedgerEntry.objects.create(
        shop=order.shop,
        cold_storage=order.cold_storage,
        order=order,
        amount=order.total_price,
        entry_type="credit",
        balance_after=new_balance,
        note=f"{order.payment_type.upper()} order #{order.id}",
        weighted_by=user,
    )


    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "ledger",
        {
            "type": "send_ledger_update",
            "data": {
                "type": "refresh"
            }
        }
    )
    #--------------Add-End----------------

def get_shop_balance(shop):
    from apps.b2b.models import LedgerEntry

    credits = LedgerEntry.objects.filter(
        shop=shop,
        entry_type="credit"
    ).aggregate(total=Sum("amount"))["total"] or 0

    payments = LedgerEntry.objects.filter(
        shop=shop,
        entry_type="payment"
    ).aggregate(total=Sum("amount"))["total"] or 0
    

    return credits - payments

# ── Cold Storage: public browsing by shops ──────────────────────────────────

class ColdStorageListView(generics.ListAPIView):
    """
    GET /api/b2b/cold-storages/
    Only shop owners can browse. Customers and cold storage CANNOT access.
    """
    serializer_class = ColdStorageListSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopOwner]

    def get_queryset(self):
        qs = ColdStorage.objects.filter(verified=True).prefetch_related("products")
        # Optional: filter by distance if lat/lng provided
        lat = self.request.query_params.get("lat")
        lng = self.request.query_params.get("lng")
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(products__category=category).distinct()
        return qs


class ColdStorageDetailView(generics.RetrieveAPIView):
    """
    GET /api/b2b/cold-storages/<id>/
    Only shop owners can view cold storage details.
    """
    serializer_class = ColdStorageListSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopOwner]
    queryset = ColdStorage.objects.filter(verified=True)


# ── Cold Storage: owner's own dashboard ─────────────────────────────────────

class MyColdStorageView(generics.RetrieveUpdateAPIView):
    """
    GET/PATCH /api/b2b/my-cold-storage/
    Cold storage owners manage their own profile.
    """
    serializer_class = ColdStoragePrivateSerializer
    permission_classes = [permissions.IsAuthenticated, IsColdStorageOrStaff]

    def get_object(self):
        return get_object_or_404(ColdStorage, owner=self.request.user)


class ColdStorageProductListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/b2b/my-cold-storage/products/  → list own products
    POST /api/b2b/my-cold-storage/products/  → add a product
    """
    serializer_class = ColdStorageProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsColdStorageOrStaff]

    def get_queryset(self):
        return ColdStorageProduct.objects.filter(
            cold_storage__owner=self.request.user
        )

    def perform_create(self, serializer):
        cold_storage = get_object_or_404(ColdStorage, owner=self.request.user)
        serializer.save(cold_storage=cold_storage)


class ColdStorageProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PATCH/DELETE /api/b2b/my-cold-storage/products/<id>/
    Cold storage owners can only edit their own products.
    """
    serializer_class = ColdStorageProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsColdStorageOrStaff]

    def get_queryset(self):
        return ColdStorageProduct.objects.filter(
            cold_storage__owner=self.request.user
        )


# ── B2B Orders: placed by shops, received by cold storage ───────────────────

class B2BOrderCreateView(generics.CreateAPIView):
    """
    POST /api/b2b/orders/
    Only shop owners can place B2B orders.
    """
    serializer_class = B2BOrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopOwnerOrColdStorage]
    # def perform_create(self, serializer):
    #     user = self.request.user

    #     if user.role == "shop_owner":
    #         shop = user.shops.first()
    #         if not shop:
    #             return Response({"error": "No shop found"}, status=400)
    #         cold_storage_id = self.request.data.get("cold_storage")
    #         cold_storage = get_object_or_404(ColdStorage, id=cold_storage_id)

    #         order = serializer.save(
    #             shop=shop,
    #             cold_storage=cold_storage
    #         )

    #     elif user.role == "cold_storage":
    #         cold_storage = get_object_or_404(ColdStorage, owner=user)

    #         order = serializer.save()

    #     else:
    #         raise ValidationError("Invalid role")
    #     # order = serializer.save()
    #     from apps.b2b.models import LedgerEntry
    #     CREDIT_LIMIT = 50000

    #     if order.payment_type == "credit":
    #         current_balance = get_shop_balance(order.shop)

    #         if current_balance + (order.total_price or 0) > CREDIT_LIMIT:
    #             raise ValidationError("Credit limit exceeded")

    # # ------------------ CREDIT ENTRY ONLY ------------------
    #     # ================= CASH =================
    #     if order.payment_type == "cash":
            
    #         order.paid_amount = order.total_price or 0
            
    #         order.save(update_fields=["paid_amount"])

    #     # ================= CREDIT =================
    #     #--------------Fix-Start----------------
    #     if order.payment_type == "credit":


    #         # calculate current balance
    #         total_credit = LedgerEntry.objects.filter(
    #             shop=order.shop,
    #             entry_type="credit"
    #         ).aggregate(Sum("amount"))["amount__sum"] or 0

    #         total_payment = LedgerEntry.objects.filter(
    #             shop=order.shop,
    #             entry_type="payment"
    #         ).aggregate(Sum("amount"))["amount__sum"] or 0

    #         current_balance = total_credit - total_payment

    #         new_balance = current_balance + (order.total_price or 0)

    #         LedgerEntry.objects.create(
    #             shop=order.shop,
    #             cold_storage=order.cold_storage,
    #             order=order,
    #             amount=order.total_price or 0,
    #             entry_type="credit",
    #             balance_after=new_balance,
    #             note=f"Credit for order #{order.id}"
    #         )
    #     #--------------Fix-End----------------
    #     notify_order_update(order)
    # Find the entire perform_create method and replace it:
    def perform_create(self, serializer):
        user = self.request.user

        if user.role == "shop_owner":
            cold_storage_id = self.request.data.get("cold_storage")  # ← fix key name
            cold_storage    = get_object_or_404(ColdStorage, id=cold_storage_id, verified=True)
            order           = serializer.save(cold_storage=cold_storage)

        elif user.role == "cold_storage":
            cold_storage = get_object_or_404(ColdStorage, owner=user)
            order        = serializer.save(cold_storage=cold_storage)

        else:
            raise ValidationError("Invalid role")

        # Payment logic — runs for both roles
        from apps.b2b.models import LedgerEntry
        CREDIT_LIMIT = 50000
        _create_ledger_entry(order, user)


        if (
            order.payment_type == "cash"
            and order.delivery_type == "pickup"
            and self.request.user.role == "cold_storage"  # ← only auto-pay walk-in orders
        ):
            order.paid_amount = order.total_price or 0
        else:
            order.paid_amount = 0

        order.save(update_fields=["paid_amount"])

        notify_order_update(order)


class ShopB2BOrderListView(generics.ListAPIView):
    """
    GET /api/b2b/orders/my-shop/
    Shop owner views their own orders sent to cold storages.
    """
    serializer_class = B2BOrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopOwner]

    def get_queryset(self):
        return B2BOrder.objects.filter(
            shop__owner=self.request.user
        ).select_related("cold_storage").prefetch_related("items__product") \
        .order_by('-created_at')


class ColdStorageIncomingOrderListView(generics.ListAPIView):
    """
    GET /api/b2b/orders/incoming/
    Cold storage views orders received from shops.
    """
    serializer_class = B2BOrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsColdStorageOrStaff]

    def get_queryset(self):
        #--------------Fix-Start----------------
        user = self.request.user
        owner = user.owner if user.role == "staff" else user

        return B2BOrder.objects.filter(
            cold_storage__owner=owner
        ).select_related("shop").prefetch_related("items__product") \
        .order_by('-created_at')
        #--------------Fix-End----------------
        
    #--------------Add-Start----------------
    def get(self, request, *args, **kwargs):
        if request.user.role == "staff" and not request.user.can_view_orders:
            return Response({"error": "No permission to view orders"}, status=403)

        return super().get(request, *args, **kwargs)
    #--------------Add-End----------------


class B2BOrderStatusUpdateView(generics.UpdateAPIView):
    """
    PATCH /api/b2b/orders/<id>/status/
    Cold storage can update order status. Shop owners cannot.
    """
    serializer_class = B2BOrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsColdStorageOrStaff]
    http_method_names = ["patch"]

    def get_queryset(self):
        #--------------Fix-Start----------------
        user = self.request.user
        owner = user.owner if user.role == "staff" else user

        return B2BOrder.objects.filter(
            cold_storage__owner=owner
        )
        #--------------Fix-End----------------

    def partial_update(self, request, *args, **kwargs):
        if request.user.role == "staff" and not request.user.can_deliver_orders:
            return Response({"error": "No permission"}, status=403)

        # ✅ FIRST GET ORDER
        order = self.get_object()

        new_status = request.data.get("status")

        # ✅ VALID STATUS CHECK
        valid_statuses = [s[0] for s in B2BOrder.Status.choices]
        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Choices: {valid_statuses}"},
                status=400,
            )

        # ✅ STAFF RULE

        if request.user.role == "staff":

        # ✅ CONFIRM
            if new_status == "confirmed":
                if not request.user.can_confirm_orders:
                    return Response(
                        {"error": "No permission to confirm orders"},
                        status=403
                    )

            # ✅ DELIVERY
            elif new_status in ["processing", "dispatched", "delivered"]:
                if not request.user.can_deliver_orders:
                    return Response(
                        {"error": "No permission for delivery actions"},
                        status=403
                    )

            # ❌ ANY OTHER STATUS
            else:
                return Response(
                    {"error": f"Staff cannot set status to '{new_status}'"},
                    status=403
                )

        # ✅ NON-STAFF RULE
        else:
            if not order.can_transition_to(new_status):
                return Response(
                    {"error": f"Cannot transition from '{order.status}' to '{new_status}'."},
                    status=400,
                )

        # ✅ UPDATE STATUS
        old_status = order.status
        order.status = new_status
        order.save(update_fields=["status"])
        notify_order_update(order)
        from apps.notifications.models import Notification

        # Status label for readable messages
        STATUS_LABELS = {
            "confirmed":  "confirmed ✅",
            "processing": "being processed 🔄",
            "dispatched": "dispatched 🚚",
            "delivered":  "delivered 🎉",
            "cancelled":  "cancelled ❌",
            "priced":     "priced — please review 💰",
        }
            # Notify the shop owner about the status change
        Notification.objects.create(
            user=order.shop.owner,
            type=Notification.Type.B2B_ORDER_UPDATED,
            title=f"Bulk order #{order.id} {STATUS_LABELS.get(new_status, new_status)}",
            message=(
                f"Your order from {order.cold_storage.name} "
                f"(₹{order.total_price}) is now {new_status}."
            ),
        )

        # Restore stock if order is cancelled
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
    """
    POST /api/b2b/orders/{id}/set-price/

    Called by cold storage after physically weighing piece-based items.
    Body: { "item_id": int, "actual_weight_kg": float, "price_per_kg": float }

    - Sets actual_weight_kg, price_per_kg_final, line_total on the item
    - If ALL items in the order are priced → status becomes "priced"
    - Notifies shop owner
    """
    permission_classes = [permissions.IsAuthenticated, IsColdStorageOrStaff]

    def post(self, request, pk):
        user = request.user
        owner = user.owner if user.role == "staff" else user

        order = get_object_or_404(
            B2BOrder,
            pk=pk,
            cold_storage__owner=owner,
        )

        if order.status not in [B2BOrder.Status.PENDING_PRICE]:
            return Response(
                {"error": f"Cannot set price on an order with status '{order.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SetPriceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item_id    = serializer.validated_data["item_id"]
        weight     = serializer.validated_data["actual_weight_kg"]
        price_kg   = serializer.validated_data["price_per_kg"]

        # Fetch the specific item and verify it belongs to this order
        item = get_object_or_404(B2BOrderItem, pk=item_id, order=order)

        if item.unit_type != "piece":
            return Response(
                {"error": "This item is kg-based and already has a price."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set the pricing
        item.actual_weight_kg   = weight
        item.price_per_kg_final = price_kg
        item.line_total         = weight * price_kg
        item.save(update_fields=["actual_weight_kg", "price_per_kg_final", "line_total"])
        LedgerEntry.objects.filter(order=order, entry_type="credit").update(
            weighted_by=request.user
        )
        notify_order_update(order)
        # Check if ALL piece items in this order are now priced
        unpriced_count = order.items.filter(
            unit_type="piece",
            line_total__isnull=True,
        ).count()

        if unpriced_count == 0:
            order.status = B2BOrder.Status.CONFIRMED
            order.save(update_fields=["status"])

            order.recalculate_total()
            order.refresh_from_db()

            #--------------Add-Start----------------
            _create_ledger_entry(order, request.user)
            #--------------Add-End----------------

            notify_order_update(order)

        return Response(
            B2BOrderSerializer(order).data,
            status=status.HTTP_200_OK,
        )


# ── Map API: location visibility enforced per role ───────────────────────────

class MapLocationsView(APIView):
    """
    GET /api/map/locations/
    Returns locations based on the caller's role:
      - customer     → shops only (no address)
      - shop_owner   → shops + cold storages (with address)
      - cold_storage → shops only (with address for delivery)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.shops.models import Shop

        #--------------Fix-Start----------------
        # role is directly on User model — no separate profile
        role = request.user.role
        #--------------Fix-End----------------

        #--------------Add-Start----------------
        # Each role gets different fields — visibility rules enforced here
        if role == "customer":
            # Customers see shop name + location ONLY — no address
            shops = list(Shop.objects.filter(is_verified=True).values(
                "id", "name", "latitude", "longitude"
                # address intentionally excluded
            ))
            return Response({
                "shops": shops,
                "cold_storages": [],  # customers never see cold storage
            })

        elif role == "shop_owner":
            # Shop owners see shops with address (for customer delivery context)
            shops = list(Shop.objects.filter(is_verified=True).values(
                "id", "name", "address", "city", "latitude", "longitude"
            ))
            # Shop owners also see cold storage locations + address
            cold_storages = list(ColdStorage.objects.filter(verified=True).values(
                "id", "name", "address", "latitude", "longitude"
            ))
            return Response({
                "shops": shops,
                "cold_storages": cold_storages,
            })

        elif role == "cold_storage":
            # Cold storage sees shop locations + address (for delivery routing)
            # but NOT customer info, NOT other cold storages
            shops = list(Shop.objects.filter(is_verified=True).values(
                "id", "name", "address", "city", "latitude", "longitude"
            ))
            return Response({
                "shops": shops,
                "cold_storages": [],  # cold storage cannot see other cold storages
            })

        elif role == "staff":
            shops = list(Shop.objects.filter(is_verified=True).values(
                "id", "name", "address", "city", "latitude", "longitude"
            ))
            return Response({
                "shops": shops,
                "cold_storages": [],
            })

        else:
            shops = list(Shop.objects.filter(is_verified=True).values(
                "id", "name", "latitude", "longitude"
            ))
            return Response({
                "shops": shops,
                "cold_storages": [],
            })
        
def notify_order_update(order):
    channel_layer = get_channel_layer()

    event_type = "new_order"

    if order.status == "confirmed":
        event_type = "order_confirmed"
    elif order.status == "processing":
        event_type = "order_processing"
    elif order.status == "dispatched":
        event_type = "delivery_assigned"

    async_to_sync(channel_layer.group_send)(
        "global_updates",
        {
            "type": "send_update",
            "data": {
                "type": event_type,
                "order_id": order.id,
            }
        }
    )
    
#--------------Add-Start----------------
class B2BOrderDetailView(RetrieveAPIView):
    """
    GET /api/b2b/orders/<id>/
 
    Accessible by:
      - shop_owner   → orders where shop.owner == user  
                       OR orders placed by cold_storage on behalf of a walk-in
                       shop that was created under this user's account
      - cold_storage → orders where cold_storage.owner == user
      - staff        → orders where cold_storage.owner == user.owner
    """
    serializer_class = B2BOrderSerializer
    permission_classes = [IsAuthenticated]  # role checks done in get_object
 
    def get_queryset(self):
        user = self.request.user

        if user.role == "shop_owner":
            return B2BOrder.objects.filter(
                shop__owner=user
            )

        if user.role in ["cold_storage", "staff"]:
            owner = user.owner if user.role == "staff" else user

            return B2BOrder.objects.filter(
                Q(cold_storage__owner_id=owner.id)
            )

        return B2BOrder.objects.none()
            
    def get_object(self):
            qs = self.get_queryset()
            obj = get_object_or_404(qs, pk=self.kwargs["pk"])

            print("🔥 OrderDetailView called")
            print("REQUEST USER:", self.request.user)
            print("ORDER SHOP OWNER:", obj.shop.owner)

            return obj
            #     if user.role == "shop_owner" and obj.shop.owner != user:
    #         raise PermissionDenied("Not your order.")
 
    #     if user.role in ["cold_storage", "staff"]:
    #         owner = user.owner if user.role == "staff" else user
    #         if obj.cold_storage.owner != owner:
    #             raise PermissionDenied("Not your order.")
 
    # def get_object(self):
    #     """
    #     Override to give a cleaner error and handle the walk-in shop edge case.
    #     """
    #     user = self.request.user
    #     pk = self.kwargs["pk"]
 
    #     # Try to fetch from the role-filtered queryset first
    #     qs = self.get_queryset()
    #     obj = qs.filter(pk=pk).first()
    #     print("🔥 OrderDetailView called")
    #     print("REQUEST USER:", self.request.user)
    #     print("ORDER SHOP OWNER:", obj.shop.owner if obj else "NONE")
 
    #     if obj is None:

    #         raise NotFound(f"Order #{pk} not found.")
 
    #     # Extra permission safety
    #     if user.role == "shop_owner" and obj.shop.owner != user:
    #         raise PermissionDenied("Not your order.")
 
    #     if user.role in ["cold_storage", "staff"]:
    #         owner = user.owner if user.role == "staff" else user
    #         if obj.cold_storage.owner != owner:
    #             raise PermissionDenied("Not your order.")
 
    #     return obj
    
#--------------Add-End----------------


#--------------Add-Start----------------
class ShopOrderConfirmView(APIView):
    """
    PATCH /api/b2b/orders/<id>/confirm/

    Shop owner confirms priced order → moves to confirmed
    """
    permission_classes = [IsAuthenticated, IsShopOwner]

    def patch(self, request, pk):
        order = get_object_or_404(
            B2BOrder,
            pk=pk,
            shop__owner=request.user
        )

        # ✅ Only allow priced → confirmed
        if order.status != B2BOrder.Status.PRICED:
            return Response(
                {"error": "Only priced orders can be confirmed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = B2BOrder.Status.CONFIRMED
        order.save(update_fields=["status"])

        notify_order_update(order)

        # 🔔 Notify cold storage
        from apps.notifications.models import Notification

        Notification.objects.create(
            user=order.cold_storage.owner,
            type=Notification.Type.B2B_ORDER_UPDATED,
            title=f"Order #{order.id} confirmed ✅",
            message=f"{order.shop.name} confirmed the order. You can now process it."
        )

        return Response(B2BOrderSerializer(order).data)
#--------------Add-End----------------




from apps.b2b.models import B2BOrder, LedgerEntry


class DailyReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        #--------------Fix-Start----------------
        user = request.user
        owner = user.owner if user.role == "staff" else user

        cold_storage = owner.cold_storage
        #--------------Fix-End----------------

        today = timezone.now().date()

        # Orders today
        orders = B2BOrder.objects.filter(
            cold_storage=cold_storage,
            created_at__date=today
        )

        total_orders = orders.count()

        total_sales = orders.aggregate(
            total=Sum("total_price")
        )["total"] or 0

        # Payments today
        payments = LedgerEntry.objects.filter(
            cold_storage=cold_storage,
            entry_type="payment",
            created_at__date=today
        )

        cash_collected = payments.aggregate(
            total=Sum("amount")
        )["total"] or 0

        # Credit given today
        credits = LedgerEntry.objects.filter(
            cold_storage=cold_storage,
            entry_type="credit",
            created_at__date=today
        )

        credit_given = credits.aggregate(
            total=Sum("amount")
        )["total"] or 0

        # Total outstanding
        total_credit = LedgerEntry.objects.filter(
            cold_storage=cold_storage
        ).filter(
            entry_type="credit"
        ).aggregate(total=Sum("amount"))["total"] or 0

        total_paid = LedgerEntry.objects.filter(
            cold_storage=cold_storage
        ).filter(
            entry_type="payment"
        ).aggregate(total=Sum("amount"))["total"] or 0

        balance = total_credit - total_paid

        return Response({
            "orders": total_orders,
            "sales": total_sales,
            "cash": cash_collected,
            "credit": credit_given,
            "balance": balance,
        })