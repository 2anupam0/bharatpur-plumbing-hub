from django.urls import path
from . import owner_views

urlpatterns = [
    path("", owner_views.owner_dashboard, name="owner_dashboard"),
    path("products/", owner_views.owner_products, name="owner_products"),
    path("products/add/", owner_views.owner_product_add, name="owner_product_add"),
    path("products/<int:pk>/edit/", owner_views.owner_product_edit, name="owner_product_edit"),
    path("products/<int:pk>/delete/", owner_views.owner_product_delete, name="owner_product_delete"),
    path("products/search-api/", owner_views.owner_product_search_api, name="owner_product_search_api"),
    path("orders/", owner_views.owner_orders, name="owner_orders"),
    path("orders/<int:pk>/", owner_views.owner_order_detail, name="owner_order_detail"),
    path("orders/<int:pk>/create-bill/", owner_views.owner_order_to_bill, name="owner_order_to_bill"),
    path("bills/", owner_views.owner_bills, name="owner_bills"),
    path("bills/create/", owner_views.owner_bill_create, name="owner_bill_create"),
    path("bills/<int:pk>/", owner_views.owner_bill_detail, name="owner_bill_detail"),
    path("bills/<int:pk>/print/", owner_views.owner_bill_print, name="owner_bill_print"),
    path("bills/<int:pk>/update-status/", owner_views.owner_bill_update_status, name="owner_bill_update_status"),
]
