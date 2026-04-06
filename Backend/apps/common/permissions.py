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
    
class IsColdStorage(BasePermission):
    message = "Only cold storage accounts can access this endpoint."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_cold_storage()
        )


class IsShopOwnerOrColdStorage(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.is_shop_owner() or request.user.is_cold_storage())
        )
        
from rest_framework.permissions import BasePermission
from apps.accounts.models import User


class CanCollectPaymentOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        # Owner (cold storage) → full access
        if user.role == User.Role.COLD_STORAGE:
            return True

        # Staff → only POST (add payment)
        if user.role == User.Role.STAFF:
            return request.method == "POST"

        return False
    
#--------------Add-Start----------------
class IsColdStorageOrStaff(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return user.role in [
            User.Role.COLD_STORAGE,
            User.Role.STAFF
        ]
#--------------Add-End----------------

#--------------Add-Start----------------
class StaffPermission(BasePermission):
    """
    Generic permission checker for staff abilities
    Usage: StaffPermission("can_view_orders")
    """

    def __init__(self, permission_name=None):
        self.permission_name = permission_name

    def has_permission(self, request, view):
        user = request.user

        # Owner always allowed
        if user.role == User.Role.COLD_STORAGE:
            return True

        # Staff → check permission field
        if user.role == User.Role.STAFF:
            if not self.permission_name:
                return False
            return getattr(user, self.permission_name, False)

        return False
#--------------Add-End----------------