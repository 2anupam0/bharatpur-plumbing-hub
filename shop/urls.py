from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("contact/", views.contact, name="contact"),
    path("delivery/", views.delivery_info, name="delivery_info"),
    path("about/", views.about, name="about"),
    path("cart/", views.cart_page, name="cart_page"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:product_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("order/<str:order_number>/", views.order_confirmation, name="order_confirmation"),
    path("order/<str:order_number>/invoice/", views.order_invoice, name="order_invoice"),
]
