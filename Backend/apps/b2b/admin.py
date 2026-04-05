from django.contrib import admin
from apps.b2b.models import (
    ColdStorage,
    ColdStorageProduct,
    B2BOrder,
    B2BOrderItem,
    LedgerEntry,
)


@admin.register(ColdStorage)
class ColdStorageAdmin(admin.ModelAdmin):
    list_display  = ["name", "owner", "verified", "created_at"]
    list_filter   = ["verified"]
    search_fields = ["name", "owner__phone"]


@admin.register(ColdStorageProduct)
class ColdStorageProductAdmin(admin.ModelAdmin):
    list_display  = ["name", "cold_storage", "category", "unit_type", "price_per_kg", "is_available"]
    list_filter   = ["category", "unit_type", "is_available"]
    search_fields = ["name", "cold_storage__name"]


class B2BOrderItemInline(admin.TabularInline):
    model  = B2BOrderItem
    extra  = 0
    fields = ["product", "product_name_snapshot", "unit_type", "quantity", "price_per_kg_snapshot", "line_total"]
    readonly_fields = ["product_name_snapshot", "line_total"]


@admin.register(B2BOrder)
class B2BOrderAdmin(admin.ModelAdmin):
    list_display  = ["id", "shop", "cold_storage", "status", "payment_type", "total_price", "paid_amount", "created_at"]
    list_filter   = ["status", "payment_type", "delivery_type"]
    search_fields = ["shop__name", "cold_storage__name"]
    inlines       = [B2BOrderItemInline]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display  = ["id", "shop", "cold_storage", "entry_type", "amount", "balance_after", "collected_by", "weighted_by", "created_at"]
    list_filter   = ["entry_type"]
    search_fields = ["shop__name", "cold_storage__name"]
    readonly_fields = ["created_at"]
