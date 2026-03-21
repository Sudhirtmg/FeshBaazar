# apps/cart/urls.py
from django.urls import path
from apps.cart.api.views.cart_views import CartView, CartItemAddView, CartItemUpdateView

urlpatterns = [
    path("",                CartView.as_view(),           name="cart"),
    path("items/",          CartItemAddView.as_view(),     name="cart-item-add"),
    path("items/<int:pk>/", CartItemUpdateView.as_view(),  name="cart-item-update"),
]