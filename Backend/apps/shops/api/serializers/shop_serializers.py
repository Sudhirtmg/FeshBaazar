# # apps/shops/api/serializers/shop_serializers.py
# from rest_framework import serializers
# from apps.shops.models import Shop


# class ShopSerializer(serializers.ModelSerializer):
#     owner_phone = serializers.CharField(source="owner.phone", read_only=True)

#     class Meta:
#         model  = Shop
#         fields = [
#             "id", "name", "slug", "description", "phone",
#             "address", "city", "latitude", "longitude",
#             "is_open", "is_verified", "has_delivery", "has_pickup",
#             "delivery_charge", "owner_phone", "created_at",
#         ]
#         read_only_fields = ["slug", "is_verified", "created_at"]


# class ShopCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model  = Shop
#         fields = [
#             "name", "description", "phone",
#             "address", "city", "latitude", "longitude",
#         ]

#     def create(self, validated_data):
#         owner = self.context["request"].user
#         return Shop.objects.create(owner=owner, **validated_data)

# apps/shops/api/serializers/shop_serializers.py
from rest_framework import serializers
from apps.shops.models import Shop, ShopSchedule


class ShopScheduleSerializer(serializers.ModelSerializer):
    weekday_name = serializers.CharField(
        source="get_weekday_display", read_only=True
    )

    class Meta:
        model  = ShopSchedule
        fields = [
            "id", "weekday", "weekday_name", "is_active",
            "morning_open", "morning_close",
            "afternoon_open", "afternoon_close",
        ]


class ShopSerializer(serializers.ModelSerializer):
    owner_phone  = serializers.CharField(source="owner.phone", read_only=True)
    is_open      = serializers.BooleanField(read_only=True)  # ✅ from property
    next_opening = serializers.CharField(read_only=True)     # ✅ from property
    schedules    = ShopScheduleSerializer(many=True, read_only=True)

    class Meta:
        model  = Shop
        fields = [
            "id", "name", "slug", "description",
            "address", "city", "phone", "logo",
            "is_open", "is_verified",
            "is_temporarily_closed", "temporary_close_note",
            "next_opening", "owner_phone",
            "schedules", "created_at",
        ]
        read_only_fields = [
            "slug", "is_verified", "is_open",
            "next_opening", "created_at", "owner_phone",
        ]


class ShopCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Shop
        fields = ["name"]


class ShopOnboardingSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model  = Shop
        fields = [
            "name", "description", "address",
            "city", "phone", "logo",
            "is_temporarily_closed", "temporary_close_note",
        ]

    def update(self, instance, validated_data):
        logo = validated_data.pop("logo", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if logo is not None:
            instance.logo = logo
        instance.save()
        return instance


class ShopScheduleUpdateSerializer(serializers.Serializer):
    """
    Accepts a list of 7 schedule slots and bulk updates them.
    """
    schedules = ShopScheduleSerializer(many=True)

    def update(self, instance, validated_data):
        schedules_data = validated_data.get("schedules", [])
        for slot_data in schedules_data:
            weekday = slot_data.get("weekday")
            ShopSchedule.objects.update_or_create(
                shop=instance,
                weekday=weekday,
                defaults={
                    "is_active":       slot_data.get("is_active", True),
                    "morning_open":    slot_data.get("morning_open"),
                    "morning_close":   slot_data.get("morning_close"),
                    "afternoon_open":  slot_data.get("afternoon_open"),
                    "afternoon_close": slot_data.get("afternoon_close"),
                },
            )
        return instance