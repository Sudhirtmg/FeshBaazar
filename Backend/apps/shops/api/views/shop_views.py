# apps/shops/api/views/shop_views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.shops.models import Shop
from apps.shops.api.serializers.shop_serializers import ShopSerializer, ShopCreateSerializer
from apps.common.permissions import IsShopOwner, IsOwnerOfShop


class ShopListView(generics.ListAPIView):
    serializer_class   = ShopSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # ✅ Removed is_verified filter — show all open shops
        queryset = Shop.objects.filter(is_open=True).order_by("-created_at")
        city = self.request.query_params.get("city")
        if city:
            queryset = queryset.filter(city__icontains=city)
        return queryset


class ShopCreateView(generics.CreateAPIView):
    serializer_class   = ShopCreateSerializer
    permission_classes = [IsAuthenticated, IsShopOwner]


class ShopDetailView(generics.RetrieveAPIView):
    serializer_class   = ShopSerializer
    permission_classes = [AllowAny]
    queryset           = Shop.objects.all()
    lookup_field       = "slug"


class ShopUpdateView(generics.UpdateAPIView):
    serializer_class   = ShopSerializer
    permission_classes = [IsAuthenticated, IsOwnerOfShop]
    queryset           = Shop.objects.all()
    lookup_field       = "slug"
    http_method_names  = ["patch"]
    

class MyShopView(generics.RetrieveAPIView):
    serializer_class   = ShopSerializer
    permission_classes = [IsAuthenticated, IsShopOwner]

    def get_object(self):
        return self.request.user.shops.first()