# apps/b2b/admin.py
from django.contrib import admin
from django.utils.html import mark_safe
from .models import ColdStorage, ColdStorageProduct, B2BOrder, B2BOrderItem, B2BOrderStatusHistory


class ColdStorageProductInline(admin.TabularInline):
    model  = ColdStorageProduct
    extra  = 0
    fields = [
        "name", "category", "allowed_units",  "price_per_kg",
        "stock_kg","stock_pieces", "min_order_kg", "is_available",
    ]


class B2BOrderItemInline(admin.TabularInline):
    model  = B2BOrderItem
    extra  = 0
    fields = [
        "product", "product_name_snapshot",
        "quantity_kg", "price_per_kg_snapshot", "price",
    ]
    readonly_fields = ["product_name_snapshot", "price_per_kg_snapshot", "price"]


@admin.register(ColdStorage)
class ColdStorageAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "owner",
        "verified", 
        "address",
        "location_link",
        "verification_badge",
        "product_count",
        "created_at",
    ]
    list_filter    = ["verified"]
    search_fields  = ["name", "owner__phone"]
    list_editable  = ["verified"]
    ordering       = ["verified", "-created_at"]
    inlines        = [ColdStorageProductInline]
    readonly_fields = ["created_at", "map_preview"]

    fieldsets = (
        (
            "Cold Storage Info",
            {
                "fields": (
                    "owner",
                    "name",
                    "address",
                    "latitude",
                    "longitude",
                    "map_preview",
                )
            },
        ),
        (
            "Verification",
            {
                "fields": ("verified",),
                "description": "⚠️ Only verify after confirming the supplier details.",
            },
        ),
        (
            "Meta",
            {
                "fields": ("created_at",),
            },
        ),
    )

    actions = ["verify_suppliers", "unverify_suppliers"]

    def verification_badge(self, obj):
        if obj.verified:
            return mark_safe('<span style="color:green;font-weight:bold">✓ Verified</span>')
        return mark_safe('<span style="color:orange;font-weight:bold">⏳ Pending</span>')
    verification_badge.short_description = "Status"

    def product_count(self, obj):
        count = obj.products.count()
        return mark_safe(f'<span style="font-weight:bold">{count}</span>')
    product_count.short_description = "Products"

    def location_link(self, obj):
        if obj.latitude and obj.longitude:
            url = f"https://www.google.com/maps?q={obj.latitude},{obj.longitude}"
            return mark_safe(
                f'<a href="{url}" target="_blank" '
                f'style="color:#16a34a;font-weight:600;">📍 Open Map</a>'
            )
        return "No location"
    location_link.short_description = "Location"

    def map_preview(self, obj):
        if obj.latitude and obj.longitude:
            return mark_safe(
                f'<iframe width="100%" height="200" '
                f'src="https://maps.google.com/maps?q={obj.latitude},{obj.longitude}&z=15&output=embed">'
                f'</iframe>'
            )
        return "No location set"
    map_preview.short_description = "Map Preview"

    def verify_suppliers(self, request, queryset):
        queryset.update(verified=True)
        self.message_user(request, f"{queryset.count()} supplier(s) verified.")
    verify_suppliers.short_description = "✓ Verify selected suppliers"

    def unverify_suppliers(self, request, queryset):
        queryset.update(verified=False)
        self.message_user(request, f"{queryset.count()} supplier(s) unverified.")
    unverify_suppliers.short_description = "✗ Unverify selected suppliers"

    def save_model(self, request, obj, form, change):
        if change and "verified" in form.changed_data:
            from apps.notifications.models import Notification
            if obj.verified:
                Notification.objects.create(
                    user=obj.owner,
                    type=Notification.Type.SHOP_VERIFIED,
                    title="🎉 Cold Storage verified!",
                    message=f"Your cold storage '{obj.name}' has been verified and is now visible to shops.",
                )
            else:
                Notification.objects.create(
                    user=obj.owner,
                    type=Notification.Type.SHOP_REJECTED,
                    title="❌ Verification removed",
                    message=f"Your cold storage '{obj.name}' has been unverified. Please contact support.",
                )
        super().save_model(request, obj, form, change)


@admin.register(ColdStorageProduct)
class ColdStorageProductAdmin(admin.ModelAdmin):
    list_display  = [
        "name", "cold_storage", "category","allowed_units_display", 
        "price_per_kg", "stock_kg", "stock_pieces","is_available",
    ]
    def allowed_units_display(self, obj):
        if not obj.allowed_units:
            return obj.unit_type
        return ", ".join(obj.allowed_units)
    allowed_units_display.short_description = "Units"
    list_filter = ["category", "is_available", "cold_storage", "allowed_units",]
    search_fields = ["name", "cold_storage__name"]
    list_editable = ["price_per_kg", "stock_kg", "is_available"]


@admin.register(B2BOrder)
class B2BOrderAdmin(admin.ModelAdmin):
    list_display = [
        "id", "shop", "cold_storage",
        "status_badge", "total_price", "created_at",
    ]
    list_filter   = ["status", "cold_storage"]
    search_fields = ["shop__name", "cold_storage__name"]
    ordering      = ["-created_at"]
    inlines       = [B2BOrderItemInline]
    readonly_fields = ["total_price", "created_at", "updated_at"]

    fieldsets = (
        (
            "Order Info",
            {
                "fields": ("shop", "cold_storage", "status", "notes"),
            },
        ),
        (
            "Pricing",
            {
                "fields": ("total_price",),
            },
        ),
        (
            "Meta",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    def status_badge(self, obj):
        colors = {
            "pending":    "orange",
            "confirmed":  "blue",
            "processing": "purple",
            "dispatched": "teal",
            "delivered":  "green",
            "cancelled":  "red",
        }
        color = colors.get(obj.status, "gray")
        return mark_safe(
            f'<span style="color:{color};font-weight:bold">{obj.get_status_display()}</span>'
        )
    status_badge.short_description = "Status"


@admin.register(B2BOrderStatusHistory)
class B2BOrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display  = ["order", "from_status", "to_status", "changed_by", "created_at"]
    list_filter   = ["to_status"]
    search_fields = ["order__id"]
    readonly_fields = ["order", "from_status", "to_status", "changed_by", "created_at"]