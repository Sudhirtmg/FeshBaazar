# apps/accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, StaffActionLog
from django.db import models

# ---------------- INLINE FIRST ----------------
class StaffInline(admin.TabularInline):
    model = User
    fk_name = "owner"
    extra = 0
    fields = ("phone", "name", "role", "is_active")
    readonly_fields = ("phone",)

class MyStaffFilter(admin.SimpleListFilter):
    title = "My Staff"
    parameter_name = "my_staff"

    def lookups(self, request, model_admin):
        return (
            ("yes", "My Staff Only"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(owner=request.user)
        return queryset

# ---------------- USER ADMIN ----------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["-date_joined"]

    # ✅ now it works
    inlines = [StaffInline]

    # ---------------- COLOR ROLE ----------------
    def colored_role(self, obj):
        colors = {
            "customer": "gray",
            "shop_owner": "blue",
            "cold_storage": "purple",
            "staff": "green",
            "delivery_rider": "orange",
            "admin": "red",
        }
        return format_html(
            '<b style="color:{}">{}</b>',
            colors.get(obj.role, "black"),
            obj.get_role_display()
        )

    colored_role.short_description = "Role"

    # ---------------- DISPLAY ----------------
    list_display = ["phone", "name", "colored_role", "owner", "is_active"]
    list_filter = ["role", "is_active", "is_staff", MyStaffFilter]
    search_fields = ["phone", "email", "name"]
    readonly_fields = ["date_joined", "last_login"]

    # ---------------- ACTIONS ----------------
    actions = ["make_staff", "activate_users"]

    def make_staff(self, request, queryset):
        queryset.update(role="staff")

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Admin sees everything
        if request.user.is_superuser:
            return qs

        # Owner sees only their staff + themselves
        return qs.filter(models.Q(owner=request.user) | models.Q(id=request.user.id))
    
    def save_model(self, request, obj, form, change):
        if not obj.owner and obj.role == "staff":
            obj.owner = request.user  # auto assign owner
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if not request.user.is_superuser:
            if "owner" in form.base_fields:
                form.base_fields["owner"].disabled = True

        return form
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        extra_context["total_users"] = User.objects.count()
        extra_context["total_staff"] = User.objects.filter(role="staff").count()
        extra_context["total_active"] = User.objects.filter(is_active=True).count()

        return super().changelist_view(request, extra_context=extra_context)
    
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if obj is None:
            return True

        return obj.owner == request.user or obj == request.user
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if obj is None:
            return True

        return obj.owner == request.user

    # ---------------- FIELDSETS ----------------
    fieldsets = (
        ("🔑 Login Info", {
            "fields": ("phone", "password")
        }),

        ("👤 Personal Info", {
            "fields": ("name", "email", "profile_image")
        }),

        ("🏢 Role & Hierarchy", {
            "fields": ("role", "owner")
        }),

        ("⚡ Staff Permissions", {
            "fields": (
                "can_collect_payment",
                "can_view_ledger",
                "can_create_order",
                "can_manage_products",
                "can_view_orders",
                "can_deliver_orders",
                "can_confirm_orders",
            )
        }),

        ("🛡️ System Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),

        ("📅 Dates", {
            "fields": ("last_login", "date_joined")
        }),
    )

    # ---------------- CREATE USER ----------------
    add_fieldsets = (
        ("➕ Create User", {
            "classes": ("wide",),
            "fields": (
                "phone",
                "name",
                "email",
                "role",
                "owner",
                "password1",
                "password2",
            ),
        }),
    )


# ---------------- STAFF LOG ----------------
@admin.register(StaffActionLog)
class StaffActionLogAdmin(admin.ModelAdmin):
    list_display = ["staff", "action", "performed_by", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["staff__phone", "action"]
    readonly_fields = ["created_at"]