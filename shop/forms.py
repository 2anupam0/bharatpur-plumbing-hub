import re
from django import forms
from .models import ContactInquiry, Order


class ContactForm(forms.ModelForm):
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput,
        label="",
    )

    class Meta:
        model = ContactInquiry
        fields = ["name", "phone", "email", "inquiry_type", "message"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none",
                "placeholder": "Your full name",
            }),
            "phone": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none",
                "placeholder": "+977 98XXXXXXXX",
            }),
            "email": forms.EmailInput(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none",
                "placeholder": "your@email.com (optional)",
            }),
            "inquiry_type": forms.Select(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none",
            }),
            "message": forms.Textarea(attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none",
                "rows": 5,
                "placeholder": "Tell us what you need...",
            }),
        }

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spam detected.")
        return ""

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        cleaned = re.sub(r"[\s\-\(\)]", "", phone)
        if not re.match(r"^\+?\d{7,15}$", cleaned):
            raise forms.ValidationError("Enter a valid phone number.")
        return cleaned


class CheckoutForm(forms.Form):
    FULFILLMENT_CHOICES = [
        ("delivery", "Home Delivery"),
        ("pickup", "Pickup from Shop"),
    ]

    customer_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Full name",
        }),
    )
    customer_phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "+977 98XXXXXXXX",
        }),
    )
    customer_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            "class": "form-input",
            "placeholder": "Email (optional)",
        }),
    )
    fulfillment_method = forms.ChoiceField(
        choices=FULFILLMENT_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-input",
            "id": "fulfillment-method",
            "onchange": "toggleAddress(this.value)",
        }),
    )
    customer_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-input",
            "rows": 2,
            "placeholder": "Delivery address",
            "id": "delivery-address",
        }),
    )
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-input",
        }),
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-input",
            "rows": 2,
            "placeholder": "Order notes (optional)",
        }),
    )

    def clean_customer_phone(self):
        phone = self.cleaned_data.get("customer_phone", "")
        cleaned = re.sub(r"[\s\-\(\)]", "", phone)
        if not re.match(r"^\+?\d{7,15}$", cleaned):
            raise forms.ValidationError("Enter a valid phone number.")
        return cleaned

    def clean_customer_address(self):
        address = self.cleaned_data.get("customer_address", "")
        fulfillment = self.cleaned_data.get("fulfillment_method")
        if fulfillment == "delivery" and not address.strip():
            raise forms.ValidationError("Delivery address is required for home delivery.")
        return address
