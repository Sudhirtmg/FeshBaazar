# apps/products/api/serializers/product_serializers.py

from rest_framework import serializers
from apps.products.models import Category, Product, CutType
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from apps.accounts.models import User
from django.utils.text import slugify
import uuid


# -------------------------------
# CATEGORY
# -------------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ["id", "name", "slug"]


# -------------------------------
# CUT TYPE
# -------------------------------
class CutTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CutType
        fields = ["id", "name", "extra_price", "is_active"]


# -------------------------------
# PRODUCT (READ)
# -------------------------------
class ProductSerializer(serializers.ModelSerializer):
    cut_types       = CutTypeSerializer(many=True, read_only=True)
    category_name   = serializers.CharField(source="category.name", read_only=True)
    shop_name       = serializers.CharField(source="shop.name", read_only=True)
    effective_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model  = Product
        fields = [
            "id", "name", "slug", "description",
            "price", "discount_price", "effective_price",
            "stock_quantity", "unit", "image", "is_available",
            "category", "category_name", "shop", "shop_name",
            "cut_types", "created_at",
        ]
        read_only_fields = ["slug", "created_at", "shop"]


# -------------------------------
# PRODUCT (CREATE)
# -------------------------------
class ProductCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )
    cut_types = CutTypeSerializer(many=True, required=False)

    class Meta:
        model  = Product
        fields = [
            "name", "description", "category",
            "price", "discount_price", "stock_quantity",
            "unit", "image", "cut_types",
        ]

    # 🔥 VALIDATION (MERGED + CLEAN)
    def validate(self, data):
        user = self.context["request"].user

        # Role check
        if user.role != User.Role.SHOP_OWNER:
            raise serializers.ValidationError("Only shop owners can create products.")

        price = data.get("price")
        discount_price = data.get("discount_price")

        # Price validation
        if price is not None and price < 0:
            raise serializers.ValidationError("Price cannot be negative.")

        if discount_price is not None:
            if discount_price < 0:
                raise serializers.ValidationError("Discount price cannot be negative.")
            if price is not None and discount_price > price:
                raise serializers.ValidationError("Discount price cannot be greater than price.")

        return data

    # 🔥 CUT TYPE VALIDATION
    def validate_cut_types(self, value):
        for cut in value:
            if cut.get("extra_price", 0) < 0:
                raise serializers.ValidationError("Extra price cannot be negative.")
        return value

    # 🔥 CREATE LOGIC (SAFE + TRANSACTION)
    def create(self, validated_data):
        print("FILES:", self.context["request"].FILES)
        print("DATA:", validated_data)
        cut_types_data = validated_data.pop("cut_types", []) or []
        image          = validated_data.pop("image", None)
        request = self.context["request"]

        shop = request.user.shops.first()

        if not shop:
            raise serializers.ValidationError("Shop not found.")
        
        
        with transaction.atomic():
            name = validated_data.get("name", "product")

            product = Product.objects.create(
                shop=shop,
                slug=slugify(name) + "-" + str(uuid.uuid4())[:6],
                **validated_data
            )
            if image:
                product.image = image
                product.save()

            CutType.objects.bulk_create([
                CutType(product=product, **cut) for cut in cut_types_data
            ])

        return product
    
    # ─── UPDATE ───────────────────────────────────────────────
    def update(self, instance, validated_data):
        cut_types_data = validated_data.pop("cut_types", None)
        # ✅ Only pop image if it was actually sent — don't overwrite with None
        image = validated_data.pop("image", None)

        # Update all other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # ✅ Only update image if a new File was uploaded
        if image is not None:
            instance.image = image

        instance.save()

        # ✅ Only replace cut types if they were sent in the request
        if cut_types_data is not None:
            instance.cut_types.all().delete()
            CutType.objects.bulk_create([
                CutType(product=instance, **cut) for cut in cut_types_data
            ])

        return instance