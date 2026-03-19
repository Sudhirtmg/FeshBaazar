# apps/shops/api/serializers/shop_serializers.py
from rest_framework import serializers
from apps.shops.models import Shop


class ShopSerializer(serializers.ModelSerializer):
    owner_phone = serializers.CharField(source="owner.phone", read_only=True)

    class Meta:
        model  = Shop
        fields = [
            "id", "name", "slug", "description", "phone",
            "address", "city", "latitude", "longitude",
            "is_open", "is_verified", "has_delivery", "has_pickup",
            "delivery_charge", "owner_phone", "created_at",
        ]
        read_only_fields = ["slug", "is_verified", "created_at"]


class ShopCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Shop
        fields = [
            "name", "description", "phone",
            "address", "city", "latitude", "longitude",
        ]

    def create(self, validated_data):
        owner = self.context["request"].user
        return Shop.objects.create(owner=owner, **validated_data)