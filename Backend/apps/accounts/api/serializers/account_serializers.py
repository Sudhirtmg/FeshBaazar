from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.accounts.models import User
from apps.shops.models import Shop
from django.db import transaction


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    email    = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model  = User
        fields = ["phone", "email", "password", "role"]

    def validate_role(self, value):
        allowed = [User.Role.CUSTOMER, User.Role.SHOP_OWNER]
        if value not in allowed:
            raise serializers.ValidationError(
                "You can only register as a customer or shop owner."
            )
        return value

    def validate_phone(self, value):
        return value.replace(" ", "").replace("-", "").strip()

    def create(self, validated_data):
        email = validated_data.pop("email", None) or None
        role  = validated_data.get("role") or User.Role.CUSTOMER
        phone = validated_data["phone"].replace(" ", "").replace("-", "").strip()

        with transaction.atomic():
            user = User.objects.create_user(
                phone=phone,
                password=validated_data["password"],
                email=email,
                role=role,
            )

            if user.role == User.Role.SHOP_OWNER:
                Shop.objects.get_or_create(
                    owner=user,
                    defaults={
                        "name": f"{user.phone}'s Shop",
                        "is_verified": False,
                    },
                )

        return user


class LoginSerializer(serializers.Serializer):
    phone    = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone = data["phone"].replace(" ", "").replace("-", "").strip()
        user  = authenticate(username=phone, password=data["password"])

        if not user:
            raise serializers.ValidationError({
                "detail": "Invalid phone or password."
            })
        if not user.is_active:
            raise serializers.ValidationError({
                "detail": "Account is disabled."
            })

        data["user"]    = user
        data["role"]    = user.role
        data["user_id"] = user.id
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = [
            "id",
            "name",
            "phone",
            "email",
            "role",
            "profile_image",
            "date_joined",
            "can_collect_payment",
            "can_view_ledger",
            "can_create_order",
            "can_manage_products",
            "can_view_orders",
            "can_deliver_orders",
        ]
        read_only_fields = ["role", "date_joined"]


class CreateStaffSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model  = User
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
        ]

    def create(self, validated_data):
        owner = self.context["request"].user

        return User.objects.create_user(
            phone=validated_data["phone"],
            password=validated_data["password"],
            role=User.Role.STAFF,
            owner=owner,
            name=validated_data.get("name", ""),
            can_collect_payment=validated_data.get("can_collect_payment", False),
            can_view_ledger=validated_data.get("can_view_ledger", False),
            can_create_order=validated_data.get("can_create_order", False),
            can_manage_products=validated_data.get("can_manage_products", False),
            can_view_orders=validated_data.get("can_view_orders", False),
            can_deliver_orders=validated_data.get("can_deliver_orders", False),
        )
