from django.urls import path
from .api.views.shop_views import (
    ShopListView, ShopCreateView, ShopDetailView,
    ShopUpdateView, MyShopView
)

urlpatterns = [
    path("",                    ShopListView.as_view(),   name="shop-list"),
    path("my-shop/",            MyShopView.as_view(),     name="my-shop"),
    path("create/",             ShopCreateView.as_view(),  name="shop-create"),
    path("<slug:slug>/",        ShopDetailView.as_view(), name="shop-detail"),
    path("<slug:slug>/update/", ShopUpdateView.as_view(), name="shop-update"),
]