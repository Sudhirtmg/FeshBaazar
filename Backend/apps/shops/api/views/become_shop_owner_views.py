# apps/shops/api/views/become_shop_owner_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction

from apps.shops.models import Shop, ShopSchedule
from apps.accounts.models import User
from apps.shops.api.serializers.shop_serializers import ShopSerializer


class BecomeShopOwnerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.role == User.Role.SHOP_OWNER:
            shop = user.shops.first()
            return Response({
                "detail": "You are already a shop owner.",
                "shop": ShopSerializer(shop).data if shop else None,
            }, status=status.HTTP_200_OK)

        if user.role != User.Role.CUSTOMER:
            return Response(
                {"detail": "Only customers can become shop owners."},
                status=status.HTTP_403_FORBIDDEN,
            )

        with transaction.atomic():
            user.role = User.Role.SHOP_OWNER
            user.save(update_fields=["role"])

            shop = Shop.objects.create(
                owner       = user,
                name        = request.data.get("name", f"{user.phone}'s Shop"),
                phone       = request.data.get("phone", ""),
                address     = request.data.get("address", ""),
                city        = request.data.get("city", ""),
                is_verified = False,
                verification_status = "pending",
            )

            ShopSchedule.objects.bulk_create([
                ShopSchedule(
                    shop            = shop,
                    weekday         = day,
                    is_active       = True,
                    morning_open    = "06:00",
                    morning_close   = "11:00",
                    afternoon_open  = "14:00" if day < 6 else None,
                    afternoon_close = "18:00" if day < 6 else None,
                )
                for day in range(7)
            ])

        return Response({
            "detail": "Role upgraded. Complete your shop profile.",
            "shop": ShopSerializer(shop).data,
        }, status=status.HTTP_201_CREATED)


class CancelShopOwnerRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.role != User.Role.SHOP_OWNER:
            return Response(
                {"detail": "You are not a shop owner."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        shop = user.shops.first()
        if shop and shop.is_verified:
            return Response(
                {"detail": "Your shop is already verified. You cannot cancel."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            if shop:
                shop.delete()
            user.role = User.Role.CUSTOMER
            user.save(update_fields=["role"])

        return Response(
            {"detail": "Shop owner request cancelled. You are now a customer."},
            status=status.HTTP_200_OK,
        )