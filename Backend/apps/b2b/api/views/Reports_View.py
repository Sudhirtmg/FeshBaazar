from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from apps.b2b.models import B2BOrder, LedgerEntry
from django.utils import timezone
from apps.common.permissions import IsColdStorage


class ReportsView(APIView):
    permission_classes = [IsAuthenticated, IsColdStorage]

    def get(self, request):
        cold_storage = request.user.cold_storage

        total_sales = B2BOrder.objects.filter(
            cold_storage=cold_storage
        ).aggregate(total=Sum("total_price"))["total"] or 0

        total_credit = LedgerEntry.objects.filter(
            cold_storage=cold_storage,
            entry_type="credit"
        ).aggregate(total=Sum("amount"))["total"] or 0

        total_paid = LedgerEntry.objects.filter(
            cold_storage=cold_storage,
            entry_type="payment"
        ).aggregate(total=Sum("amount"))["total"] or 0

        return Response({
            "sales": float(total_sales),
            "credit": float(total_credit),
            "paid": float(total_paid),
            "balance": float(total_credit - total_paid),
        })