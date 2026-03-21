# apps/orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderStatusHistoryInline(admin.TabularInline):
    model           = OrderStatusHistory
    extra           = 0
    readonly_fields = ["from_status", "to_status", "changed_by", "created_at"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ["id", "customer", "shop", "total_amount", "status", "created_at"]
    list_filter   = ["status", "payment_method"]
    search_fields = ["customer__phone", "shop__name"]
    inlines       = [OrderItemInline, OrderStatusHistoryInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display  = ["order", "product_name", "cut_type_name", "quantity", "unit_price", "total_price"]
    search_fields = ["product_name", "order__id"]


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display  = ["order", "from_status", "to_status", "changed_by", "created_at"]
    search_fields = ["order__id"]