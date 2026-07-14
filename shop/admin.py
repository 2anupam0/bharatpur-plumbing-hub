from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.urls import reverse
from .models import Category, Product, ContactInquiry, SiteSettings


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name", "slug", "icon", "get_product_count",
        "is_active", "sort_order",
    ]
    list_editable = ["is_active", "sort_order", "icon"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]
    list_filter = ["is_active"]
    list_per_page = 20

    def get_product_count(self, obj):
        count = obj.get_product_count()
        color = "#16a34a" if count > 0 else "#94a3b8"
        return format_html(
            '<span style="font-weight:600;color:{};">{}</span>',
            color, count,
        )
    get_product_count.short_description = "Products"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "image_preview", "name", "category_badge", "price",
        "is_featured", "is_active", "stock_display", "original_price",
    ]
    list_filter = [
        "category", "is_featured", "is_active",
        ("created_at", admin.DateFieldListFilter),
    ]
    list_editable = ["is_featured", "is_active"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "description", "brand"]
    list_per_page = 20
    readonly_fields = ["created_at", "updated_at"]
    save_on_top = True

    fieldsets = (
        ("Basic Info", {
            "fields": ("name", "slug", "category", "brand", "unit"),
        }),
        ("Pricing", {
            "fields": ("price", "original_price"),
        }),
        ("Details", {
            "fields": ("description", "short_description", "image"),
        }),
        ("Inventory", {
            "fields": ("stock",),
        }),
        ("Status", {
            "fields": ("is_active", "is_featured"),
        }),
        ("Timestamps", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:42px;height:42px;border-radius:8px;object-fit:cover;border:1px solid #e2e8f0;" />',
                obj.image.url,
            )
        return mark_safe(
            '<div style="width:42px;height:42px;border-radius:8px;background:#f1f5f9;display:flex;align-items:center;justify-content:center;color:#94a3b8;font-size:18px;border:1px solid #e2e8f0;">📦</div>'
        )
    image_preview.short_description = ""

    def category_badge(self, obj):
        return format_html(
            '<span style="padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;background:#dbeafe;color:#1d4ed8;">{}</span>',
            obj.category.name,
        )
    category_badge.short_description = "Category"

    def price_display(self, obj):
        if obj.original_price and obj.original_price > obj.price:
            discount = int(((obj.original_price - obj.price) / obj.original_price) * 100)
            return format_html(
                '<div style="font-weight:700;">Rs {:.0f}</div>'
                '<div style="font-size:11px;color:#94a3b8;text-decoration:line-through;">Rs {:.0f}</div>'
                '<div style="font-size:10px;color:#dc2626;font-weight:600;">-{}%</div>',
                obj.price, obj.original_price, discount,
            )
        return format_html('<div style="font-weight:700;">Rs {:.0f}</div>', obj.price)
    price_display.short_description = "Price"
    price_display.admin_order_field = "price"

    def stock_display(self, obj):
        if obj.stock == 0:
            return format_html(
                '<span class="stock-badge out-of-stock"><i class="fas fa-times-circle"></i> Out</span>',
            )
        elif obj.stock <= 5:
            return format_html(
                '<span class="stock-badge low-stock"><i class="fas fa-exclamation-circle"></i> {}</span>',
                obj.stock,
            )
        return format_html(
            '<span class="stock-badge in-stock"><i class="fas fa-check-circle"></i> {}</span>',
            obj.stock,
        )
    stock_display.short_description = "Stock"
    stock_display.admin_order_field = "stock"


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = [
        "name", "phone", "inquiry_type_badge", "message_preview",
        "created_at", "is_resolved",
    ]
    list_filter = ["inquiry_type", "is_resolved", "created_at"]
    list_editable = ["is_resolved"]
    search_fields = ["name", "phone", "message"]
    readonly_fields = ["created_at"]
    list_per_page = 25
    date_hierarchy = "created_at"

    fieldsets = (
        ("Contact Info", {
            "fields": ("name", "phone", "email"),
        }),
        ("Inquiry", {
            "fields": ("inquiry_type", "message"),
        }),
        ("Status", {
            "fields": ("is_resolved", "created_at"),
        }),
    )

    def has_add_permission(self, request):
        return False

    def inquiry_type_badge(self, obj):
        colors = {
            "general": ("#f1f5f9", "#64748b"),
            "bulk": ("#fef3c7", "#92400e"),
            "contractor": ("#cffafe", "#164e63"),
            "delivery": ("#dcfce7", "#166534"),
        }
        bg, fg = colors.get(obj.inquiry_type, ("#f1f5f9", "#64748b"))
        return format_html(
            '<span style="padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;background:{};color:{};">{}</span>',
            bg, fg, obj.get_inquiry_type_display(),
        )
    inquiry_type_badge.short_description = "Type"

    def message_preview(self, obj):
        msg = obj.message[:60] + "..." if len(obj.message) > 60 else obj.message
        return format_html('<span style="color:#64748b;">{}</span>', msg)
    message_preview.short_description = "Message"

    def status_badge(self, obj):
        if obj.is_resolved:
            return format_html(
                '<span class="stock-badge in-stock"><i class="fas fa-check"></i> Resolved</span>',
            )
        return format_html(
            '<span class="stock-badge low-stock"><i class="fas fa-clock"></i> Pending</span>',
        )
    status_badge.short_description = "Status"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ["whatsapp_number", "free_delivery_threshold", "delivery_fee"]
    fieldsets = (
        ("WhatsApp Configuration", {
            "description": "Configure the WhatsApp number for customer ordering.",
            "fields": ("whatsapp_number",),
        }),
        ("Delivery Settings", {
            "description": "Configure delivery fees and free delivery thresholds.",
            "fields": ("free_delivery_threshold", "delivery_fee"),
        }),
        ("Announcements", {
            "description": "Set an announcement message shown on the website header. Leave empty to hide.",
            "fields": ("announcement_text",),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        SiteSettings.load()
        return super().changelist_view(request, extra_context)

    def has_view_permission(self, request, obj=None):
        return True


admin.site.site_header = "Bharatpur Plumbing Hub"
admin.site.site_title = "Plumbing Hub Admin"
admin.site.index_title = "Dashboard"
