# apps/common/permissions.py
from rest_framework.permissions import BasePermission


class IsShopOwner(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "shop_owner"
        )


class IsOwnerOfShop(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsColdStorage(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "cold_storage"
        )


class IsShopOwnerOrColdStorage(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ["shop_owner", "cold_storage"]
        )


class IsColdStorageOrStaff(BasePermission):
    """
    Allows cold_storage owners AND their staff members.
    Staff must have the owner FK pointing to a cold_storage user.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role == "cold_storage":
            return True

        if request.user.role == "staff" and request.user.owner is not None:
            return request.user.owner.role == "cold_storage"

        return False
