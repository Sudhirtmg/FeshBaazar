# apps/shops/models.py
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
import uuid
from decimal import Decimal

class Shop(models.Model):
    owner       = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="shops",
    )
    name        = models.CharField(max_length=255)
    slug        = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    address     = models.CharField(max_length=255, blank=True)
    city        = models.CharField(max_length=100, blank=True)
    is_walkin = models.BooleanField(default=False)
    phone       = models.CharField(max_length=20, blank=True)
    logo        = models.ImageField(upload_to="shops/logos/", null=True, blank=True)
    is_verified         = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('verified', 'Verified'), ('rejected', 'Rejected')],
        default='pending',
    )
    rejection_reason    = models.TextField(blank=True)

    # ✅ Delivery settings
    #-----------------------ADD-START----------------------------------------------------
    has_delivery    = models.BooleanField(default=True)
    delivery_charge = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("50.00")
    )
    #-----------------------ADD-END------------------------------------------------------

    # ✅ Manual override
    is_temporarily_closed = models.BooleanField(default=False)
    temporary_close_note  = models.CharField(max_length=255, blank=True)

    # ✅ Manual override — owner can force close for the day
    is_temporarily_closed = models.BooleanField(default=False)
    temporary_close_note  = models.CharField(max_length=255, blank=True)

    created_at  = models.DateTimeField(auto_now_add=True)
    #--------------Add-Start--------------------------------
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.owner.role == "cold_storage":
             self.is_walkin = True
        if not self.slug:
            base = slugify(self.name) or "shop"
            self.slug = base + "-" + str(uuid.uuid4())[:6]
        #-------------------------add start-------------------------
        # Auto-unverify when shop info changes (except schedule/status fields)
        if self.pk:
            try:
                old = Shop.objects.get(pk=self.pk)
                info_fields = ['name', 'address', 'city', 'phone', 'description']
                changed = any(getattr(old, f) != getattr(self, f) for f in info_fields)
                if changed and self.is_verified:
                    self.is_verified = False
            except Shop.DoesNotExist:
                pass
        #-------------------------add end-------------------------
        super().save(*args, **kwargs)

    @property
    def is_open(self):
        if self.is_temporarily_closed:
            return False

        now          = timezone.localtime(timezone.now())
        day          = now.weekday()
        current_time = now.time().replace(second=0, microsecond=0)  # ✅ strip seconds

        schedule = self.schedules.filter(weekday=day, is_active=True)

        for slot in schedule:
            if slot.morning_open and slot.morning_close:
                if slot.morning_open <= current_time <= slot.morning_close:
                    return True
            if slot.afternoon_open and slot.afternoon_close:
                if slot.afternoon_open <= current_time <= slot.afternoon_close:
                    return True

        return False

    @property
    def next_opening(self):
        now       = timezone.localtime(timezone.now())
        today     = now.weekday()
        curr_time = now.time()

        for offset in range(7):
            day   = (today + offset) % 7
            slots = self.schedules.filter(weekday=day, is_active=True)

            for slot in slots:
                if offset == 0:
                    # ✅ Check morning first, then afternoon
                    if slot.morning_open and slot.morning_open > curr_time:
                        return f"today at {slot.morning_open.strftime('%I:%M %p')}"
                    if slot.afternoon_open and slot.afternoon_open > curr_time:
                        return f"today at {slot.afternoon_open.strftime('%I:%M %p')}"
                else:
                    day_name = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][day]
                    if slot.morning_open:
                        return f"{day_name} at {slot.morning_open.strftime('%I:%M %p')}"

        return None

    def __str__(self):
        return self.name


WEEKDAYS = [
    (0, "Monday"),
    (1, "Tuesday"),
    (2, "Wednesday"),
    (3, "Thursday"),
    (4, "Friday"),
    (5, "Saturday"),
    (6, "Sunday"),
]


class ShopSchedule(models.Model):
    shop            = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    weekday         = models.IntegerField(choices=WEEKDAYS)
    is_active       = models.BooleanField(default=True)  # False = closed that day

    # Morning slot e.g. 6:00 AM – 11:00 AM
    morning_open    = models.TimeField(null=True, blank=True)
    morning_close   = models.TimeField(null=True, blank=True)

    # Afternoon slot e.g. 2:00 PM – 6:00 PM
    afternoon_open  = models.TimeField(null=True, blank=True)
    afternoon_close = models.TimeField(null=True, blank=True)
    #-------------------------add start-------------------------
    close_note      = models.CharField(max_length=255, blank=True)
    #-------------------------add end-------------------------

    class Meta:
        unique_together = ["shop", "weekday"]
        ordering        = ["weekday"]

    def __str__(self):
        return f"{self.shop.name} — {self.get_weekday_display()}"