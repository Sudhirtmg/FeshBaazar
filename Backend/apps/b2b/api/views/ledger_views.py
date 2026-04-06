# apps/b2b/api/views/ledger_views.py

from datetime import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from apps.b2b.models import B2BOrder, LedgerEntry
from apps.shops.models import Shop
from apps.b2b.models import ColdStorage
from decimal import Decimal


def _resolve_user_display(user):
    """
    Return the best human-readable identifier for a User.

    The custom User model sets username=None, so falling back to
    .username returns None.  We use .name first (if filled), then
    .phone (always present and unique).
    """
    if user is None:
        return None
    return user.name.strip() if user.name and user.name.strip() else user.phone


# ✅ 1. GET LEDGER (history)
class LedgerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        shop_id = request.query_params.get("shop_id")

        if not shop_id:
            return Response({"error": "shop_id required"}, status=400)
        # --------------Fix-Start----------------
        user = request.user
        owner = user.owner if user.role == "staff" else user

        shop = (
            Shop.objects.filter(id=shop_id, b2b_orders__cold_storage__owner=owner)
            .distinct()
            .first()
        )
        # --------------Fix-End----------------

        if not shop:
            return Response({"error": "Shop not found"}, status=404)

        entries = LedgerEntry.objects.filter(
            shop=shop,
            cold_storage__owner_id=owner.id
        ).order_by("-created_at")

        data = []

        for e in entries:
            items = []

            if e.order:
                for item in e.order.items.all():
                    # Priority 1: price_per_kg_final (piece orders, set after weighing)
                    # Priority 2: price_per_kg_snapshot (kg orders, set at order time)
                    price_per_kg = float(
                        item.price_per_kg_final or item.price_per_kg_snapshot or 0
                    )

                    # Priority 3: derive from totals if both price fields are missing
                    if price_per_kg == 0 and item.line_total:
                        if item.unit_type == "piece" and item.actual_weight_kg:
                            # piece: line_total = actual_weight_kg × price_per_kg_final
                            price_per_kg = round(
                                float(item.line_total) / float(item.actual_weight_kg), 2
                            )
                        elif item.unit_type == "kg" and item.quantity:
                            # kg: line_total = quantity × price_per_kg
                            price_per_kg = round(
                                float(item.line_total) / float(item.quantity), 2
                            )

                    items.append({
                        "product_name": item.product_name_snapshot,
                        "price_per_kg": price_per_kg,
                        "quantity":     float(item.quantity),
                        "total":        float(item.line_total or 0),
                    })


            data.append(
                {
                    "id": e.id,
                    "amount": str(e.amount),
                    "entry_type": e.entry_type,
                    "collected_by": _resolve_user_display(e.collected_by),
                    "weighted_by": _resolve_user_display(e.weighted_by),
                    "note": e.note,
                    "balance_after": str(e.balance_after),
                    "order_id": e.order.id if e.order else None,
                    "created_at": e.created_at.isoformat(),
                    # ✅ PRODUCTS
                    "items": items,
                    # 🔥 ADD THIS (VERY IMPORTANT)
                    "shop_name": e.shop.name if e.shop else "",
                    "shop_phone": getattr(e.shop, "phone", "") or "",
                    "shop_email": getattr(e.shop, "email", "") or "",
                    "cold_storage_name": e.cold_storage.name if e.cold_storage else "",
                    "cold_storage_address": getattr(e.cold_storage, "address", "")
                    or "",
                    "cold_storage_phone": getattr(e.cold_storage.owner, "phone", "")
                    or "",
                }
            )

        return Response(data)


