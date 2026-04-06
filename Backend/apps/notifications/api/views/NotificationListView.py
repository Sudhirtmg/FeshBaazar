# apps/notifications/api/views/NotificationListView.py:
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.notifications.models import Notification
from apps.notifications.api.serializers.NotificationSerializers import NotificationSerializer


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def patch(self, request):
        Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).update(is_read=True)
        return Response({"detail": "All marked as read."})