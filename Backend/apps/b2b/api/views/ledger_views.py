# apps/b2b/api/views/ledger_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from apps.b2b.models import B2BOrder, LedgerEntry, ColdStorage
from apps.shops.models import Shop
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


# ── 1. Ledger history ────────────────────────────────────────────────────────

class LedgerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        shop_id = request.query_params.get("shop_id")
        if not shop_id:
            return Response({"error": "shop_id required"}, status=400)

        user  = request.user
        owner = user.owner if user.role == "staff" else user

        shop = (
            Shop.objects.filter(id=shop_id, b2b_orders__cold_storage__owner=owner)
            .distinct()
            .first()
        )
        if not shop:
            return Response({"error": "Shop not found"}, status=404)

        entries = LedgerEntry.objects.filter(shop=shop).order_by("-created_at")

        data = []
        for e in entries:
            items = []
            if e.order:
                for item in e.order.items.all():
                    items.append({
                        "product_name": item.product_name_snapshot,
                        "price_per_kg": float(item.price_per_kg_snapshot or 0),
                        "quantity":     float(item.quantity),
                        "total":        float(item.line_total or 0),
                    })

            data.append({
                "id":           e.id,
                "amount":       str(e.amount),
                "entry_type":   e.entry_type,
                # ✅ FIX: use phone as fallback — username=None on this User model
                "collected_by": _resolve_user_display(e.collected_by),
                "weighted_by":  _resolve_user_display(e.weighted_by),
                "note":         e.note,
                "balance_after": str(e.balance_after),
                "order_id":     e.order.id if e.order else None,
                "created_at":   e.created_at.isoformat(),
                "items":        items,
                "shop_name":    e.shop.name if e.shop else "",
                "shop_phone":   getattr(e.shop, "phone", "") or "",
                "shop_email":   getattr(e.shop, "email", "") or "",
                "cold_storage_name":    e.cold_storage.name if e.cold_storage else "",
                "cold_storage_address": getattr(e.cold_storage, "address", "") or "",
                "cold_storage_phone":   getattr(e.cold_storage.owner, "phone", "") or "",
            })

        return Response(data)


# ── 2. Balance ────────────────────────────────────────────────────────────────

class LedgerBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        shop_id = request.query_params.get("shop_id")
        if not shop_id:
            return Response({"error": "shop_id required"}, status=400)

        user  = request.user
        owner = user.owner if user.role == "staff" else user

        shop = (
            Shop.objects.filter(id=shop_id, b2b_orders__cold_storage__owner=owner)
            .distinct()
            .first()
        )
        if not shop:
            return Response({"error": "Shop not found"}, status=404)

        credits = (
            LedgerEntry.objects.filter(shop=shop, entry_type="credit")
            .aggregate(total=Sum("amount"))["total"] or 0
        )
        payments = (
            LedgerEntry.objects.filter(shop=shop, entry_type="payment")
            .aggregate(total=Sum("amount"))["total"] or 0
        )

        return Response({
            "total_credit": float(credits),
            "total_paid":   float(payments),
            "balance":      float(credits - payments),
        })


# ── 3. Add payment ────────────────────────────────────────────────────────────

class AddPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ["cold_storage", "staff"]:
            return Response({"error": "Permission denied"}, status=403)

        if request.user.role == "staff" and not request.user.can_collect_payment:
            return Response({"error": "No permission to collect payment"}, status=403)

        shop_id  = request.data.get("shop_id")
        amount   = request.data.get("amount")
        note     = request.data.get("note", "")
        order_id = request.data.get("order_id")

        if not all([shop_id, amount]):
            return Response({"error": "Missing fields"}, status=400)

        user  = request.user
        owner = user.owner if user.role == "staff" else user

        shop = (
            Shop.objects.filter(id=shop_id, b2b_orders__cold_storage__owner=owner)
            .distinct()
            .first()
        )
        if not shop:
            return Response({"error": "Shop not found"}, status=404)

        order = None
        if order_id:
            order = get_object_or_404(B2BOrder, id=order_id, shop=shop)

        try:
            cold_storage = owner.cold_storage
        except ColdStorage.DoesNotExist:
            return Response({"error": "Cold storage not found"}, status=404)

        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                raise ValueError()
        except Exception:
            return Response({"error": "Invalid amount"}, status=400)

        credits = (
            LedgerEntry.objects.filter(shop=shop, entry_type="credit")
            .aggregate(total=Sum("amount"))["total"] or 0
        )
        payments = (
            LedgerEntry.objects.filter(shop=shop, entry_type="payment")
            .aggregate(total=Sum("amount"))["total"] or 0
        )
        new_balance = credits - payments - amount

        entry = LedgerEntry.objects.create(
            shop=shop,
            cold_storage=cold_storage,
            order=order,
            amount=amount,
            entry_type="payment",
            note=note,
            collected_by=request.user,   # ✅ always saved
            balance_after=new_balance,
        )

        if order:
            new_paid = order.paid_amount + amount
            if new_paid > (order.total_price or 0):
                return Response({"error": "Overpayment not allowed"}, status=400)
            order.paid_amount = new_paid
            order.save(update_fields=["paid_amount"])

        return Response({"message": "Payment added", "id": entry.id})


# ── 4. Shop summary list ──────────────────────────────────────────────────────

class ShopLedgerSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user  = request.user
        owner = user.owner if user.role == "staff" else user

        shops = Shop.objects.filter(b2b_orders__cold_storage__owner=owner).distinct()

        data = []
        for shop in shops:
            credits = (
                LedgerEntry.objects.filter(shop=shop, entry_type="credit")
                .aggregate(total=Sum("amount"))["total"] or 0
            )
            payments = (
                LedgerEntry.objects.filter(shop=shop, entry_type="payment")
                .aggregate(total=Sum("amount"))["total"] or 0
            )
            data.append({
                "id":           shop.id,
                "name":         shop.name,
                "balance":      float(credits - payments),
                "total_credit": float(credits),
                "total_paid":   float(payments),
            })

        return Response(data)


# ── 5. Staff collection summary ───────────────────────────────────────────────

class StaffCollectionSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.utils import timezone

        today = timezone.now().date()
        data  = LedgerEntry.objects.filter(
            collected_by=request.user,
            entry_type="payment",
            created_at__date=today,
        ).aggregate(total=Sum("amount"))

        return Response({
            # ✅ FIX: phone not username
            "staff":                   _resolve_user_display(request.user),
            "total_collected_today":   float(data["total"] or 0),
        })


# ── 6. All staff collection ───────────────────────────────────────────────────

class AllStaffCollectionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = (
            LedgerEntry.objects.filter(entry_type="payment")
            .values("collected_by__phone", "collected_by__name")
            .annotate(total=Sum("amount"))
        )
        return Response([
            {
                "staff": row["collected_by__name"] or row["collected_by__phone"],
                "total": float(row["total"]),
            }
            for row in data
        ])
