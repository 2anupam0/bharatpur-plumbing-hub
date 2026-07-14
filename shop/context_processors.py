from django.conf import settings
from .models import SiteSettings


_site_settings_cache = None


def site_context(request):
    global _site_settings_cache
    if _site_settings_cache is None:
        _site_settings_cache = SiteSettings.load()
    site_settings = _site_settings_cache
    return {
        "site_name": getattr(settings, "SITE_NAME", "Bharatpur Plumbing Hub"),
        "site_tagline": getattr(settings, "SITE_TAGLINE", "All Plumbing & Hardware Materials"),
        "site_phone": getattr(settings, "SITE_PHONE", "+9779800000000"),
        "site_email": getattr(settings, "SITE_EMAIL", "info@bharatpurplumbing.com"),
        "site_address": getattr(settings, "SITE_ADDRESS", "Bharatpur, Chitwan, Nepal"),
        "site_opening_hours": getattr(settings, "SITE_OPENING_HOURS", "Sun-Fri: 8AM-7PM"),
        "whatsapp_number": site_settings.whatsapp_number,
        "free_delivery_threshold": site_settings.free_delivery_threshold,
        "announcement_text": site_settings.announcement_text,
    }
