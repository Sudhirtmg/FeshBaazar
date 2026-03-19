# apps/orders/api/serializers/order_serializers.py
from rest_framework import serializers
from apps.orders.models import Order, OrderItem, OrderStatusHistory


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = OrderItem
        fields = [
            "id", "product", "product_name", "cut_type_name",
            "quantity", "unit_price", "total_price",
        ]


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_phone = serializers.CharField(
        source="changed_by.phone", read_only=True
    )
    class Meta:
        model  = OrderStatusHistory
        fields = ["from_status", "to_status", "changed_by_phone", "note", "created_at"]


class OrderSerializer(serializers.ModelSerializer):
    items   = OrderItemSerializer(many=True, read_only=True)
    history = OrderStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model  = Order
        fields = [
            "id", "shop", "status", "payment_method",
            "subtotal", "delivery_fee", "total_amount",
            "delivery_name", "delivery_phone", "delivery_address",
            "notes", "items", "history", "created_at",
        ]


class CheckoutSerializer(serializers.Serializer):
    delivery_name    = serializers.CharField(max_length=255)
    delivery_phone   = serializers.CharField(max_length=20)
    delivery_address = serializers.CharField()
    payment_method   = serializers.ChoiceField(
        choices=Order.PaymentMethod.choices,
        default=Order.PaymentMethod.COD,
    )
    notes = serializers.CharField(required=False, allow_blank=True)


class StatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.Status.choices)
    note   = serializers.CharField(required=False, allow_blank=True)