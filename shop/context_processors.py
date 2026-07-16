from django.conf import settings
from .models import SiteSettings


_site_settings_cache = None


def site_context(request):
    global _site_settings_cache
    if _site_settings_cache is None:
        _site_settings_cache = SiteSettings.load()
    site_settings = _site_settings_cache

    cart_count = 0
    cart = request.session.get("cart")
    if cart:
        cart_count = sum(item["quantity"] for item in cart.values())

    return {
        "site_name": site_settings.shop_name,
        "site_tagline": site_settings.shop_tagline,
        "site_phone": site_settings.shop_phone,
        "site_email": site_settings.shop_email,
        "site_address": site_settings.shop_address,
        "site_opening_hours": site_settings.shop_opening_hours,
        "whatsapp_number": site_settings.whatsapp_number,
        "free_delivery_threshold": site_settings.free_delivery_threshold,
        "delivery_fee": site_settings.delivery_fee,
        "announcement_text": site_settings.announcement_text,
        "cart_count": cart_count,
    }
