# b2b/urls.py
from django.urls import path
from apps.b2b.api.views.views import (
    ColdStorageListView,
    ColdStorageDetailView,
    MyColdStorageView,
    ColdStorageProductListCreateView,
    ColdStorageProductDetailView,
    B2BOrderCreateView,
    ShopB2BOrderListView,
    ColdStorageIncomingOrderListView,
    B2BOrderStatusUpdateView,
    SetPriceView,
    B2BOrderDetailView,  # ← ADD THIS
    MapLocationsView,  # ← ADD THIS if you use it here
    ShopOrderConfirmView,  # ← ADD THIS
    DailyReportView,
)
from apps.b2b.api.views.ledger_views import (
    LedgerListView,
    LedgerBalanceView,
    AddPaymentView,
)
from apps.b2b.api.views.Reports_View import ReportsView
from apps.b2b.api.views.ledger_views import ShopLedgerSummaryView

urlpatterns = [
    # Cold storage browsing (shop owners only)
    path("cold-storages/", ColdStorageListView.as_view()),
    path("cold-storages/<int:pk>/", ColdStorageDetailView.as_view()),
    # Cold storage owner dashboard
    path("my-cold-storage/", MyColdStorageView.as_view()),
    path("my-cold-storage/products/", ColdStorageProductListCreateView.as_view()),
    path("my-cold-storage/products/<int:pk>/", ColdStorageProductDetailView.as_view()),
    # B2B orders
    path("orders/", B2BOrderCreateView.as_view()),
    path("orders/my-shop/", ShopB2BOrderListView.as_view()),
    path("orders/incoming/", ColdStorageIncomingOrderListView.as_view()),
    path("orders/<int:pk>/", B2BOrderDetailView.as_view()),
    path("orders/<int:pk>/status/", B2BOrderStatusUpdateView.as_view()),
    # --------------Add-Start----------------
    path("orders/<int:pk>/confirm/", ShopOrderConfirmView.as_view()),
    # --------------Add-End----------------
    # NEW: Set price for piece-based orders
    path("orders/<int:pk>/set-price/", SetPriceView.as_view()),
    # Ledger APIs
    path("ledger/", LedgerListView.as_view()),
    path("ledger/balance/", LedgerBalanceView.as_view()),
    path("ledger/payment/", AddPaymentView.as_view()),
    path("reports/", ReportsView.as_view()),
    path("ledger/summary/", ShopLedgerSummaryView.as_view()),
    path("reports/daily/", DailyReportView.as_view()),
]
