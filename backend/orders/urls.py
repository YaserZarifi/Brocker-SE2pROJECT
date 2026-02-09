from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    # Orders
    path("", views.OrderListView.as_view(), name="order_list"),
    path("create/", views.OrderCreateView.as_view(), name="order_create"),
    path("<uuid:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
    path("<uuid:pk>/cancel/", views.OrderCancelView.as_view(), name="order_cancel"),
    # Portfolio
    path("portfolio/", views.portfolio_view, name="portfolio"),
    # Order Book
    path("book/<str:symbol>/", views.order_book_view, name="order_book"),
]
