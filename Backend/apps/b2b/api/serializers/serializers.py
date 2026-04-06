# apps/b2b/serializers/serializers.py
from rest_framework import serializers
from apps.b2b.models import ColdStorage, ColdStorageProduct, B2BOrder, B2BOrderItem
from django.db import transaction
from apps.shops.models import Shop
class ColdStorageProductSerializer(serializers.ModelSerializer):
    price_per_kg = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True
    )

    stock_kg = serializers.DecimalField(
    max_digits=10,
    decimal_places=2,
    required=False,
    allow_null=True
    )

    min_order_kg = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        allow_null=True
    )

    stock_pieces = serializers.IntegerField(
        required=False,
        allow_null=True
    )
    class Meta:
        model = ColdStorageProduct
        fields = [
            "id", "name", "category", "price_per_kg",
            "stock_kg", "min_order_kg", 
            "unit_type", "allowed_units",
            "approx_weight_per_piece_kg", "stock_pieces",
            "is_available","created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ColdStorageListSerializer(serializers.ModelSerializer):
    products     = ColdStorageProductSerializer(many=True, read_only=True)
    product_count = serializers.IntegerField(source="products.count", read_only=True)

    class Meta:
        model = ColdStorage
        fields = [
            "id", "name", "latitude", "longitude",
            "address", "verified", "product_count", "products",
        ]


class ColdStoragePrivateSerializer(serializers.ModelSerializer):
    products = ColdStorageProductSerializer(many=True, read_only=True)

    class Meta:
        model = ColdStorage
        fields = "__all__"
        read_only_fields = ["owner", "verified"]

# ── Order item serializers ────────────────────────────────────────────────────

class B2BOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    is_priced    = serializers.SerializerMethodField()
    class Meta:
        model = B2BOrderItem
        fields = [
            "id", "product", "product_name",
            "unit_type", "quantity",
            "product_name_snapshot", "price_per_kg_snapshot",
            "actual_weight_kg", "price_per_kg_final", "line_total",
            "is_priced",
        ]
        read_only_fields = [
            "product_name_snapshot", "price_per_kg_snapshot",
            "actual_weight_kg", "price_per_kg_final", "line_total",
        ]
        
    def get_is_priced(self, obj) -> bool:
        return obj.line_total is not None

class B2BOrderItemCreateSerializer(serializers.Serializer):
    """Used only during order creation. Validates each item."""
    product     = serializers.PrimaryKeyRelatedField(queryset=ColdStorageProduct.objects.filter(is_available=True))
    quantity    = serializers.DecimalField(max_digits=10, decimal_places=2)
    unit_type   = serializers.ChoiceField(choices=["kg", "piece"])
    

    def validate(self, data):
        product   = data["product"]
        qty       = data["quantity"]
        unit_type = data["unit_type"]
        allowed_units = (
            product.allowed_units
            if product.allowed_units
            else [product.unit_type]
        )

        if unit_type not in allowed_units:
            raise serializers.ValidationError(
                f"{product.name} can only be ordered in {allowed_units}"
            )

       
        # Allow both kg and piece depending on stock availability

        if unit_type == "kg":
            if product.stock_kg is None:
                raise serializers.ValidationError(
                    f"{product.name} is not available in kg."
                )

            if qty < product.min_order_kg:
                raise serializers.ValidationError(
                    f"Minimum order for {product.name} is {product.min_order_kg}kg."
                )

            if product.stock_kg < qty:
                raise serializers.ValidationError(
                    f"Insufficient stock for {product.name}."
                )

        elif unit_type == "piece":
            if product.stock_pieces is None:
                raise serializers.ValidationError(
                    f"{product.name} is not available in pieces."
                )

            if qty > product.stock_pieces:
                raise serializers.ValidationError(
                    f"Only {product.stock_pieces} pieces available for {product.name}."
                )

        return data


# ── Set price serializer (cold storage sets price for piece orders) ───────────

class SetPriceSerializer(serializers.Serializer):
    """
    Called by cold storage after weighing piece-based items.
    POST /api/b2b/orders/{id}/set-price/
    """
    item_id       = serializers.IntegerField(help_text="ID of the B2BOrderItem to price")
    actual_weight_kg  = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Actual weight after weighing (kg)"
    )
    price_per_kg  = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Price per kg charged by supplier"
    )

    def validate_actual_weight_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError("Weight must be greater than 0.")
        return value

    def validate_price_per_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price per kg must be greater than 0.")
        return value

# ── Order create / list serializers ──────────────────────────────────────────

