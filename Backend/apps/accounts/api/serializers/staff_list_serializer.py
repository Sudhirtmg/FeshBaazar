from rest_framework import serializers
from apps.accounts.models import User


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "phone",
            "can_view_orders",
            "can_confirm_orders",
            "can_deliver_orders",
            "can_collect_payment",
            "can_view_ledger",
            "can_manage_products",
        ]