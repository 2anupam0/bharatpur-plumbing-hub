from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden

from .models import Category, Product, ProductImage, ProductVideo, ContactInquiry, SiteSettings, Order, OrderItem, Bill, BillItem
from .owner_forms import ProductForm


def admin_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect("admin_panel_login")
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admin_panel_dashboard")
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect("admin_panel_dashboard")
        else:
            messages.error(request, "Invalid credentials or you don't have admin access.")
    return render(request, "admin_panel/login.html")


def admin_logout(request):
    logout(request)
    return redirect("admin_panel_login")


@admin_login_required
def admin_dashboard(request):
    total_users = User.objects.count()
    staff_users = User.objects.filter(is_staff=True).count()
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    total_categories = Category.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(order_status="pending").count()
    delivered_orders = Order.objects.filter(order_status="delivered").count()
    total_bills = Bill.objects.count()
    paid_bills = Bill.objects.filter(status="paid").count()
    unpaid_bills = Bill.objects.filter(status__in=["draft", "confirmed"]).count()
    total_revenue = Order.objects.filter(payment_status="paid").aggregate(
        total=Sum("grand_total")
    )["total"] or 0
    bill_revenue = Bill.objects.filter(status="paid").aggregate(
        total=Sum("grand_total")
    )["total"] or 0
    unresolved_inquiries = ContactInquiry.objects.filter(is_resolved=False).count()
    low_stock = Product.objects.filter(stock__lte=5, is_active=True).count()

    recent_orders = Order.objects.all()[:5]
    recent_bills = Bill.objects.all()[:5]
    recent_inquiries = ContactInquiry.objects.all()[:5]

    orders_by_status = Order.objects.values("order_status").annotate(count=Count("id"))
    orders_status_map = {item["order_status"]: item["count"] for item in orders_by_status}

    context = {
        "total_users": total_users,
        "staff_users": staff_users,
        "total_products": total_products,
        "active_products": active_products,
        "total_categories": total_categories,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "delivered_orders": delivered_orders,
        "total_bills": total_bills,
        "paid_bills": paid_bills,
        "unpaid_bills": unpaid_bills,
        "total_revenue": total_revenue + bill_revenue,
        "unresolved_inquiries": unresolved_inquiries,
        "low_stock": low_stock,
        "recent_orders": recent_orders,
        "recent_bills": recent_bills,
        "recent_inquiries": recent_inquiries,
        "orders_status_map": orders_status_map,
    }
    return render(request, "admin_panel/dashboard.html", context)


@admin_login_required
def admin_users(request):
    search = request.GET.get("q", "").strip()
    users = User.objects.all().order_by("-date_joined")
    if search:
        users = users.filter(
            Q(username__icontains=search) | Q(email__icontains=search) | Q(first_name__icontains=search)
        )
    paginator = Paginator(users, 20)
    page = request.GET.get("page", 1)
    users_page = paginator.get_page(page)
    return render(request, "admin_panel/users.html", {"users": users_page, "search": search, "total_count": paginator.count})


@admin_login_required
def admin_user_add(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        password = request.POST.get("password", "")
        is_staff = request.POST.get("is_staff") == "on"
        is_superuser = request.POST.get("is_superuser") == "on"
        is_active = request.POST.get("is_active", "on") == "on"

        if not username or not password:
            messages.error(request, "Username and password are required.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(
                username=username, email=email, password=password,
                first_name=first_name, last_name=last_name,
                is_staff=is_staff, is_superuser=is_superuser, is_active=is_active,
            )
            messages.success(request, f"User '{user.username}' created successfully.")
            return redirect("admin_panel_users")
    return render(request, "admin_panel/user_form.html", {"editing": False})


@admin_login_required
def admin_user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        user.username = request.POST.get("username", user.username).strip()
        user.email = request.POST.get("email", "").strip()
        user.first_name = request.POST.get("first_name", "").strip()
        user.last_name = request.POST.get("last_name", "").strip()
        user.is_staff = request.POST.get("is_staff") == "on"
        user.is_superuser = request.POST.get("is_superuser") == "on"
        user.is_active = request.POST.get("is_active", "on") == "on"
        new_password = request.POST.get("password", "").strip()
        if new_password:
            user.set_password(new_password)
        user.save()
        messages.success(request, f"User '{user.username}' updated successfully.")
        return redirect("admin_panel_users")
    return render(request, "admin_panel/user_form.html", {"editing": True, "edit_user": user})


@admin_login_required
def admin_user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        if user.pk == request.user.pk:
            messages.error(request, "You cannot delete your own account.")
        else:
            username = user.username
            user.delete()
            messages.success(request, f"User '{username}' deleted.")
        return redirect("admin_panel_users")
    return render(request, "admin_panel/confirm_delete.html", {
        "object": user, "object_name": user.username, "cancel_url": "admin_panel_users",
        "type": "User",
    })


@admin_login_required
def admin_products(request):
    products = Product.objects.select_related("category").all()
    search = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "")
    status = request.GET.get("status", "")
    if search:
        products = products.filter(Q(name__icontains=search) | Q(brand__icontains=search))
    if category_id:
        products = products.filter(category_id=category_id)
    if status == "active":
        products = products.filter(is_active=True)
    elif status == "inactive":
        products = products.filter(is_active=False)
    elif status == "low_stock":
        products = products.filter(stock__lte=5, is_active=True)
    paginator = Paginator(products, 20)
    page = request.GET.get("page", 1)
    products_page = paginator.get_page(page)
    categories = Category.objects.all()
    return render(request, "admin_panel/products.html", {
        "products": products_page, "categories": categories, "search": search,
        "filter_category": category_id, "filter_status": status, "total_count": paginator.count,
    })


