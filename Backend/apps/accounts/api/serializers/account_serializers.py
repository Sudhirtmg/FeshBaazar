from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.accounts.models import User
from apps.shops.models import Shop
from django.db import transaction


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["phone", "email", "password", "role"]

    def validate_role(self, value):
        allowed = [User.Role.CUSTOMER, User.Role.SHOP_OWNER]
        if value not in allowed:
            raise serializers.ValidationError(
                "You can only register as a customer or shop owner."
            )
        return value
    
    #--------------Add-Start----------------
    def validate_phone(self, value):
        return value.replace(" ", "").replace("-", "").strip()
    #--------------Add-End----------------

    def create(self, validated_data):
        # ✅ Fixed: single pop, converts empty string to None
        email = validated_data.pop("email", None) or None
        role = validated_data.get("role") or User.Role.CUSTOMER
        #--------------Add-Start----------------
        phone = validated_data["phone"].replace(" ", "").replace("-", "").strip()
        #--------------Add-End----------------

        with transaction.atomic():
            user = User.objects.create_user(
                phone=phone,
                password=validated_data["password"],
                email=email,
                role=role,
            )

            # ✅ Auto-create shop when registering as shop owner
            if user.role == User.Role.SHOP_OWNER:
                Shop.objects.get_or_create(
                        owner=user,
                        defaults={
                            "name": f"{user.phone}'s Shop",
                            "is_verified": False,  # ✅ pending admin approval
                        },
                )

        return user


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone = data["phone"].replace(" ", "").replace("-", "").strip()

        user = authenticate(
            username=phone,
            password=data["password"]
        )

        if not user:
            raise serializers.ValidationError({
                "detail": "Invalid phone or password."
            })

        if not user.is_active:
            raise serializers.ValidationError({
                "detail": "Account is disabled."
            })

        data["user"] = user
        data["role"] = user.role
        data["user_id"] = user.id
        return data
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "name",
            "id",
            "phone",
            "email",
            "role",
            "profile_image",
            "date_joined",

            # 🔥 ADD THESE (VERY IMPORTANT)
            "can_collect_payment",
            "can_view_ledger",
            "can_create_order",
            "can_manage_products",
            "can_view_orders",
            "can_deliver_orders",
        ]

        read_only_fields = ["role", "date_joined"]
