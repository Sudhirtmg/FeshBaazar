from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.accounts.models import User
from apps.accounts.api.serializers.staff_serializers import CreateStaffSerializer
from apps.accounts.api.serializers.staff_list_serializer import StaffSerializer


class CreateStaffView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # 🔥 Only cold storage can create staff
        if user.role != User.Role.COLD_STORAGE:
            return Response(
                {"error": "Only cold storage can create staff"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CreateStaffSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        staff = serializer.save()

        return Response({
            "message": "Staff created successfully",
            "staff_id": staff.id,
            "phone": staff.phone
        })
        
class StaffListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != User.Role.COLD_STORAGE:
            return Response({"error": "Not allowed"}, status=403)

        staff = User.objects.filter(owner=user, role=User.Role.STAFF)
        serializer = StaffSerializer(staff, many=True)

        return Response(serializer.data)


# ✅ UPDATE STAFF PERMISSIONS
class StaffUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user

        if user.role != User.Role.COLD_STORAGE:
            return Response({"error": "Not allowed"}, status=403)

        try:
            staff = User.objects.get(id=pk, owner=user,role=User.Role.STAFF)
        except User.DoesNotExist:
            return Response({"error": "Staff not found"}, status=404)

        serializer = StaffSerializer(
            staff,
            data=data,
            partial=True
        )
        allowed_fields = [
            "can_view_orders",
            "can_confirm_orders",
            "can_deliver_orders",
            "can_collect_payment",
            "can_view_ledger",
            "can_manage_products",
        ]

        data = {k: v for k, v in request.data.items() if k in allowed_fields}

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Updated successfully"})
    
# ✅ DELETE STAFF
class StaffDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        if request.user.role != User.Role.COLD_STORAGE:
            return Response({"error": "Not allowed"}, status=403)

        try:
            staff = User.objects.get(id=pk, owner=request.user)
        except User.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        staff.delete()

        return Response({"message": "Deleted"})