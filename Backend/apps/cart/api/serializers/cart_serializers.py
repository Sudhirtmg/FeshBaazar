# apps/cart/api/serializers/cart_serializers.py
from rest_framework import serializers
from apps.cart.models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name  = serializers.CharField(source="product.name", read_only=True)
    cut_type_name = serializers.CharField(source="cut_type.name", read_only=True)
    shop_name     = serializers.CharField(source="product.shop.name", read_only=True)
    subtotal      = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model  = CartItem
        fields = [
            "id", "product", "product_name", "cut_type", "cut_type_name",
            "shop_name", "quantity", "amount", "price_at_time", "subtotal",
        ]
        read_only_fields = ["price_at_time"]


class CartItemAddSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CartItem
        fields = ["product", "cut_type", "quantity", "amount"]

    def validate(self, data):
        if not data.get("quantity") and not data.get("amount"):
            raise serializers.ValidationError(
                "Provide either quantity (kg) or amount (Rs.)."
            )
        product = data["product"]
        if not product.is_available:
            raise serializers.ValidationError(
                f"{product.name} is not available."
            )
        if product.stock_quantity == 0:
            raise serializers.ValidationError(
                f"{product.name} is out of stock."
            )
        cut_type = data.get("cut_type")
        if cut_type and cut_type.product != product:
            raise serializers.ValidationError(
                "This cut type does not belong to the selected product."
            )
        return data

    def create(self, validated_data):
        user     = self.context["request"].user
        cart, _  = Cart.objects.get_or_create(user=user)
        product  = validated_data["product"]
        cut_type = validated_data.get("cut_type")

        existing = CartItem.objects.filter(
            cart=cart, product=product, cut_type=cut_type
        ).first()

        if existing:
            if validated_data.get("quantity"):
                existing.quantity += validated_data["quantity"]
            elif validated_data.get("amount"):
                existing.amount = (existing.amount or 0) + validated_data["amount"]
            existing.save()
            return existing

        return CartItem.objects.create(cart=cart, **validated_data)


class CartSerializer(serializers.ModelSerializer):
    items      = CartItemSerializer(many=True, read_only=True)
    total      = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Cart
        fields = ["id", "items", "total", "item_count", "updated_at"]