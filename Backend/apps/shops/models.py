# apps/shops/models.py
from django.db import models
from django.utils.text import slugify


class Shop(models.Model):
    owner       = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="shops",
        limit_choices_to={"role": "shop_owner"},
    )
    name        = models.CharField(max_length=255)
    slug        = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    phone       = models.CharField(max_length=20)
    address     = models.TextField()
    city        = models.CharField(max_length=100)
    latitude    = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude   = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    is_open     = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    has_delivery = models.BooleanField(default=True)  
    has_pickup   = models.BooleanField(default=True)
    delivery_charge = models.DecimalField(max_digits=8, decimal_places=2, default=50.00)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            n    = 1
            # handles duplicate names: "moms-shop", "moms-shop-2", etc.
            while Shop.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n   += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.city})"