@admin_login_required
def admin_product_add(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            for img in request.FILES.getlist('gallery_images'):
                ProductImage.objects.create(product=product, image=img)
            for url in request.POST.getlist('video_urls'):
                url = url.strip()
                if url:
                    ProductVideo.objects.create(product=product, video_url=url)
            for vf in request.FILES.getlist('video_files'):
                ProductVideo.objects.create(product=product, video_file=vf)
            messages.success(request, f"Product '{product.name}' added successfully.")
            return redirect("admin_panel_products")
    else:
        form = ProductForm()
    return render(request, "admin_panel/product_form.html", {"form": form, "editing": False})


@admin_login_required
def admin_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            for img in request.FILES.getlist('gallery_images'):
                ProductImage.objects.create(product=product, image=img)
            for url in request.POST.getlist('video_urls'):
                url = url.strip()
                if url:
                    ProductVideo.objects.create(product=product, video_url=url)
            for vf in request.FILES.getlist('video_files'):
                ProductVideo.objects.create(product=product, video_file=vf)
            delete_images = request.POST.getlist('delete_image')
            for img_id in delete_images:
                ProductImage.objects.filter(pk=img_id, product=product).delete()
            delete_videos = request.POST.getlist('delete_video')
            for vid_id in delete_videos:
                ProductVideo.objects.filter(pk=vid_id, product=product).delete()
            messages.success(request, f"Product '{product.name}' updated successfully.")
            return redirect("admin_panel_products")
    else:
        form = ProductForm(instance=product)
    return render(request, "admin_panel/product_form.html", {
        "form": form, "editing": True, "product": product,
    })


@admin_login_required
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        name = product.name
        product.delete()
        messages.success(request, f"Product '{name}' deleted.")
        return redirect("admin_panel_products")
    return render(request, "admin_panel/confirm_delete.html", {
        "object": product, "object_name": product.name, "cancel_url": "admin_panel_products",
        "type": "Product",
    })


@admin_login_required
def admin_categories(request):
    categories = Category.objects.annotate(product_count=Count("products")).all()
    search = request.GET.get("q", "").strip()
    if search:
        categories = categories.filter(name__icontains=search)
    return render(request, "admin_panel/categories.html", {"categories": categories, "search": search, "total_count": categories.count()})


@admin_login_required
def admin_category_add(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        icon = request.POST.get("icon", "").strip() or "🔧"
        is_active = request.POST.get("is_active", "on") == "on"
        sort_order = int(request.POST.get("sort_order", 0) or 0)
        if not name:
            messages.error(request, "Category name is required.")
        else:
            cat = Category.objects.create(
                name=name, description=description, icon=icon,
                is_active=is_active, sort_order=sort_order,
            )
            if request.FILES.get("image"):
                cat.image = request.FILES["image"]
                cat.save()
            messages.success(request, f"Category '{cat.name}' created successfully.")
            return redirect("admin_panel_categories")
    return render(request, "admin_panel/category_form.html", {"editing": False})


@admin_login_required
def admin_category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.name = request.POST.get("name", category.name).strip()
        category.description = request.POST.get("description", "").strip()
        category.icon = request.POST.get("icon", "").strip() or "🔧"
        category.is_active = request.POST.get("is_active", "on") == "on"
        category.sort_order = int(request.POST.get("sort_order", 0) or 0)
        if request.FILES.get("image"):
            category.image = request.FILES["image"]
        category.save()
        messages.success(request, f"Category '{category.name}' updated successfully.")
        return redirect("admin_panel_categories")
    return render(request, "admin_panel/category_form.html", {"editing": True, "category": category})


@admin_login_required
def admin_category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        name = category.name
        category.delete()
        messages.success(request, f"Category '{name}' deleted.")
        return redirect("admin_panel_categories")
    return render(request, "admin_panel/confirm_delete.html", {
        "object": category, "object_name": category.name, "cancel_url": "admin_panel_categories",
        "type": "Category",
    })


@admin_login_required
def admin_orders(request):
    orders = Order.objects.all()
    status_filter = request.GET.get("status", "")
    if status_filter:
        orders = orders.filter(order_status=status_filter)
    paginator = Paginator(orders, 20)
    page = request.GET.get("page", 1)
    orders_page = paginator.get_page(page)
    return render(request, "admin_panel/orders.html", {"orders": orders_page, "filter_status": status_filter, "total_count": paginator.count})


@admin_login_required
def admin_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        new_status = request.POST.get("order_status")
        new_payment = request.POST.get("payment_status")
        if new_status:
            order.order_status = new_status
        if new_payment:
            order.payment_status = new_payment
        order.save(update_fields=["order_status", "payment_status", "updated_at"])
        messages.success(request, "Order updated successfully.")
        return redirect("admin_panel_order_detail", pk=pk)
    return render(request, "admin_panel/order_detail.html", {"order": order})


@admin_login_required
def admin_bills(request):
    bills = Bill.objects.all()
    status_filter = request.GET.get("status", "")
    if status_filter:
        bills = bills.filter(status=status_filter)
    paginator = Paginator(bills, 20)
    page = request.GET.get("page", 1)
    bills_page = paginator.get_page(page)
    return render(request, "admin_panel/bills.html", {"bills": bills_page, "filter_status": status_filter, "total_count": paginator.count})


@admin_login_required
def admin_bill_detail(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Bill.BILL_STATUS_CHOICES):
            if new_status == "cancelled" and bill.status != "cancelled":
                for item in bill.items.all():
                    if item.product:
                        item.product.stock += item.quantity
                        item.product.save(update_fields=["stock"])
            bill.status = new_status
            bill.save(update_fields=["status"])
            messages.success(request, f"Bill status changed to {bill.get_status_display()}.")
        return redirect("admin_panel_bill_detail", pk=pk)
    return render(request, "admin_panel/bill_detail.html", {"bill": bill})


@admin_login_required
def admin_inquiries(request):
    inquiries = ContactInquiry.objects.all()
    status_filter = request.GET.get("status", "")
    if status_filter == "resolved":
        inquiries = inquiries.filter(is_resolved=True)
    elif status_filter == "pending":
        inquiries = inquiries.filter(is_resolved=False)
    paginator = Paginator(inquiries, 20)
    page = request.GET.get("page", 1)
    inquiries_page = paginator.get_page(page)
    return render(request, "admin_panel/inquiries.html", {"inquiries": inquiries_page, "filter_status": status_filter, "total_count": paginator.count})


@admin_login_required
def admin_inquiry_detail(request, pk):
    inquiry = get_object_or_404(ContactInquiry, pk=pk)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "resolve":
            inquiry.is_resolved = True
            inquiry.save(update_fields=["is_resolved"])
            messages.success(request, "Inquiry marked as resolved.")
        elif action == "unresolve":
            inquiry.is_resolved = False
            inquiry.save(update_fields=["is_resolved"])
            messages.success(request, "Inquiry marked as unresolved.")
        elif action == "delete":
            inquiry.delete()
            messages.success(request, "Inquiry deleted.")
            return redirect("admin_panel_inquiries")
        return redirect("admin_panel_inquiry_detail", pk=pk)
    return render(request, "admin_panel/inquiry_detail.html", {"inquiry": inquiry})


@admin_login_required
def admin_settings(request):
    site_settings = SiteSettings.load()
    if request.method == "POST":
        site_settings.whatsapp_number = request.POST.get("whatsapp_number", site_settings.whatsapp_number)
        site_settings.free_delivery_threshold = request.POST.get("free_delivery_threshold", site_settings.free_delivery_threshold)
        site_settings.delivery_fee = request.POST.get("delivery_fee", site_settings.delivery_fee)
        site_settings.tax_percent = request.POST.get("tax_percent", site_settings.tax_percent)
        site_settings.announcement_text = request.POST.get("announcement_text", "")
        site_settings.save()
        messages.success(request, "Site settings updated successfully.")
        return redirect("admin_panel_settings")
    return render(request, "admin_panel/settings.html", {"site_settings": site_settings})


@admin_login_required
def admin_order_to_bill(request, pk):
    order = get_object_or_404(Order, pk=pk)

    existing_bill = Bill.objects.filter(
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        notes__contains=f"Order: {order.order_number}",
    ).first()
    if existing_bill:
        messages.warning(request, f"Bill {existing_bill.bill_number} already exists for this order.")
        return redirect("admin_panel_bill_detail", pk=existing_bill.pk)

    bill = Bill.objects.create(
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        customer_address=order.customer_address,
        discount_amount=order.discount_amount,
        tax_percent=order.tax_percent,
        payment_method=order.payment_method,
        status="confirmed",
        notes=f"Order: {order.order_number}",
        created_by=request.user,
    )

    for order_item in order.items.all():
        BillItem.objects.create(
            bill=bill,
            product=order_item.product,
            product_name=order_item.product_name,
            quantity=order_item.quantity,
            unit_price=order_item.unit_price,
            total_price=order_item.total_price,
        )
        if order_item.product:
            order_item.product.stock = max(0, order_item.product.stock - order_item.quantity)
            order_item.product.save(update_fields=["stock"])

    bill.recalculate_totals()
    if order.delivery_fee > 0:
        bill.notes += f" (Delivery fee: Rs {order.delivery_fee})"
        bill.save(update_fields=["notes"])

    messages.success(request, f"Bill {bill.bill_number} created from order {order.order_number}.")
    return redirect("admin_panel_bill_detail", pk=bill.pk)
