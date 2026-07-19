import io
import json
import base64
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.utils import timezone
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask

from .models import (
    Category, Product, ProductImage, ProductVideo, SiteSettings, Order, OrderItem,
    Bill, BillItem,
)
from .owner_forms import ProductForm, BillCreateForm
from .cart import Cart


def owner_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("admin_panel_login")
        return view_func(request, *args, **kwargs)
    return wrapper


@owner_login_required
def owner_dashboard(request):
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(order_status="pending").count()
    total_bills = Bill.objects.count()
    unpaid_bills = Bill.objects.filter(status__in=["draft", "confirmed"]).count()
    total_revenue = Order.objects.filter(payment_status="paid").aggregate(
        total=Sum("grand_total")
    )["total"] or 0
    bill_revenue = Bill.objects.filter(status="paid").aggregate(
        total=Sum("grand_total")
    )["total"] or 0
    low_stock = Product.objects.filter(stock__lte=5, is_active=True).count()
    categories = Category.objects.annotate(
        product_count=Count("products")
    ).order_by("-product_count")

    recent_unpaid_bills = Bill.objects.filter(
        status__in=["draft", "confirmed"]
    ).order_by("-created_at")[:10]

    context = {
        "total_products": total_products,
        "active_products": active_products,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_bills": total_bills,
        "unpaid_bills": unpaid_bills,
        "total_revenue": total_revenue + bill_revenue,
        "low_stock": low_stock,
        "categories": categories,
        "recent_unpaid_bills": recent_unpaid_bills,
    }
    return render(request, "owner/dashboard.html", context)


@owner_login_required
def owner_products(request):
    products = Product.objects.select_related("category").all()
    search = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "")
    status = request.GET.get("status", "")

    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(brand__icontains=search)
        )
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

    context = {
        "products": products_page,
        "categories": categories,
        "search": search,
        "filter_category": category_id,
        "filter_status": status,
        "total_count": paginator.count,
    }
    return render(request, "owner/products.html", context)


