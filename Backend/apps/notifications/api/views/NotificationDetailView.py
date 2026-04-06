from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from apps.notifications.models import Notification
from apps.notifications.api.serializers.NotificationSerializers import NotificationSerializer


class NotificationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        try:
            return Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return None

    # ✅ MARK AS READ
    def patch(self, request, pk):
        notification = self.get_object(request, pk)
        if not notification:
            return Response({"detail": "Not found"}, status=404)

        notification.is_read = True
        notification.save()

        return Response(NotificationSerializer(notification).data)

    # ✅ DELETE
    def delete(self, request, pk):
        notification = self.get_object(request, pk)
        if not notification:
            return Response({"detail": "Not found"}, status=404)

        notification.delete()
        return Response({"detail": "Deleted"}, status=status.HTTP_204_NO_CONTENT)