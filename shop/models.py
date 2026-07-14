from django.db import models
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
    image = models.ImageField(upload_to="products/")
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    unit = models.CharField(
        max_length=20, default="piece",
        help_text="Unit of measurement (piece, meter, kg, etc.)"
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
