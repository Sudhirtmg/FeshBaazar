from django.db import models


class Notification(models.Model):

    class Type(models.TextChoices):
        SHOP_VERIFIED = "shop_verified", "Shop Verified"
        SHOP_REJECTED = "shop_rejected", "Shop Rejected"
        ORDER_STATUS  = "order_status",  "Order Status"
        B2B_ORDER_PLACED  = "b2b_order_placed",   "B2B Order Placed"
        B2B_ORDER_UPDATED = "b2b_order_updated",  "B2B Order Updated"
        LOW_STOCK = "low_stock", "Low Stock"

    user       = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type       = models.CharField(max_length=50, choices=Type.choices)
    title      = models.CharField(max_length=255)
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} — {self.title}"