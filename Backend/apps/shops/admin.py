# from django.contrib import admin
# from .models import Shop


# admin.site.register(Shop)

# apps/shops/admin.py

from django.contrib import admin
from django.utils.html import mark_safe
from apps.shops.models import Shop, ShopSchedule


class ShopScheduleInline(admin.TabularInline):
    model = ShopSchedule
    extra = 0
    fields = [
        "weekday",
        "is_active",
        "morning_open",
        "morning_close",
        "afternoon_open",
        "afternoon_close",
    ]


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "owner",
        "city",
        # -------------------------change start-------------------------
        # replaced "is_verified" and "is_open" with colored badge methods
        "verification_status",
        "is_open_now",
        # -------------------------change end-------------------------
        "is_temporarily_closed",
        "created_at",
    ]
    list_filter = ["is_verified", "is_temporarily_closed", "city"]
    search_fields = ["name", "owner__phone"]
    list_editable = ["is_temporarily_closed"]
    # -------------------------change start-------------------------
    # unverified shops sorted to top so admin sees them first
    ordering = ["is_verified", "-created_at"]
    # -------------------------change end-------------------------
    inlines = [ShopScheduleInline]
    readonly_fields = ["created_at", "slug"]

    # -------------------------add start-------------------------
    fieldsets = (
        (
            "Shop info",
            {
                "fields": (
                    "owner",
                    "name",
                    "slug",
                    "description",
                    "phone",
                    "address",
                    "city",
                    "logo",
                )
            },
        ),
        (
            "Verification",
            {
                "fields": ("is_verified",),
                "description": "⚠️ Verify only after confirming shop info is accurate.",
            },
        ),
        (
            "Delivery",
            {
                "fields": ("has_delivery", "delivery_charge"),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_temporarily_closed", "temporary_close_note"),
            },
        ),
        (
            "Meta",
            {
                "fields": ("created_at",),
            },
        ),
    )
    # -------------------------add end-------------------------

    actions = ["verify_shops", "unverify_shops"]

    # -------------------------add start-------------------------
    def verification_status(self, obj):
        if obj.is_verified:
            return mark_safe(
                '<span style="color:green;font-weight:bold">Verified</span>'
            )
        return mark_safe('<span style="color:orange;font-weight:bold">Pending</span>')

    verification_status.short_description = "Status"

    def is_open_now(self, obj):
        if obj.is_open:
            return mark_safe('<span style="color:green">Open</span>')
        return mark_safe('<span style="color:red">Closed</span>')

    is_open_now.short_description = "Now"
    # -------------------------add end-------------------------

    def verify_shops(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f"{queryset.count()} shop(s) verified.")

    verify_shops.short_description = "✓ Verify selected shops"

    def unverify_shops(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, f"{queryset.count()} shop(s) unverified.")

    unverify_shops.short_description = "✗ Unverify selected shops"


@admin.register(ShopSchedule)
class ShopScheduleAdmin(admin.ModelAdmin):
    list_display = [
        "shop",
        "weekday",
        "is_active",
        "morning_open",
        "morning_close",
        "afternoon_open",
        "afternoon_close",
    ]
    list_filter = ["weekday", "is_active"]
