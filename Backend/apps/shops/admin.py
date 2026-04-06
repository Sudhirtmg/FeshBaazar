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
        "is_walkin",
        "address",
        "location_link",
        "verification_badge",
        "is_open_now",
        "is_temporarily_closed",
        "created_at",
    ]
    list_filter = ["is_verified", "is_walkin", "is_temporarily_closed", "city"]
    search_fields = ["name", "owner__phone"]
    list_editable = ["is_temporarily_closed"]
    # -------------------------change start-------------------------
    # unverified shops sorted to top so admin sees them first
    ordering = ["is_verified", "-created_at"]
    # -------------------------change end-------------------------
    inlines = [ShopScheduleInline]
    readonly_fields = ["created_at", "slug", "map_preview"]

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
                    "is_walkin",
                    "latitude",
                    "longitude",
                    "map_preview",
                    "logo",
                )
            },
        ),
        (
            "Verification",
            {
                "fields": ("is_verified", "verification_status", "rejection_reason"),
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
    def verification_badge(self, obj):
        colors = {
            "verified": "green",
            "pending": "orange",
            "rejected": "red",
        }
        color = colors.get(obj.verification_status, "gray")
        return mark_safe(
            f'<span style="color:{color};font-weight:bold">{obj.verification_status.title()}</span>'
        )

    verification_badge.short_description = "Status"

    def is_open_now(self, obj):
        if obj.is_open:
            return mark_safe('<span style="color:green">Open</span>')
        return mark_safe('<span style="color:red">Closed</span>')

    is_open_now.short_description = "Now"
    # -------------------------add end-------------------------

    def verify_shops(self, request, queryset):
        for shop in queryset:
            shop.is_verified = True
            shop.verification_status = "verified"
            shop.rejection_reason = ""
            shop.save()
            from apps.notifications.models import Notification

            Notification.objects.create(
                user=shop.owner,
                type=Notification.Type.SHOP_VERIFIED,
                title="🎉 Shop verified!",
                message=f"Your shop '{shop.name}' has been verified and is now live.",
            )
        self.message_user(request, f"{queryset.count()} shop(s) verified.")

    verify_shops.short_description = "✓ Verify selected shops"

    def unverify_shops(self, request, queryset):
        for shop in queryset:
            shop.is_verified = False
            shop.verification_status = "rejected"
            shop.save()
            from apps.notifications.models import Notification

            Notification.objects.create(
                user=shop.owner,
                type=Notification.Type.SHOP_REJECTED,
                title="❌ Verification denied",
                message=f"Your shop '{shop.name}' was not verified. Please update your details and resubmit.",
            )
        self.message_user(request, f"{queryset.count()} shop(s) unverified.")

    unverify_shops.short_description = "✗ Unverify selected shops"

    # --------------Add-Start----------------
    def location_link(self, obj):
        if obj.latitude and obj.longitude and obj.latitude != 0 and obj.longitude != 0:
            url = f"https://www.google.com/maps?q={obj.latitude},{obj.longitude}"
            # --------------Upgrade-Start----------------
            return mark_safe(
                f'<a href="{url}" target="_blank" '
                f'style="color:#16a34a;font-weight:600;">📍 Open Map</a>'
            )
            # --------------Upgrade-End----------------
        return "No location"

    location_link.short_description = "Location"
    # --------------Add-End----------------

    def map_preview(self, obj):
        if obj.latitude and obj.longitude and obj.latitude != 0 and obj.longitude != 0:
            return mark_safe(
                f'<iframe width="100%" height="200" '
                f'src="https://maps.google.com/maps?q={obj.latitude},{obj.longitude}&z=15&output=embed"></iframe>'
            )
        return "No location"

    # --------------Add-Start--------------------------------
    def save_model(self, request, obj, form, change):
        if change and "is_verified" in form.changed_data:
            from apps.notifications.models import Notification

            if obj.is_verified:
                obj.verification_status = "verified"
                obj.rejection_reason = ""
                Notification.objects.create(
                    user=obj.owner,
                    type=Notification.Type.SHOP_VERIFIED,
                    title="🎉 Shop verified!",
                    message=f"Your shop '{obj.name}' has been verified and is now live.",
                )
            else:
                obj.verification_status = "rejected"
                Notification.objects.create(
                    user=obj.owner,
                    type=Notification.Type.SHOP_REJECTED,
                    title="❌ Verification denied",
                    message=f"Your shop '{obj.name}' was not verified. Please update your details and resubmit.",
                )
        super().save_model(request, obj, form, change)

    # --------------Add-End--------------------------------


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
