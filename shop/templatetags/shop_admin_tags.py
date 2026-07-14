from django import template
from django.db.models import Q, Count, F
from shop.models import Product, Category, ContactInquiry, SiteSettings

register = template.Library()


@register.simple_tag
def get_admin_stats():
    products = Product.objects.all()
    active_products = products.filter(is_active=True)
    inquiries = ContactInquiry.objects.all()
    settings = SiteSettings.load()

    return {
        "total_products": active_products.count(),
        "total_categories": Category.objects.filter(is_active=True).count(),
        "featured_products": active_products.filter(is_featured=True).count(),
        "total_inquiries": inquiries.count(),
        "pending_inquiries": inquiries.filter(is_resolved=False).count(),
        "low_stock_count": active_products.filter(stock__gt=0, stock__lte=5).count(),
        "out_of_stock_count": active_products.filter(stock=0).count(),
        "discounted_products": active_products.filter(
            original_price__isnull=False, original_price__gt=F("price")
        ).count(),
        "inactive_products": products.filter(is_active=False).count(),
        "whatsapp_number": settings.whatsapp_number,
    }


@register.simple_tag
def get_recent_products(count=8):
    return Product.objects.select_related("category").order_by("-created_at")[:count]


@register.simple_tag
def get_recent_inquiries(count=8):
    return ContactInquiry.objects.all()[:count]


@register.simple_tag
def get_category_stats():
    return Category.objects.filter(is_active=True).annotate(
        product_count=Count("products")
    ).order_by("-product_count")
