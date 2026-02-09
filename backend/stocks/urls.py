from django.urls import path

from . import views

app_name = "stocks"

urlpatterns = [
    # Public endpoints
    path("", views.StockListView.as_view(), name="stock_list"),
    path("stats/", views.market_stats, name="market_stats"),
    path("<str:symbol>/", views.StockDetailView.as_view(), name="stock_detail"),
    path("<str:symbol>/history/", views.StockPriceHistoryView.as_view(), name="stock_price_history"),
    # Admin endpoints
    path("admin/manage/", views.AdminStockListCreateView.as_view(), name="admin_stock_list_create"),
    path("admin/manage/<str:symbol>/", views.AdminStockDetailView.as_view(), name="admin_stock_detail"),
]
