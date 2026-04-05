# apps/b2b/urls.py
from django.urls import path
from apps.b2b.api.views.b2b_views import (
    ColdStorageListView,
    ColdStorageDetailView,
    MyColdStorageView,
    ColdStorageProductListCreateView,
    ColdStorageProductDetailView,
    B2BOrderCreateView,
    ShopB2BOrderListView,
    ColdStorageIncomingOrderListView,
    B2BOrderDetailView,
    B2BOrderStatusUpdateView,
    SetPriceView,
    ShopOrderConfirmView,
    MapLocationsView,
    DailyReportView,
)
from apps.b2b.api.views.ledger_views import (
    LedgerListView,
    LedgerBalanceView,
    AddPaymentView,
    ShopLedgerSummaryView,
    StaffCollectionSummaryView,
    AllStaffCollectionView,
)

urlpatterns = [
    # Cold Storage browsing (shop owners)
    path("cold-storages/",              ColdStorageListView.as_view(),          name="cold-storage-list"),
    path("cold-storages/<int:pk>/",     ColdStorageDetailView.as_view(),        name="cold-storage-detail"),

    # Cold Storage owner dashboard
    path("my-cold-storage/",            MyColdStorageView.as_view(),            name="my-cold-storage"),
    path("my-cold-storage/products/",   ColdStorageProductListCreateView.as_view(), name="cs-product-list"),
    path("my-cold-storage/products/<int:pk>/", ColdStorageProductDetailView.as_view(), name="cs-product-detail"),

    # Orders
    path("orders/",                     B2BOrderCreateView.as_view(),           name="b2b-order-create"),
    path("orders/my-shop/",             ShopB2BOrderListView.as_view(),         name="b2b-order-shop"),
    path("orders/incoming/",            ColdStorageIncomingOrderListView.as_view(), name="b2b-order-incoming"),
    path("orders/<int:pk>/",            B2BOrderDetailView.as_view(),           name="b2b-order-detail"),
    path("orders/<int:pk>/status/",     B2BOrderStatusUpdateView.as_view(),     name="b2b-order-status"),
    path("orders/<int:pk>/set-price/",  SetPriceView.as_view(),                 name="b2b-set-price"),
    path("orders/<int:pk>/confirm/",    ShopOrderConfirmView.as_view(),         name="b2b-order-confirm"),

    # Ledger
    path("ledger/",                     LedgerListView.as_view(),               name="ledger-list"),
    path("ledger/balance/",             LedgerBalanceView.as_view(),            name="ledger-balance"),
    path("ledger/payment/",             AddPaymentView.as_view(),               name="ledger-payment"),
    path("ledger/summary/",             ShopLedgerSummaryView.as_view(),        name="ledger-summary"),
    path("ledger/staff-summary/",       StaffCollectionSummaryView.as_view(),   name="ledger-staff-summary"),
    path("ledger/all-staff/",           AllStaffCollectionView.as_view(),       name="ledger-all-staff"),

    # Reports & map (both singular and plural supported)
    path("report/daily/",               DailyReportView.as_view(),              name="b2b-daily-report"),
    path("reports/daily/",              DailyReportView.as_view(),              name="b2b-daily-report-alias"),
    path("map/",                        MapLocationsView.as_view(),             name="b2b-map"),
]
