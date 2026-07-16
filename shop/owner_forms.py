import re
from django import forms
from .models import Product, Category, Bill, BillItem


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name", "category", "price", "original_price", "description",
            "short_description", "image", "stock", "is_active", "is_featured",
            "unit", "brand",
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "ow-input",
                "placeholder": "Product name",
            }),
            "category": forms.Select(attrs={"class": "ow-input"}),
            "price": forms.NumberInput(attrs={
                "class": "ow-input",
                "placeholder": "0.00",
                "step": "0.01",
            }),
            "original_price": forms.NumberInput(attrs={
                "class": "ow-input",
                "placeholder": "0.00 (optional)",
                "step": "0.01",
            }),
            "description": forms.Textarea(attrs={
                "class": "ow-input",
                "rows": 4,
                "placeholder": "Full product description...",
            }),
            "short_description": forms.TextInput(attrs={
                "class": "ow-input",
                "placeholder": "Brief one-liner (optional)",
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "ow-input",
            }),
            "stock": forms.NumberInput(attrs={
                "class": "ow-input",
                "placeholder": "0",
            }),
            "unit": forms.TextInput(attrs={
                "class": "ow-input",
                "placeholder": "piece, meter, kg, etc.",
            }),
            "brand": forms.TextInput(attrs={
                "class": "ow-input",
                "placeholder": "Brand name (optional)",
            }),
        }


class BillCreateForm(forms.Form):
    customer_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "ow-input",
            "placeholder": "Customer name",
        }),
    )
    customer_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "ow-input",
            "placeholder": "Phone number",
        }),
    )
    customer_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "ow-input",
            "rows": 2,
            "placeholder": "Address (optional)",
        }),
    )
    discount_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=0,
        widget=forms.NumberInput(attrs={
            "class": "ow-input",
            "placeholder": "0",
            "step": "0.01",
        }),
    )
    tax_percent = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        initial=13.00,
        widget=forms.NumberInput(attrs={
            "class": "ow-input",
            "placeholder": "13",
            "step": "0.01",
        }),
    )
    payment_method = forms.ChoiceField(
        choices=Bill.PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={"class": "ow-input"}),
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "ow-input",
            "rows": 2,
            "placeholder": "Notes (optional)",
        }),
    )


class BillItemForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    product_name = forms.CharField(max_length=200, widget=forms.HiddenInput())
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            "class": "ow-input ow-qty-input",
            "min": "1",
        }),
    )
    unit_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            "class": "ow-input ow-price-input",
            "step": "0.01",
        }),
    )
