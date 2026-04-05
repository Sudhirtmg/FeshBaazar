# apps/b2b/api/serializers/serializers.py
from rest_framework import serializers
from apps.b2b.models import (
    ColdStorage,
    ColdStorageProduct,
    B2BOrder,
    B2BOrderItem,
)


# ── Cold Storage ─────────────────────────────────────────────────────────────

class ColdStorageProductSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ColdStorageProduct
        fields = [
            "id", "name", "category", "unit_type", "allowed_units",
            "price_per_kg", "stock_kg", "stock_pieces",
            "min_order_kg", "low_stock_threshold",
            "approx_weight_per_piece_kg", "is_available",
            "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ColdStorageListSerializer(serializers.ModelSerializer):
    """Public view — shown to shop owners browsing cold storages."""
    products = ColdStorageProductSerializer(many=True, read_only=True)

    class Meta:
        model  = ColdStorage
        fields = ["id", "name", "address", "latitude", "longitude", "verified", "products"]


class ColdStoragePrivateSerializer(serializers.ModelSerializer):
    """Owner's private dashboard view."""
    products = ColdStorageProductSerializer(many=True, read_only=True)

    class Meta:
        model  = ColdStorage
        fields = ["id", "name", "address", "latitude", "longitude", "verified", "products", "created_at"]
        read_only_fields = ["verified", "created_at"]


# ── B2B Orders ────────────────────────────────────────────────────────────────

class B2BOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = B2BOrderItem
        fields = [
            "id", "product", "product_name_snapshot",
            "unit_type", "quantity", "quantity_kg",
            "price_per_kg_snapshot", "actual_weight_kg",
            "price_per_kg_final", "line_total", "price",
        ]
        read_only_fields = ["product_name_snapshot", "line_total", "price"]


class B2BOrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = B2BOrderItem
        fields = ["product", "unit_type", "quantity"]


class B2BOrderCreateSerializer(serializers.ModelSerializer):
    items = B2BOrderItemCreateSerializer(many=True)

    class Meta:
        model  = B2BOrder
        fields = [
            "items", "payment_type", "delivery_type",
            "delivery_address", "delivery_latitude", "delivery_longitude",
            "notes", "order_source",
        ]

    def create(self, validated_data):
        items_data   = validated_data.pop("items")
        request      = self.context["request"]
        user         = request.user

        # Resolve shop for the order
        if user.role == "shop_owner":
            shop = user.shops.first()
            if not shop:
                raise serializers.ValidationError("No shop found for this user.")
        elif user.role == "cold_storage":
            # Cold storage creates walk-in orders
            shop_id = self.context["request"].data.get("shop_id")
            if not shop_id:
                raise serializers.ValidationError("shop_id is required for cold storage orders.")
            from apps.shops.models import Shop
            try:
                shop = Shop.objects.get(id=shop_id)
            except Shop.DoesNotExist:
                raise serializers.ValidationError("Shop not found.")
        else:
            raise serializers.ValidationError("Invalid role for creating B2B orders.")

        order = B2BOrder.objects.create(shop=shop, created_by=user, **validated_data)

        has_piece_items = False
        total = 0

        for item_data in items_data:
            product  = item_data["product"]
            unit_type = item_data["unit_type"]
            quantity  = item_data["quantity"]

            if unit_type == "piece":
                has_piece_items = True
                line_total = None
            else:
                line_total = quantity * (product.price_per_kg or 0)
                total += line_total

            B2BOrderItem.objects.create(
                order=order,
                product=product,
                product_name_snapshot=product.name,
                unit_type=unit_type,
                quantity=quantity,
                price_per_kg_snapshot=product.price_per_kg if unit_type == "kg" else None,
                line_total=line_total,
                price=line_total or 0,
            )

        if has_piece_items:
            order.status      = B2BOrder.Status.PENDING_PRICE
            order.total_price = None
        else:
            order.total_price = total

        order.save(update_fields=["status", "total_price"])
        return order


class B2BOrderSerializer(serializers.ModelSerializer):
    items        = B2BOrderItemSerializer(many=True, read_only=True)
    shop_name    = serializers.CharField(source="shop.name", read_only=True)
    cold_storage_name = serializers.CharField(source="cold_storage.name", read_only=True)
    payment_status    = serializers.CharField(read_only=True)

    class Meta:
        model  = B2BOrder
        fields = [
            "id", "shop", "shop_name", "cold_storage", "cold_storage_name",
            "status", "payment_type", "payment_status", "total_price",
            "paid_amount", "delivery_type", "delivery_address",
            "delivery_latitude", "delivery_longitude",
            "notes", "order_source", "items",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "shop", "cold_storage", "total_price", "created_at", "updated_at"]


class SetPriceSerializer(serializers.Serializer):
    item_id           = serializers.IntegerField()
    actual_weight_kg  = serializers.DecimalField(max_digits=10, decimal_places=3)
    price_per_kg      = serializers.DecimalField(max_digits=10, decimal_places=2)
