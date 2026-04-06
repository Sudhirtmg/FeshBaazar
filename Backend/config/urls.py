from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/auth/",      include("apps.accounts.urls")),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/cart/",      include("apps.cart.urls")),
    path("api/orders/",    include("apps.orders.urls")),
    path("api/shops/",     include("apps.shops.urls")),
    path("api/products/",  include("apps.products.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/b2b/", include("apps.b2b.urls")),

]

# ✅ Serve media files always in dev — not gated by DEBUG
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)