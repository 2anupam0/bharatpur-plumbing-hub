from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Category, Product, SiteSettings, Order, OrderItem
from .forms import ContactForm, CheckoutForm
from .cart import Cart


def home(request):
    categories = Category.objects.filter(is_active=True).annotate(
        product_count=Count("products", filter=Q(products__is_active=True))
    )
    featured_products = Product.objects.filter(
        is_active=True, is_featured=True
    )[:8]
    site_settings = SiteSettings.load()

    context = {
        "categories": categories,
        "featured_products": featured_products,
        "free_delivery_threshold": site_settings.free_delivery_threshold,
    }
    return render(request, "shop/home.html", context)


def product_list(request):
    products = Product.objects.select_related("category").filter(is_active=True)
    categories = Category.objects.filter(is_active=True).annotate(
        product_count=Count("products", filter=Q(products__is_active=True))
    )
    category_slug = request.GET.get("category")
    search_query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "")
    page = request.GET.get("page", 1)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=category)
    else:
        category = None

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(brand__icontains=search_query)
        )

    if sort == "price_low":
        products = products.order_by("price")
    elif sort == "price_high":
        products = products.order_by("-price")
    elif sort == "newest":
        products = products.order_by("-created_at")
    else:
        products = products.order_by("-is_featured", "-created_at")

    paginator = Paginator(products, 18)
    products_page = paginator.get_page(page)

    context = {
        "products": products_page,
        "categories": categories,
        "current_category": category,
        "search_query": search_query,
        "current_sort": sort,
        "total_count": paginator.count,
    }
    return render(request, "shop/product_list.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(pk=product.pk)[:4]

    gallery_items = []
    if product.image:
        gallery_items.append({
            'type': 'image',
            'url': product.image.url,
            'embed_url': '',
        })
    for img in product.additional_images.all():
        gallery_items.append({
            'type': 'image',
            'url': img.image.url,
            'embed_url': '',
        })
    for vid in product.videos.all():
        gallery_items.append({
            'type': 'video',
            'url': vid.video_url,
            'embed_url': vid.get_embed_url(),
        })

    context = {
        "product": product,
        "related_products": related_products,
        "gallery_items": gallery_items,
    }
    return render(request, "shop/product_detail.html", context)


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Thank you! Your inquiry has been submitted. We will contact you soon.",
            )
            return redirect("contact")
    else:
        form = ContactForm()

    return render(request, "shop/contact.html", {"form": form})


def delivery_info(request):
    site_settings = SiteSettings.load()
    context = {
        "free_delivery_threshold": site_settings.free_delivery_threshold,
        "delivery_fee": site_settings.delivery_fee,
    }
    return render(request, "shop/delivery_info.html", context)


def about(request):
    return render(request, "shop/about.html")


def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = Cart(request)
    quantity = int(request.POST.get("quantity", 1))
    if quantity < 1:
        quantity = 1
    if quantity > product.stock:
        quantity = product.stock
    cart.add(product, quantity)
    cart_count = len(cart)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        from django.http import JsonResponse
        return JsonResponse({
            "success": True,
            "message": f"{product.name} added to cart.",
            "cart_count": cart_count,
            "product_name": product.name,
        })
    messages.success(request, f"{product.name} added to cart.")
    return redirect("cart_page")


def cart_remove(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = Cart(request)
    cart.remove(product)
    messages.success(request, f"{product.name} removed from cart.")
    return redirect("cart_page")


def cart_update(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = Cart(request)
    quantity = int(request.POST.get("quantity", 1))
    if quantity > product.stock:
        messages.warning(request, f"Only {product.stock} {product.unit} available.")
        quantity = product.stock
    cart.update(product, quantity)
    return redirect("cart_page")


def cart_page(request):
    cart = Cart(request)
    cart_items = cart.get_items()
    context = {
        "cart_items": cart_items,
        "subtotal": cart.get_subtotal(),
        "delivery_fee": cart.get_delivery_fee(),
        "tax": cart.get_tax(),
        "total": cart.get_total(),
        "cart_count": len(cart),
    }
    return render(request, "shop/cart.html", context)


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect("product_list")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            is_delivery = form.cleaned_data["fulfillment_method"] == "delivery"
            delivery_fee = cart.get_delivery_fee() if is_delivery else Decimal("0")

            order = Order.objects.create(
                customer_name=form.cleaned_data["customer_name"],
                customer_phone=form.cleaned_data["customer_phone"],
                customer_email=form.cleaned_data.get("customer_email", ""),
                customer_address=form.cleaned_data.get("customer_address", ""),
                payment_method=form.cleaned_data["payment_method"],
                notes=form.cleaned_data.get("notes", ""),
                source="website",
                delivery_fee=delivery_fee,
                tax_percent=Decimal("13.00"),
            )
            for item in cart.get_items():
                product = item["product"]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    quantity=item["quantity"],
                    unit_price=item["price"],
                    total_price=item["total"],
                )
                product.stock = max(0, product.stock - item["quantity"])
                product.save(update_fields=["stock"])
            order.recalculate_totals()
            cart.clear()
            messages.success(request, f"Order {order.order_number} placed successfully!")
            return redirect("order_confirmation", order_number=order.order_number)
    else:
        initial = {}
        cart_items = cart.get_items()
        if cart_items:
            initial["customer_name"] = request.user.get_full_name() if request.user.is_authenticated else ""
            initial["customer_phone"] = ""
        form = CheckoutForm(initial=initial)

    context = {
        "form": form,
        "cart_items": cart.get_items(),
        "subtotal": cart.get_subtotal(),
        "delivery_fee": cart.get_delivery_fee(),
        "tax": cart.get_tax(),
        "total": cart.get_total(),
        "free_delivery_threshold": SiteSettings.load().free_delivery_threshold,
    }
    return render(request, "shop/checkout.html", context)


def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, "shop/order_confirmation.html", {"order": order})


def order_invoice(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, "shop/invoice.html", {"order": order})
