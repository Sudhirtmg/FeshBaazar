from rest_framework import serializers
from apps.accounts.models import User


class CreateStaffSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "name",
            "phone",
            "password",
            "can_collect_payment",
            "can_view_ledger",
            "can_create_order",
            "can_manage_products",
            "can_view_orders",
            "can_deliver_orders",
            "can_confirm_orders",
        ]

    def create(self, validated_data):
        owner = self.context["request"].user

        user = User.objects.create_user(
            phone=validated_data["phone"],
            password=validated_data["password"],
            role=User.Role.STAFF,
            owner=owner,
            name=validated_data.get("name", ""),
            # 🔥 permissions
            can_collect_payment=validated_data.get("can_collect_payment", False),
            can_view_ledger=validated_data.get("can_view_ledger", False),
            can_create_order=validated_data.get("can_create_order", False),
            can_manage_products=validated_data.get("can_manage_products", False),
            can_view_orders=validated_data.get("can_view_orders", False),
            can_deliver_orders=validated_data.get("can_deliver_orders", False),
            can_confirm_orders=validated_data.get("can_confirm_orders", False),
        )

        return user
