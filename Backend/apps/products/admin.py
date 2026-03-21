from django.contrib import admin
from .models import Product, Category, CutType


class CutTypeInline(admin.TabularInline):
    model  = CutType
    extra  = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "shop",
        "category",
        "price",
        "discount_price",
        "stock_quantity",
        "unit",
        "is_available",
        "created_at",
    )

    list_filter = (
        "shop",
        "category",
        "unit",
        "is_available",
    )

    search_fields = (
        "name",
        "shop__name",
        "category__name",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }
    
    inlines = [CutTypeInline] 
    


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = ("name", "slug")

    search_fields = ("name",)

    prepopulated_fields = {
        "slug": ("name",)
    }


@admin.register(CutType)
class CutTypeAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "product",
        "extra_price",
        "is_active",
    )

    list_filter = ("is_active",)

    search_fields = (
        "name",
        "product__name",
    )