# ✅ 2. GET BALANCE
class LedgerBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        shop_id = request.query_params.get("shop_id")
        if not shop_id:
            return Response({"error": "shop_id required"}, status=400)

        # --------------Fix-Start----------------
        user = request.user
        owner = user.owner if user.role == "staff" else user

        shop = (
            Shop.objects.filter(id=shop_id, b2b_orders__cold_storage__owner=owner)
            .distinct()
            .first()
        )
        # --------------Fix-End----------------

        if not shop:
            return Response({"error": "Shop not found"}, status=404)
        credits = (
            LedgerEntry.objects.filter(shop=shop, entry_type="credit").aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        payments = (
            LedgerEntry.objects.filter(shop=shop, entry_type="payment").aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )
        return Response(
            {
                "total_credit": float(credits),
                "total_paid": float(payments),
                "balance": float(credits - payments),
            }
        )


# ✅ 3. ADD PAYMENT (mark as paid)
class AddPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # --------------Add-Start----------------
        if request.user.role not in ["cold_storage", "staff"]:
            return Response({"error": "Permission denied"}, status=403)

        if request.user.role == "staff" and not request.user.can_collect_payment:
            return Response({"error": "No permission to collect payment"}, status=403)
        # --------------Add-End----------------
        shop_id = request.data.get("shop_id")
        # cold_storage_id = request.data.get("cold_storage_id")
        amount = request.data.get("amount")
        note = request.data.get("note", "")
        order_id = request.data.get("order_id")

        # ✅ validate shop first
        # --------------Fix-Start----------------
        user = request.user

        # If staff → use owner
        owner = user.owner if user.role == "staff" else user

        shop = (
            Shop.objects.filter(id=shop_id, b2b_orders__cold_storage__owner=owner)
            .distinct()
            .first()
        )
        # --------------Fix-End----------------

        if not shop:
            return Response({"error": "Shop not found"}, status=404)
        order = None
        if order_id:
            order = get_object_or_404(
                B2BOrder, id=order_id, shop=shop  # 🔥 VERY IMPORTANT SECURITY
            )

        # if not all([shop_id, cold_storage_id, amount]):
        #     return Response({"error": "Missing fields"}, status=400)
        # --------------Fix-Start----------------
        if not all([shop_id, amount]):
            return Response({"error": "Missing fields"}, status=400)
        # --------------Fix-End----------------

        # ✅ validate cold storage

        user = request.user
        owner = user.owner if user.role == "staff" else user

        try:
            cold_storage = owner.cold_storage
        except ColdStorage.DoesNotExist:
            return Response({"error": "Cold storage not found"}, status=404)

        # ✅ validate amount
        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                raise ValueError()
        except:
            return Response({"error": "Invalid amount"}, status=400)

        credits = (
            LedgerEntry.objects.filter(shop=shop, entry_type="credit").aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        payments = (
            LedgerEntry.objects.filter(shop=shop, entry_type="payment").aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        current_balance = credits - payments
        new_balance = current_balance - amount

        entry = LedgerEntry.objects.create(
            shop=shop,
            cold_storage=cold_storage,
            order=order,
            amount=amount,
            entry_type="payment",
            note=note,
            collected_by=request.user,
            balance_after=new_balance,
        )
        if order:
            new_paid = order.paid_amount + amount

            if new_paid > (order.total_price or 0):
                return Response({"error": "Overpayment not allowed"}, status=400)

            order.paid_amount = new_paid
            order.save(update_fields=["paid_amount"])

        return Response({"message": "Payment added", "id": entry.id})


class StaffCollectionSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()

        data = LedgerEntry.objects.filter(
            collected_by=request.user, entry_type="payment", created_at__date=today
        ).aggregate(total=Sum("amount"))

        return Response(
            {
                "staff": _resolve_user_display(request.user),
                "total_collected_today": float(data["total"] or 0),
            }
        )


class AllStaffCollectionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = (
            LedgerEntry.objects.filter(entry_type="payment")
            .values("collected_by__phone", "collected_by__name")
            .annotate(total=Sum("amount"))
        )

        return Response(
            [
                {
                    "staff": row["collected_by__name"] or row["collected_by__phone"],
                    "total": float(row["total"]),
                }
                for row in data
            ]
        )


class ShopLedgerSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        owner = user.owner if user.role == "staff" else user

        shops = Shop.objects.filter(b2b_orders__cold_storage__owner=owner).distinct()

        data = []

        for shop in shops:
            credits = (
                LedgerEntry.objects.filter(shop=shop, entry_type="credit").aggregate(
                    total=Sum("amount")
                )["total"]
                or 0
            )

            payments = (
                LedgerEntry.objects.filter(shop=shop, entry_type="payment").aggregate(
                    total=Sum("amount")
                )["total"]
                or 0
            )

            balance = credits - payments

            data.append(
                {
                    "id": shop.id,
                    "name": shop.name,
                    "balance": float(balance),
                    "total_credit": float(credits),
                    "total_paid": float(payments),
                }
            )

        return Response(data)
