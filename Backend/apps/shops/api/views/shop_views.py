# # apps/shops/api/views/shop_views.py
# from rest_framework import generics, status
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from apps.shops.models import Shop
# from apps.shops.api.serializers.shop_serializers import ShopSerializer, ShopCreateSerializer
# from apps.common.permissions import IsShopOwner, IsOwnerOfShop


# class ShopListView(generics.ListAPIView):
#     serializer_class   = ShopSerializer
#     permission_classes = [AllowAny]

#     def get_queryset(self):
#         # ✅ Removed is_verified filter — show all open shops
#         queryset = Shop.objects.filter(is_open=True).order_by("-created_at")
#         city = self.request.query_params.get("city")
#         if city:
#             queryset = queryset.filter(city__icontains=city)
#         return queryset


# class ShopCreateView(generics.CreateAPIView):
#     serializer_class   = ShopCreateSerializer
#     permission_classes = [IsAuthenticated, IsShopOwner]


# class ShopDetailView(generics.RetrieveAPIView):
#     serializer_class   = ShopSerializer
#     permission_classes = [AllowAny]
#     queryset           = Shop.objects.all()
#     lookup_field       = "slug"


# class ShopUpdateView(generics.UpdateAPIView):
#     serializer_class   = ShopSerializer
#     permission_classes = [IsAuthenticated, IsOwnerOfShop]
#     queryset           = Shop.objects.all()
#     lookup_field       = "slug"
#     http_method_names  = ["patch"]
    

# class MyShopView(generics.RetrieveAPIView):
#     serializer_class   = ShopSerializer
#     permission_classes = [IsAuthenticated, IsShopOwner]

#     def get_object(self):
#         return self.request.user.shops.first()

# apps/shops/api/views/shop_views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction

from apps.shops.models import Shop, ShopSchedule, WEEKDAYS
from apps.accounts.models import User
from apps.shops.api.serializers.shop_serializers import (
    ShopSerializer,
    ShopCreateSerializer,
    ShopOnboardingSerializer,
    ShopScheduleSerializer,
    ShopScheduleUpdateSerializer,
)
from apps.common.permissions import IsShopOwner, IsOwnerOfShop


class ShopListView(generics.ListAPIView):
    serializer_class   = ShopSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Shop.objects.filter(
            is_verified=True,
        ).prefetch_related("schedules").order_by("-created_at")
        city = self.request.query_params.get("city")
        if city:
            queryset = queryset.filter(city__icontains=city)
        return queryset


class ShopDetailView(generics.RetrieveAPIView):
    serializer_class   = ShopSerializer
    permission_classes = [AllowAny]
    queryset           = Shop.objects.filter(
        is_verified=True
    ).prefetch_related("schedules")
    lookup_field       = "slug"


class MyShopView(generics.RetrieveAPIView):
    serializer_class   = ShopSerializer
    permission_classes = [IsAuthenticated, IsShopOwner]

    def get_object(self):
        return self.request.user.shops.prefetch_related("schedules").first()


class ShopOnboardingView(generics.UpdateAPIView):
    serializer_class   = ShopOnboardingSerializer
    permission_classes = [IsAuthenticated, IsShopOwner]
    parser_classes     = [MultiPartParser, FormParser]
    http_method_names  = ["patch"]

    def get_object(self):
        return self.request.user.shops.first()

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ShopScheduleView(APIView):
    """
    GET  — returns current 7-day schedule (creates defaults if missing)
    POST — bulk update all 7 days at once
    """
    permission_classes = [IsAuthenticated, IsShopOwner]

    def _get_or_create_schedule(self, shop):
        """Ensure all 7 days exist with sensible Nepal meat shop defaults."""
        defaults = {
            # Morning: 6 AM – 11 AM, Afternoon: 2 PM – 6 PM
            0: {"morning_open": "06:00", "morning_close": "11:00", "afternoon_open": "14:00", "afternoon_close": "18:00", "is_active": True},
            1: {"morning_open": "06:00", "morning_close": "11:00", "afternoon_open": "14:00", "afternoon_close": "18:00", "is_active": True},
            2: {"morning_open": "06:00", "morning_close": "11:00", "afternoon_open": "14:00", "afternoon_close": "18:00", "is_active": True},
            3: {"morning_open": "06:00", "morning_close": "11:00", "afternoon_open": "14:00", "afternoon_close": "18:00", "is_active": True},
            4: {"morning_open": "06:00", "morning_close": "11:00", "afternoon_open": "14:00", "afternoon_close": "18:00", "is_active": True},
            5: {"morning_open": "06:00", "morning_close": "11:00", "afternoon_open": "14:00", "afternoon_close": "18:00", "is_active": True},
            6: {"morning_open": "06:00", "morning_close": "12:00", "afternoon_open": None,     "afternoon_close": None,     "is_active": True},
        }
        for day, times in defaults.items():
            ShopSchedule.objects.get_or_create(
                shop=shop,
                weekday=day,
                defaults=times,
            )

    def get(self, request):
        shop = request.user.shops.first()
        self._get_or_create_schedule(shop)
        schedules = shop.schedules.all().order_by("weekday")
        return Response(ShopScheduleSerializer(schedules, many=True).data)

    def post(self, request):
        shop = request.user.shops.first()
        serializer = ShopScheduleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(shop, serializer.validated_data)
        schedules = shop.schedules.all().order_by("weekday")
        return Response(ShopScheduleSerializer(schedules, many=True).data)


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
                owner=user,
                name=f"{user.phone}'s Shop",
                is_verified=False,
            )

            # ✅ Auto-create default schedule for new shop
            ShopSchedule.objects.bulk_create([
                ShopSchedule(
                    shop=shop,
                    weekday=day,
                    is_active=True,
                    morning_open="06:00",
                    morning_close="11:00",
                    afternoon_open="14:00" if day < 6 else None,
                    afternoon_close="18:00" if day < 6 else None,
                )
                for day in range(7)
            ])

        return Response({
            "detail": "Role upgraded. Complete your shop profile.",
            "shop": ShopSerializer(shop).data,
        }, status=status.HTTP_201_CREATED)


class ShopUpdateView(generics.UpdateAPIView):
    serializer_class   = ShopSerializer
    permission_classes = [IsAuthenticated, IsOwnerOfShop]
    queryset           = Shop.objects.all()
    lookup_field       = "slug"
    http_method_names  = ["patch"]
    parser_classes     = [MultiPartParser, FormParser]