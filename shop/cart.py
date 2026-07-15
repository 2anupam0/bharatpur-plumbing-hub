from decimal import Decimal
from .models import Product, SiteSettings


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        product_id = str(product.pk)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0, "price": str(product.price)}
        self.cart[product_id]["quantity"] += quantity
        self.cart[product_id]["price"] = str(product.price)
        self.save()

    def remove(self, product):
        product_id = str(product.pk)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def update(self, product, quantity):
        product_id = str(product.pk)
        if product_id in self.cart:
            if quantity <= 0:
                self.remove(product)
            else:
                self.cart[product_id]["quantity"] = quantity
                self.cart[product_id]["price"] = str(product.price)
                self.save()

    def clear(self):
        self.session["cart"] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def get_items(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(pk__in=product_ids)
        product_map = {str(p.pk): p for p in products}
        items = []
        for product_id, item in self.cart.items():
            product = product_map.get(product_id)
            if product:
                items.append({
                    "product": product,
                    "quantity": item["quantity"],
                    "price": Decimal(item["price"]),
                    "total": Decimal(item["price"]) * item["quantity"],
                })
        return items

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def get_subtotal(self):
        return sum(
            Decimal(item["price"]) * item["quantity"]
            for item in self.cart.values()
        )

    def get_delivery_fee(self):
        site_settings = SiteSettings.load()
        subtotal = self.get_subtotal()
        if subtotal >= site_settings.free_delivery_threshold:
            return Decimal("0")
        return site_settings.delivery_fee

    def get_tax(self):
        site_settings = SiteSettings.load()
        subtotal = self.get_subtotal()
        return subtotal * site_settings.tax_percent / 100

    def get_total(self):
        subtotal = self.get_subtotal()
        delivery = self.get_delivery_fee()
        tax = self.get_tax()
        return subtotal + delivery + tax