@owner_login_required
def owner_product_add(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                product = form.save()
            except Exception as e:
                messages.error(request, f"Error saving product: {e}")
                return render(request, "owner/product_form.html", {"form": form, "editing": False})
            for img in request.FILES.getlist('gallery_images'):
                try:
                    ProductImage.objects.create(product=product, image=img)
                except Exception:
                    pass
            for url in request.POST.getlist('video_urls'):
                url = url.strip()
                if url:
                    ProductVideo.objects.create(product=product, video_url=url)
            for vf in request.FILES.getlist('video_files'):
                try:
                    ProductVideo.objects.create(product=product, video_file=vf)
                except Exception:
                    pass
            messages.success(request, f"Product '{product.name}' added successfully.")
            return redirect("owner_products")
    else:
        form = ProductForm()
    return render(request, "owner/product_form.html", {"form": form, "editing": False})


@owner_login_required
def owner_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            try:
                form.save()
            except Exception as e:
                messages.error(request, f"Error saving product: {e}")
                return render(request, "owner/product_form.html", {
                    "form": form, "editing": True, "product": product,
                })
            for img in request.FILES.getlist('gallery_images'):
                try:
                    ProductImage.objects.create(product=product, image=img)
                except Exception:
                    pass
            for url in request.POST.getlist('video_urls'):
                url = url.strip()
                if url:
                    ProductVideo.objects.create(product=product, video_url=url)
            for vf in request.FILES.getlist('video_files'):
                try:
                    ProductVideo.objects.create(product=product, video_file=vf)
                except Exception:
                    pass
            delete_images = request.POST.getlist('delete_image')
            for img_id in delete_images:
                ProductImage.objects.filter(pk=img_id, product=product).delete()
            delete_videos = request.POST.getlist('delete_video')
            for vid_id in delete_videos:
                ProductVideo.objects.filter(pk=vid_id, product=product).delete()
            messages.success(request, f"Product '{product.name}' updated successfully.")
            return redirect("owner_products")
    else:
        form = ProductForm(instance=product)
    return render(request, "owner/product_form.html", {
        "form": form, "editing": True, "product": product,
    })


@owner_login_required
def owner_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        name = product.name
        product.delete()
        messages.success(request, f"Product '{name}' deleted.")
        return redirect("owner_products")
    return render(request, "owner/product_confirm_delete.html", {"product": product})


@owner_login_required
def owner_orders(request):
    orders = Order.objects.all()
    status_filter = request.GET.get("status", "")
    if status_filter:
        orders = orders.filter(order_status=status_filter)

    paginator = Paginator(orders, 20)
    page = request.GET.get("page", 1)
    orders_page = paginator.get_page(page)

    context = {
        "orders": orders_page,
        "filter_status": status_filter,
    }
    return render(request, "owner/orders.html", context)


@owner_login_required
def owner_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        new_status = request.POST.get("order_status")
        new_payment = request.POST.get("payment_status")
        if new_status:
            order.order_status = new_status
        if new_payment:
            order.payment_status = new_payment
        order.save(update_fields=["order_status", "payment_status", "updated_at"])
        messages.success(request, "Order updated.")
        return redirect("owner_order_detail", pk=pk)
    return render(request, "owner/order_detail.html", {"order": order})


@owner_login_required
def owner_bills(request):
    bills = Bill.objects.all()
    status_filter = request.GET.get("status", "")
    if status_filter:
        bills = bills.filter(status=status_filter)

    status_counts = {
        "all": Bill.objects.count(),
        "draft": Bill.objects.filter(status="draft").count(),
        "confirmed": Bill.objects.filter(status="confirmed").count(),
        "paid": Bill.objects.filter(status="paid").count(),
        "cancelled": Bill.objects.filter(status="cancelled").count(),
    }

    paginator = Paginator(bills, 20)
    page = request.GET.get("page", 1)
    bills_page = paginator.get_page(page)

    context = {
        "bills": bills_page,
        "filter_status": status_filter,
        "status_counts": status_counts,
    }
    return render(request, "owner/bills.html", context)


@owner_login_required
def owner_bill_create(request):
    if request.method == "POST":
        form = BillCreateForm(request.POST)
        if form.is_valid():
            bill = Bill.objects.create(
                customer_name=form.cleaned_data["customer_name"],
                customer_phone=form.cleaned_data.get("customer_phone", ""),
                customer_address=form.cleaned_data.get("customer_address", ""),
                discount_amount=form.cleaned_data.get("discount_amount", 0),
                tax_percent=form.cleaned_data.get("tax_percent", 13),
                payment_method=form.cleaned_data["payment_method"],
                status="confirmed",
                notes=form.cleaned_data.get("notes", ""),
                created_by=request.user,
            )
            items_json = request.POST.get("bill_items", "[]")
            try:
                items = json.loads(items_json)
            except json.JSONDecodeError:
                items = []

            for item in items:
                product = None
                if item.get("product_id"):
                    try:
                        product = Product.objects.get(pk=item["product_id"])
                    except Product.DoesNotExist:
                        pass

                BillItem.objects.create(
                    bill=bill,
                    product=product,
                    product_name=item["name"],
                    quantity=item["quantity"],
                    unit_price=Decimal(str(item["price"])),
                    total_price=Decimal(str(item["price"])) * item["quantity"],
                )
                if product:
                    product.stock = max(0, product.stock - item["quantity"])
                    product.save(update_fields=["stock"])

            bill.recalculate_totals()
            messages.success(request, f"Bill {bill.bill_number} created successfully.")
            return redirect("owner_bill_detail", pk=bill.pk)
    else:
        form = BillCreateForm()

    products = Product.objects.filter(is_active=True).values_list(
        "pk", "name", "price", "stock", "unit", "category__name"
    )
    products_list = [
        {"pk": p[0], "name": p[1], "price": float(p[2]), "stock": p[3], "unit": p[4], "category__name": p[5] or ""}
        for p in products
    ]
    return render(request, "owner/bill_create.html", {
        "form": form,
        "products_json": json.dumps(products_list),
    })


@owner_login_required
def owner_bill_detail(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "confirm":
            bill.status = "confirmed"
            bill.save(update_fields=["status"])
            messages.success(request, f"Bill {bill.bill_number} confirmed.")
        elif action == "mark_paid":
            bill.status = "paid"
            bill.save(update_fields=["status"])
            messages.success(request, f"Bill {bill.bill_number} marked as paid.")
        elif action == "cancel":
            bill.status = "cancelled"
            bill.save(update_fields=["status"])
            for item in bill.items.all():
                if item.product:
                    item.product.stock += item.quantity
                    item.product.save(update_fields=["stock"])
            messages.success(request, f"Bill {bill.bill_number} cancelled. Stock restored.")
        return redirect("owner_bill_detail", pk=pk)

    qr_images = {}
    try:
        qr_images = _generate_payment_qr(bill)
    except Exception:
        pass
    return render(request, "owner/bill_detail.html", {
        "bill": bill,
        "qr_images": qr_images,
    })


@owner_login_required
def owner_bill_print(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    qr_images = {}
    try:
        qr_images = _generate_payment_qr(bill)
    except Exception:
        pass
    return render(request, "owner/bill_print.html", {
        "bill": bill,
        "qr_images": qr_images,
    })


@owner_login_required
def owner_bill_update_status(request, pk):
    if request.method == "POST":
        bill = get_object_or_404(Bill, pk=pk)
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
    return redirect("owner_bill_detail", pk=pk)


def generate_qr_code_image(text, size=200):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(
            back_color=(255, 255, 255),
            front_color=(37, 99, 235),
        ),
    )
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()


def _generate_payment_qr(bill):
    site_settings = SiteSettings.load()
    qr_images = {}

    esewa_id = "9800000000"
    khalti_id = "9800000000"
    ime_id = "9800000000"
    shop_name = "ARUN Suppliers"

    if bill.payment_method == "esewa":
        esewa_url = f"https://esewa.com.np/qrcode?amnt={bill.grand_total}&pid={bill.bill_number}&pn={shop_name}"
        qr_images["esewa"] = generate_qr_code_image(esewa_url)

    elif bill.payment_method == "khalti":
        khalti_url = f"https://khalti.com/pay?amnt={bill.grand_total}&pid={bill.bill_number}&pn={shop_name}"
        qr_images["khalti"] = generate_qr_code_image(khalti_url)

    elif bill.payment_method == "ime_pay":
        ime_url = f"imepay://qr?amount={bill.grand_total}&reference={bill.bill_number}&remarks={shop_name}"
        qr_images["ime_pay"] = generate_qr_code_image(ime_url)

    elif bill.payment_method == "bank_transfer":
        bank_text = f"BANK: Nabil Bank Ltd\nA/C: ARUN Suppliers\nA/C No: 12345678901\nAmount: NPR {bill.grand_total}\nRef: {bill.bill_number}"
        qr_images["bank_transfer"] = generate_qr_code_image(bank_text)

    elif bill.payment_method == "qr_code":
        generic_url = f"upi://pay?pa=plumbinghub@bank&pn={shop_name}&am={bill.grand_total}&tn=Bill {bill.bill_number}"
        qr_images["generic"] = generate_qr_code_image(generic_url)

    else:
        esewa_url = f"https://esewa.com.np/qrcode?amnt={bill.grand_total}&pid={bill.bill_number}&pn={shop_name}"
        qr_images["esewa"] = generate_qr_code_image(esewa_url)
        khalti_url = f"https://khalti.com/pay?amnt={bill.grand_total}&pid={bill.bill_number}&pn={shop_name}"
        qr_images["khalti"] = generate_qr_code_image(khalti_url)
        bank_text = f"BANK: Nabil Bank Ltd\nA/C: ARUN Suppliers\nA/C No: 12345678901\nAmount: NPR {bill.grand_total}\nRef: {bill.bill_number}"
        qr_images["bank_transfer"] = generate_qr_code_image(bank_text)

    return qr_images


@owner_login_required
def owner_product_search_api(request):
    q = request.GET.get("q", "").strip()
    if len(q) < 2:
        return JsonResponse({"results": []})
    products = Product.objects.filter(
        is_active=True,
        stock__gt=0,
    ).filter(
        Q(name__icontains=q) | Q(brand__icontains=q)
    ).values("pk", "name", "price", "stock", "unit", "category__name")[:15]
    return JsonResponse({"results": list(products)})


@owner_login_required
def owner_order_to_bill(request, pk):
    order = get_object_or_404(Order, pk=pk)

    existing_bill = Bill.objects.filter(
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        notes__contains=f"Order: {order.order_number}",
    ).first()
    if existing_bill:
        messages.warning(request, f"Bill {existing_bill.bill_number} already exists for this order.")
        return redirect("owner_bill_detail", pk=existing_bill.pk)

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
    return redirect("owner_bill_detail", pk=bill.pk)
