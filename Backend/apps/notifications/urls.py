from django.urls import path
from apps.notifications.api.views.NotificationListView import NotificationListView
from apps.notifications.api.views.NotificationDetailView import NotificationDetailView

urlpatterns = [
    path("", NotificationListView.as_view(), name="notifications"),
    path("<int:pk>/", NotificationDetailView.as_view(), name="notification-detail"),
]