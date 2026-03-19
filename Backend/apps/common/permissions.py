# apps/common/permissions.py
from rest_framework.permissions import BasePermission


class IsShopOwner(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_shop_owner()
        )


class IsOwnerOfShop(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user