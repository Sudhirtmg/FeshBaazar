# from django.urls import path
# from .api.views.shop_views import (
#     ShopListView, ShopCreateView, ShopDetailView,
#     ShopUpdateView, MyShopView
# )

# urlpatterns = [
#     path("",                    ShopListView.as_view(),   name="shop-list"),
#     path("my-shop/",            MyShopView.as_view(),     name="my-shop"),
#     path("create/",             ShopCreateView.as_view(),  name="shop-create"),
#     path("<slug:slug>/",        ShopDetailView.as_view(), name="shop-detail"),
#     path("<slug:slug>/update/", ShopUpdateView.as_view(), name="shop-update"),
# ]

# apps/shops/urls.py
from django.urls import path
from apps.shops.api.views.shop_views import (
    ShopListView,
    ShopDetailView,
    MyShopView,
    ShopOnboardingView,
    ShopScheduleView,
    BecomeShopOwnerView,
    ShopUpdateView,
)

urlpatterns = [
    path("",                    ShopListView.as_view(),       name="shop-list"),
    path("my-shop/",            MyShopView.as_view(),         name="my-shop"),
    path("onboarding/",         ShopOnboardingView.as_view(), name="shop-onboarding"),
    path("schedule/",           ShopScheduleView.as_view(),   name="shop-schedule"),
    path("become-shop-owner/",  BecomeShopOwnerView.as_view(),name="become-shop-owner"),
    path("<slug:slug>/",        ShopDetailView.as_view(),     name="shop-detail"),
    path("<slug:slug>/update/", ShopUpdateView.as_view(),     name="shop-update"),
]