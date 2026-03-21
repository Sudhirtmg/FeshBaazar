# apps/orders/urls.py
from django.urls import path
from apps.orders.api.views.order_views import (
    CheckoutView,
    CustomerOrderListView,
    OrderDetailView,
    ShopOrderListView,
    OrderStatusUpdateView,
)

urlpatterns = [
    path("checkout/",        CheckoutView.as_view(),         name="checkout"),
    path("",                 CustomerOrderListView.as_view(), name="order-list"),
    path("<int:pk>/",        OrderDetailView.as_view(),       name="order-detail"),
    path("<int:pk>/status/", OrderStatusUpdateView.as_view(), name="order-status"),
    path("shop-orders/",     ShopOrderListView.as_view(),     name="shop-orders"),
]