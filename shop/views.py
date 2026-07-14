from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Category, Product, SiteSettings
from .forms import ContactForm


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

    context = {
        "product": product,
        "related_products": related_products,
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
