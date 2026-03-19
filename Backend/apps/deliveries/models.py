from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from apps.orders.models import Order

User = settings.AUTH_USER_MODEL


class Delivery(models.Model):

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="delivery"
    )

    rider = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deliveries"
    )

    assigned_at = models.DateTimeField(null=True, blank=True)

    picked_up_at = models.DateTimeField(null=True, blank=True)

    delivered_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=30,
        default="pending"
    )