class B2BOrderCreateSerializer(serializers.ModelSerializer):
    shop = serializers.PrimaryKeyRelatedField(
        queryset=Shop.objects.all(),
        required=False
    )
    items = B2BOrderItemCreateSerializer(many=True)
    payment_type = serializers.ChoiceField(
        choices=["cash", "credit"],
        default="cash"
    )
    class Meta:
        model  = B2BOrder
        fields = [
            # "cold_storage",
            "shop", 
            "notes", "items",
            "delivery_type", "delivery_address",
            "delivery_latitude", "delivery_longitude",
            "payment_type", 
        ]

    def validate(self, data):
        # Check shop exists
        user = self.context["request"].user

        if user.role == "shop_owner":
            shop = user.shops.first()
            if not shop:
                raise serializers.ValidationError({"shop": "You don't have a shop yet."})

        elif user.role == "cold_storage":
            # allow cold storage (manual order)
            shop = None

        # Check delivery fields
        delivery_type    = data.get("delivery_type", "pickup")
        delivery_address = data.get("delivery_address", "").strip()
        delivery_lat     = data.get("delivery_latitude", None)
        delivery_lng     = data.get("delivery_longitude", None)

        if delivery_type == "delivery":
            if not delivery_address:
                raise serializers.ValidationError({
                    "delivery_address": "Delivery address is required for delivery orders."
                })
            # Use `is None` — never `not delivery_lat` (0.0 is valid but falsy)
            # if delivery_lat is None or delivery_lng is None:
            #     raise serializers.ValidationError({
            #         "delivery_latitude": "Shop location (lat/lng) is required for delivery. Please set your shop location in settings."
            #     })

        return data
    #--------------Fix-End----------------

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user = self.context["request"].user

        if user.role == "shop_owner":
            shop = user.shops.first()

        elif user.role == "cold_storage":
            shop = validated_data.get("shop")

            if not shop:
                raise serializers.ValidationError({
                    "shop": "Shop is required for manual order"
                })

        # cold_storage = validated_data.get("cold_storage")

        # if not cold_storage:
        #     raise serializers.ValidationError("Cold storage is required")
        
        cold_storage = validated_data.pop("cold_storage", None)

        if not cold_storage:
            user = self.context["request"].user
            
            if user.role == "cold_storage":
                cold_storage = user.cold_storage
            else:
                raise serializers.ValidationError("Cold storage is required")
        
        # Determine initial status based on item types
        has_piece = any(i.get("unit_type") == "piece" for i in items_data)
        initial_status = B2BOrder.Status.PENDING_PRICE if has_piece else B2BOrder.Status.PENDING
        if validated_data.get("delivery_type") == "delivery":
            validated_data["delivery_latitude"] = shop.latitude
            validated_data["delivery_longitude"] = shop.longitude
        
        validated_data.pop("shop", None)  # Remove shop from validated_data since it's set separately
        order = B2BOrder.objects.create(
            shop=shop,
            cold_storage=cold_storage,  # 🔥 ADD THIS
            status=initial_status,
            **validated_data
        )

        for item_data in items_data:
            product = item_data["product"]
            qty = item_data["quantity"]
            unit_type = item_data["unit_type"]

            # ✅ CREATE ITEM FIRST
            item = B2BOrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                quantity_kg=qty if unit_type == "kg" else None,
                unit_type=unit_type,
                price_per_kg_snapshot=product.price_per_kg if unit_type == "kg" else None,
                product_name_snapshot=product.name,
            )

            # ✅ STOCK DEDUCTION (ONLY ONCE)
            if unit_type == "kg":
                if product.stock_kg < qty:
                    raise serializers.ValidationError("Stock went negative. Try again.")

                product.stock_kg -= qty
                product.save(update_fields=["stock_kg"])

                # ✅ LOW STOCK CHECK
                if product.stock_kg is not None and product.stock_kg < product.low_stock_threshold:
                    from apps.notifications.models import Notification

                    Notification.objects.create(
                        user=product.cold_storage.owner,
                        type=Notification.Type.LOW_STOCK,
                        title=f"Low stock alert: {product.name}",
                        message=f"{product.name} is running low on stock."
                    )

            elif unit_type == "piece" and product.stock_pieces is not None:
                product.stock_pieces -= int(qty)
                product.save(update_fields=["stock_pieces"])

                # ✅ LOW STOCK CHECK
                if product.stock_pieces < product.low_stock_threshold:
                    from apps.notifications.models import Notification

                    Notification.objects.create(
                        user=product.cold_storage.owner,
                        type=Notification.Type.LOW_STOCK,
                        title=f"Low stock alert: {product.name}",
                        message=f"{product.name} is running low on stock."
                    )

        order.recalculate_total()
        # Notify cold storage owner that a new bulk order arrived
        from apps.notifications.models import Notification
        Notification.objects.create(
            user=order.cold_storage.owner,
            type=Notification.Type.B2B_ORDER_PLACED,
            title="New bulk order received 📦",
            message=(
                f"{order.shop.name} placed a bulk order worth "
                f"₹{order.total_price}. "
                f"{order.items.count()} item(s) · "
                f"{'Delivery' if order.delivery_type == 'delivery' else 'Pickup'}."
            ),
        )
        return order

class B2BOrderSerializer(serializers.ModelSerializer):
    items              = B2BOrderItemSerializer(many=True, read_only=True)
    shop_name          = serializers.CharField(source="shop.name",         read_only=True)
    cold_storage_name  = serializers.CharField(source="cold_storage.name", read_only=True)
    delivery_latitude = serializers.FloatField(required=False)
    delivery_longitude = serializers.FloatField(required=False)
    has_piece_items  = serializers.SerializerMethodField()
    all_items_priced = serializers.SerializerMethodField()
    is_paid = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()
    
    def get_is_paid(self, obj):
        return obj.is_paid

    def get_payment_status(self, obj):
        return obj.payment_status
    
    def get_has_piece_items(self, obj) -> bool:
        return obj.items.filter(unit_type="piece").exists()

    def get_all_items_priced(self, obj) -> bool:
        return not obj.items.filter(line_total__isnull=True).exists()

    class Meta:
        model = B2BOrder
        fields = [
            "id", "shop", "shop_name", "cold_storage", "cold_storage_name",
            "status", "total_price", "notes", 
            "payment_type",
            "delivery_type", "delivery_address",
            "delivery_latitude", "delivery_longitude",
            "has_piece_items", "all_items_priced",
            "items","created_at", "updated_at",
            "is_paid",
            "payment_status",
            
            
        ]
        read_only_fields = ["shop", "total_price", "created_at", "updated_at"]
   
