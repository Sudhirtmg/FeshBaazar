# apps/accounts/urls.py
from django.urls import path
from apps.accounts.api.views.staff_views import CreateStaffView
from rest_framework_simplejwt.views import TokenRefreshView
from .api.views.staff_views import StaffListView, StaffUpdateView, StaffDeleteView
from .api.views.account_views import RegisterView, LoginView, MeView

urlpatterns = [
    path("register/",      RegisterView.as_view(),    name="register"),
    path("login/",         LoginView.as_view(),        name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/",            MeView.as_view(),           name="me"),
    path("create-staff/", CreateStaffView.as_view(), name="create-staff"),
    path("staff/", StaffListView.as_view()),
    path("staff/<int:pk>/", StaffUpdateView.as_view()),
    path("staff/<int:pk>/delete/", StaffDeleteView.as_view()),
]