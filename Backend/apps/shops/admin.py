# from django.contrib import admin
# from .models import Shop


# admin.site.register(Shop)

# apps/shops/admin.py
from django.contrib import admin
from apps.shops.models import Shop, ShopSchedule


class ShopScheduleInline(admin.TabularInline):
    model  = ShopSchedule
    extra  = 0
    fields = [
        "weekday", "is_active",
        "morning_open", "morning_close",
        "afternoon_open", "afternoon_close",
    ]


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display   = [
        "name", "owner", "city",
        "is_verified", "is_temporarily_closed", "is_open", "created_at"
    ]
    list_filter    = ["is_verified", "is_temporarily_closed", "city"]
    search_fields  = ["name", "owner__phone"]
    list_editable  = ["is_verified", "is_temporarily_closed"]
    ordering       = ["-created_at"]
    inlines        = [ShopScheduleInline]

    actions = ["verify_shops", "unverify_shops"]

    def verify_shops(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f"{queryset.count()} shop(s) verified.")
    verify_shops.short_description = "Verify selected shops"

    def unverify_shops(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, f"{queryset.count()} shop(s) unverified.")
    unverify_shops.short_description = "Unverify selected shops"


@admin.register(ShopSchedule)
class ShopScheduleAdmin(admin.ModelAdmin):
    list_display = [
        "shop", "weekday", "is_active",
        "morning_open", "morning_close",
        "afternoon_open", "afternoon_close",
    ]
    list_filter  = ["weekday", "is_active"]