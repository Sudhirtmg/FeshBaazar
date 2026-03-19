# apps/products/models.py
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name       = models.CharField(max_length=100)
    slug       = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):

    class Unit(models.TextChoices):
        KG    = "kg",    "Kilogram"
        PIECE = "piece", "Piece"
        PACK  = "pack",  "Pack"

    shop           = models.ForeignKey(
        "shops.Shop",
        on_delete=models.CASCADE,
        related_name="products",
    )
    category       = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    name           = models.CharField(max_length=255)
    slug           = models.SlugField(blank=True)
    description    = models.TextField(blank=True)
    price          = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    stock_quantity = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    unit           = models.CharField(
        max_length=20, choices=Unit.choices, default=Unit.KG
    )
    image          = models.ImageField(
        upload_to="products/", null=True, blank=True
    )
    is_available   = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("shop", "slug")

    @property
    def effective_price(self):
        return self.discount_price if self.discount_price else self.price

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            n    = 1
            while Product.objects.filter(
                shop_id=self.shop_id,  # ← fix is here
                slug=slug
            ).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n   += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
         return self.name 


class CutType(models.Model):
    product     = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cut_types",
    )
    name        = models.CharField(max_length=100)
    extra_price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0
    )
    is_active   = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (+Rs.{self.extra_price})"