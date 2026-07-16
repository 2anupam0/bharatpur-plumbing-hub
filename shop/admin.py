from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.urls import reverse
from .models import Category, Product, ContactInquiry, SiteSettings, Order, OrderItem, Bill, BillItem


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


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "product_name", "quantity", "unit_price", "total_price"]
    fields = ["product_name", "quantity", "unit_price", "total_price"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number_link", "customer_name", "customer_phone",
        "grand_total_display", "payment_status_badge",
        "order_status_badge", "source_badge", "created_at",
    ]
    list_filter = [
        "order_status", "payment_status", "source",
        "payment_method", "created_at",
    ]
    search_fields = ["order_number", "customer_name", "customer_phone"]
    readonly_fields = [
        "order_number", "subtotal", "tax_amount", "grand_total",
        "created_at", "updated_at", "created_by",
    ]
    list_per_page = 25
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]
    save_on_top = True

    def order_number_link(self, obj):
        url = f"/dashboard/orders/{obj.pk}/"
        return format_html('<a href="{}" style="color:#2563eb;font-weight:600;text-decoration:none;">{}</a>', url, obj.order_number)
    order_number_link.short_description = "Order"
    order_number_link.allow_tags = True

    fieldsets = (
        ("Order Info", {
            "fields": ("order_number", "source", "created_by", "created_at"),
        }),
        ("Customer", {
            "fields": ("customer_name", "customer_phone", "customer_email", "customer_address"),
        }),
        ("Pricing", {
            "fields": ("subtotal", "discount_amount", "tax_percent", "tax_amount", "delivery_fee", "grand_total"),
        }),
        ("Payment", {
            "fields": ("payment_method", "payment_status"),
        }),
        ("Status & Notes", {
            "fields": ("order_status", "notes"),
        }),
        ("Timestamps", {
            "classes": ("collapse",),
            "fields": ("updated_at",),
        }),
    )

    actions = ["mark_confirmed", "mark_delivered", "mark_paid"]

    def grand_total_display(self, obj):
        return format_html('<strong>Rs {}</strong>', f'{obj.grand_total:,.0f}')
    grand_total_display.short_description = "Total"

    def payment_status_badge(self, obj):
        colors = {
            "pending": ("#fef3c7", "#92400e"),
            "paid": ("#dcfce7", "#166534"),
            "partially_paid": ("#cffafe", "#164e63"),
            "cancelled": ("#fee2e2", "#991b1b"),
        }
        bg, fg = colors.get(obj.payment_status, ("#f1f5f9", "#64748b"))
        return format_html(
            '<span style="padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;background:{};color:{};">{}</span>',
            bg, fg, obj.get_payment_status_display(),
        )
    payment_status_badge.short_description = "Payment"

    def order_status_badge(self, obj):
        colors = {
            "pending": ("#fef3c7", "#92400e"),
            "confirmed": ("#dbeafe", "#1d4ed8"),
            "processing": ("#cffafe", "#164e63"),
            "shipped": ("#e0e7ff", "#3730a3"),
            "delivered": ("#dcfce7", "#166534"),
            "cancelled": ("#fee2e2", "#991b1b"),
        }
        bg, fg = colors.get(obj.order_status, ("#f1f5f9", "#64748b"))
        return format_html(
            '<span style="padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;background:{};color:{};">{}</span>',
            bg, fg, obj.get_order_status_display(),
        )
    order_status_badge.short_description = "Status"

    def source_badge(self, obj):
        colors = {
            "website": ("#dbeafe", "#1d4ed8"),
            "manual": ("#dcfce7", "#166534"),
            "phone": ("#fef3c7", "#92400e"),
        }
        bg, fg = colors.get(obj.source, ("#f1f5f9", "#64748b"))
        return format_html(
            '<span style="padding:3px 8px;border-radius:20px;font-size:10px;font-weight:600;background:{};color:{};">{}</span>',
            bg, fg, obj.get_source_display(),
        )
    source_badge.short_description = "Source"

    def mark_confirmed(self, request, queryset):
        queryset.update(order_status="confirmed")
    mark_confirmed.short_description = "Mark as Confirmed"

    def mark_delivered(self, request, queryset):
        queryset.update(order_status="delivered")
    mark_delivered.short_description = "Mark as Delivered"

    def mark_paid(self, request, queryset):
        queryset.update(payment_status="paid")
    mark_paid.short_description = "Mark as Paid"

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


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
        ("Tax Settings", {
            "description": "Configure tax percentage applied to orders.",
            "fields": ("tax_percent",),
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


class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 0
    readonly_fields = ["product", "product_name", "quantity", "unit_price", "total_price"]


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = [
        "bill_number_link", "customer_name", "grand_total",
        "payment_method", "status", "created_at",
    ]
    list_filter = ["status", "payment_method"]
    search_fields = ["bill_number", "customer_name", "customer_phone"]
    readonly_fields = ["bill_number", "subtotal", "tax_amount", "grand_total", "created_at", "updated_at"]
    inlines = [BillItemInline]
    list_per_page = 20

    def bill_number_link(self, obj):
        url = f"/dashboard/bills/{obj.pk}/"
        return format_html('<a href="{}" style="color:#2563eb;font-weight:600;text-decoration:none;">{}</a>', url, obj.bill_number)
    bill_number_link.short_description = "Bill Number"
    bill_number_link.allow_tags = True

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status in ("paid", "cancelled"):
            return [f.name for f in Bill._meta.get_fields() if hasattr(f, "name")]
        return self.readonly_fields


admin.site.site_header = "Bharatpur Plumbing Hub"
admin.site.site_title = "Plumbing Hub Admin"
admin.site.index_title = "Dashboard"
