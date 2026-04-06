# apps/shops/urls.py
from django.urls import path
from apps.shops.api.views.shop_views import (
    ShopListView,
    ShopDetailView,
    MyShopView,
    ShopOnboardingView,
    ShopScheduleView,
    
    ShopUpdateView,
   
)

from apps.shops.api.views.become_shop_owner_views import (
    BecomeShopOwnerView,
    CancelShopOwnerRequestView,
)
from .api.views.shop_views import CreateWalkInShopView

urlpatterns = [
    path("",                    ShopListView.as_view(),       name="shop-list"),
    path("my-shop/",            MyShopView.as_view(),         name="my-shop"),
    path("onboarding/",         ShopOnboardingView.as_view(), name="shop-onboarding"),
    path("schedule/",           ShopScheduleView.as_view(),   name="shop-schedule"),
    path("become-shop-owner/",  BecomeShopOwnerView.as_view(),name="become-shop-owner"),
    #--------------Add-Start--------------------------------
    path("cancel-owner-request/",    CancelShopOwnerRequestView.as_view(),  name="cancel-owner-request"),
    #--------------Add-End--------------------------------
    path("create-walkin/", CreateWalkInShopView.as_view()),
    path("<slug:slug>/",        ShopDetailView.as_view(),     name="shop-detail"),
    path("<slug:slug>/update/", ShopUpdateView.as_view(),     name="shop-update"),

]