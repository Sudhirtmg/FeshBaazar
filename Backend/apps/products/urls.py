# apps/products/urls.py
from django.urls import path
from .api.views.product_views import (
    CategoryListView, ProductListView, ProductDetailView,
    ProductCreateView, ProductUpdateView, ProductDeleteView,
    ShopProductListView,
)

urlpatterns = [
    path("",                    ProductListView.as_view(),    name="product-list"),
    path("<int:pk>/",           ProductDetailView.as_view(),  name="product-detail"),
    path("create/",             ProductCreateView.as_view(),  name="product-create"),
    path("<int:pk>/update/",    ProductUpdateView.as_view(),  name="product-update"),
    path("<int:pk>/delete/",    ProductDeleteView.as_view(),  name="product-delete"),
    path("my-products/",        ShopProductListView.as_view(),name="my-products"),
    path("categories/",         CategoryListView.as_view(),   name="category-list"),
]