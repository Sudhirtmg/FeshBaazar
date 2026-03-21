# apps/accounts/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Custom manager — phone is the unique identifier, not username."""

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Phone number is required.")
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractUser):

    class Role(models.TextChoices):
        CUSTOMER       = "customer",        "Customer"
        SHOP_OWNER     = "shop_owner",      "Shop Owner"
        DELIVERY_RIDER = "delivery_rider",  "Delivery Rider"
        STAFF          = "staff",           "Staff"
        ADMIN          = "admin",           "Admin"

    # Remove username — phone is the login field
    username       = None
    email          = models.EmailField(unique=True, blank=True, null=True)
    phone          = models.CharField(max_length=20, unique=True)
    role           = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    profile_image  = models.ImageField(
        upload_to="profiles/", null=True, blank=True
    )

    USERNAME_FIELD  = "phone"
    REQUIRED_FIELDS = ["email"]   # asked when running createsuperuser

    objects = UserManager()

    # --- convenience helpers used in permissions ---
    def is_shop_owner(self):
        return self.role == self.Role.SHOP_OWNER

    def is_rider(self):
        return self.role == self.Role.DELIVERY_RIDER

    def is_admin_user(self):
        return self.role == self.Role.ADMIN

    def __str__(self):
        return f"{self.phone} ({self.get_role_display()})"