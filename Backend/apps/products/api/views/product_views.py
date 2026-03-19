# apps/products/api/views/product_views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.products.models import Category, Product, CutType
from rest_framework.parsers import MultiPartParser, FormParser
from apps.products.api.serializers.product_serializers import (
    CategorySerializer, ProductSerializer, ProductCreateSerializer, CutTypeSerializer
)
from apps.common.permissions import IsShopOwner


class CategoryListView(generics.ListAPIView):
    serializer_class   = CategorySerializer
    permission_classes = [AllowAny]
    queryset           = Category.objects.all().order_by("name")


class ProductListView(generics.ListAPIView):
    serializer_class   = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Product.objects.filter(
            is_available=True
        ).select_related("shop", "category").prefetch_related("cut_types")

        shop_id  = self.request.query_params.get("shop")
        category = self.request.query_params.get("category")
        city     = self.request.query_params.get("city")

        if shop_id:
            queryset = queryset.filter(shop__id=shop_id)
        if category:
            queryset = queryset.filter(category__slug=category)
        if city:
            queryset = queryset.filter(shop__city__icontains=city)

        return queryset.order_by("-created_at")


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class   = ProductSerializer
    permission_classes = [AllowAny]
    queryset           = Product.objects.select_related(
        "shop", "category"
    ).prefetch_related("cut_types")


class ProductCreateView(generics.CreateAPIView):
    serializer_class   = ProductCreateSerializer
    permission_classes = [IsAuthenticated, IsShopOwner]
    parser_classes     = [MultiPartParser, FormParser]


class ProductUpdateView(generics.UpdateAPIView):
    serializer_class   = ProductCreateSerializer
    permission_classes = [IsAuthenticated, IsShopOwner]
    parser_classes     = [MultiPartParser, FormParser]
    http_method_names  = ["patch"]

    def get_queryset(self):
        return Product.objects.filter(shop__owner=self.request.user)

    def patch(self, request, *args, **kwargs):
        # partial=True means only the fields sent will be updated
        # image won't be required if the user doesn't change it
        return self.partial_update(request, *args, **kwargs)


class ProductDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsShopOwner]

    def get_queryset(self):
        return Product.objects.filter(shop__owner=self.request.user)


class ShopProductListView(generics.ListAPIView):
    """All products for the logged-in shop owner."""
    serializer_class   = ProductSerializer
    permission_classes = [IsAuthenticated, IsShopOwner]

    def get_queryset(self):
        return Product.objects.filter(
            shop__owner=self.request.user
        ).select_related("category").prefetch_related("cut_types")