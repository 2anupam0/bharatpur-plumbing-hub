from django.urls import path
from . import admin_panel_views as views

urlpatterns = [
    path("", views.admin_dashboard, name="admin_panel_dashboard"),
    path("login/", views.admin_login, name="admin_panel_login"),
    path("logout/", views.admin_logout, name="admin_panel_logout"),
    path("users/", views.admin_users, name="admin_panel_users"),
    path("users/add/", views.admin_user_add, name="admin_panel_user_add"),
    path("users/<int:pk>/edit/", views.admin_user_edit, name="admin_panel_user_edit"),
    path("users/<int:pk>/delete/", views.admin_user_delete, name="admin_panel_user_delete"),
    path("products/", views.admin_products, name="admin_panel_products"),
    path("products/add/", views.admin_product_add, name="admin_panel_product_add"),
    path("products/<int:pk>/edit/", views.admin_product_edit, name="admin_panel_product_edit"),
    path("products/<int:pk>/delete/", views.admin_product_delete, name="admin_panel_product_delete"),
    path("categories/", views.admin_categories, name="admin_panel_categories"),
    path("categories/add/", views.admin_category_add, name="admin_panel_category_add"),
    path("categories/<int:pk>/edit/", views.admin_category_edit, name="admin_panel_category_edit"),
    path("categories/<int:pk>/delete/", views.admin_category_delete, name="admin_panel_category_delete"),
    path("orders/", views.admin_orders, name="admin_panel_orders"),
    path("orders/<int:pk>/", views.admin_order_detail, name="admin_panel_order_detail"),
    path("bills/", views.admin_bills, name="admin_panel_bills"),
    path("bills/<int:pk>/", views.admin_bill_detail, name="admin_panel_bill_detail"),
    path("inquiries/", views.admin_inquiries, name="admin_panel_inquiries"),
    path("inquiries/<int:pk>/", views.admin_inquiry_detail, name="admin_panel_inquiry_detail"),
    path("settings/", views.admin_settings, name="admin_panel_settings"),
]
