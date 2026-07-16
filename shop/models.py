import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


def generate_unique_slug(instance, base_slug, model_class, slug_field="slug"):
    slug = base_slug
    counter = 1
    while model_class.objects.filter(**{slug_field: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=50,
        default="🔧",
        help_text="Emoji icon for the category",
    )
    image = models.ImageField(upload_to="categories/", blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, slugify(self.name), Category)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_product_count(self):
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        help_text="Original price before discount (optional)"
    )
    description = models.TextField()
    short_description = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to="products/", blank=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    unit = models.CharField(
        max_length=20, default="piece",
        choices=[
            ("piece", "Piece"),
            ("kg", "Kilogram (kg)"),
            ("meter", "Meter"),
            ("inch", "Inch"),
            ("foot", "Foot"),
            ("yard", "Yard"),
            ("liter", "Liter"),
            ("box", "Box"),
            ("set", "Set"),
            ("roll", "Roll"),
            ("pipe", "Pipe"),
            ("fitting", "Fitting"),
            ("custom", "Custom"),
        ],
        help_text="Unit of measurement"
    )
    brand = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, slugify(self.name), Product)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def has_discount(self):
        return self.original_price and self.original_price > self.price

    def discount_percentage(self):
        if self.has_discount():
            return int(
                ((self.original_price - self.price) / self.original_price) * 100
            )
        return 0

    def is_in_stock(self):
        return self.stock > 0

    def get_all_images(self):
        images = list(self.additional_images.all().order_by('sort_order'))
        if self.image:
            images.insert(0, type('Obj', (), {'image': self.image, 'is_primary': True})())
        return images


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='products/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return f"Image for {self.product.name} #{self.sort_order}"


class ProductVideo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='videos')
    video_url = models.URLField(help_text="YouTube or Vimeo URL")
    caption = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return f"Video for {self.product.name} #{self.sort_order}"

    def get_embed_url(self):
        url = self.video_url
        if 'youtube.com/watch' in url:
            video_id = url.split('v=')[-1].split('&')[0]
            return f'https://www.youtube.com/embed/{video_id}'
        elif 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[-1].split('?')[0]
            return f'https://www.youtube.com/embed/{video_id}'
        elif 'vimeo.com/' in url:
            video_id = url.split('vimeo.com/')[-1].split('?')[0]
            return f'https://player.vimeo.com/video/{video_id}'
        return url


class ContactInquiry(models.Model):
    INQUIRY_TYPES = [
        ("general", "General Inquiry"),
        ("bulk", "Bulk Order"),
        ("contractor", "Contractor Inquiry"),
        ("delivery", "Delivery Inquiry"),
    ]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    inquiry_type = models.CharField(
        max_length=20, choices=INQUIRY_TYPES, default="general"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.get_inquiry_type_display()}"


class SiteSettings(models.Model):
    whatsapp_number = models.CharField(
        max_length=20, default="+9779800000000",
        help_text="WhatsApp number with country code"
    )
    free_delivery_threshold = models.DecimalField(
        max_digits=10, decimal_places=2, default=5000.00
    )
    delivery_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=150.00
    )
    tax_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=13.00,
        help_text="Tax percentage (e.g. 13 for Nepal VAT)"
    )
    announcement_text = models.CharField(
        max_length=255, blank=True,
        help_text="Announcement bar text (leave empty to hide)"
    )

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("bank_transfer", "Bank Transfer"),
        ("esewa", "eSewa"),
        ("khalti", "Khalti"),
        ("cod", "Cash on Delivery"),
    ]
    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("partially_paid", "Partially Paid"),
        ("cancelled", "Cancelled"),
    ]
    SOURCE_CHOICES = [
        ("website", "Website"),
        ("manual", "Manual"),
        ("phone", "Phone"),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True, default="")
    customer_address = models.TextField(blank=True, default="")

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=13.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="cash")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending")
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="website")
    notes = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order_number} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            today = uuid.uuid4().hex[:6].upper()
            self.order_number = f"ORD-{self.created_at.strftime('%Y%m%d') if self.created_at else uuid.uuid4().hex[:8].upper()}-{today}"
        super().save(*args, **kwargs)

    def recalculate_totals(self):
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.tax_amount = (self.subtotal - self.discount_amount) * self.tax_percent / 100
        self.grand_total = self.subtotal - self.discount_amount + self.tax_amount + self.delivery_fee
        self.save(update_fields=["subtotal", "tax_amount", "grand_total"])

    def item_count(self):
        return self.items.count()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class Bill(models.Model):
    BILL_STATUS_CHOICES = [
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("bank_transfer", "Bank Transfer"),
        ("esewa", "eSewa"),
        ("khalti", "Khalti"),
        ("ime_pay", "IME Pay"),
        ("qr_code", "QR Code Payment"),
    ]

    bill_number = models.CharField(max_length=20, unique=True, editable=False)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20, blank=True, default="")
    customer_address = models.TextField(blank=True, default="")

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=13.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="cash")
    status = models.CharField(max_length=20, choices=BILL_STATUS_CHOICES, default="draft")
    notes = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.bill_number} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.bill_number:
            today = uuid.uuid4().hex[:6].upper()
            self.bill_number = f"BILL-{today}"
        super().save(*args, **kwargs)

    def recalculate_totals(self):
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.tax_amount = (self.subtotal - self.discount_amount) * self.tax_percent / 100
        self.grand_total = self.subtotal - self.discount_amount + self.tax_amount
        self.save(update_fields=["subtotal", "tax_amount", "grand_total"])

    def item_count(self):
        return self.items.count()


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
