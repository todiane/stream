# shop/views.py
from .models import Category, Product, Order, OrderItem
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.views.decorators.http import require_POST, require_http_methods
from .emails import send_download_link_email
from django.core.paginator import Paginator
import stripe
import os
import logging
import mimetypes
from wsgiref.util import FileWrapper
from shop.forms import ProductReviewForm

from .cart import Cart

stripe.api_key = settings.STRIPE_SECRET_KEY

# Set up logger
logger = logging.getLogger("shop")


def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.filter(
        is_active=True, status__in=["publish", "soon", "full"]
    ).order_by("order", "-created")
    paginator = Paginator(products, 18)
    page = request.GET.get("page")
    products = paginator.get_page(page)

    return render(
        request,
        "shop/list.html",
        {
            "products": products,
            "categories": categories,
            "current_category": None,
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product, slug=slug, is_active=True, status__in=["publish", "soon", "full"]
    )

    related_products = Product.objects.filter(
        category=product.category,
        status__in=["publish", "full"],
        is_active=True,
    ).exclude(id=product.id)[:3]

    has_purchased = False
    order_item = None
    review_form = None

    if request.user.is_authenticated:
        order_item = OrderItem.objects.filter(
            order__user=request.user, order__paid=True, product=product
        ).first()

        has_purchased = bool(order_item)
        review_form = ProductReviewForm() if product.can_review(request.user) else None

    return render(
        request,
        "shop/detail.html",
        {
            "product": product,
            "related_products": related_products,
            "has_purchased": has_purchased,
            "order_item": order_item,
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
            "form": review_form,
        },
    )


@require_POST
def cart_add(request, product_id):
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get("quantity", 1))
        cart.add(product=product, quantity=quantity)
        messages.success(request, f"{product.title} has been added to your cart.")
        return redirect("shop:cart_detail")
    except Exception as e:
        print(f"Error adding to cart: {str(e)}")
        messages.error(request, "There was an error adding the item to your cart.")
        return redirect("shop:product_detail", slug=product.slug)


def cart_detail(request):
    try:
        cart = Cart(request)
        return render(request, "shop/cart.html", {"cart": cart})
    except Exception as e:
        print(f"Error in cart detail: {str(e)}")
        messages.error(request, "There was an error displaying your cart.")
        return redirect("shop:product_list")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("shop:cart_detail")


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get("quantity", 1))
    cart.add(product=product, quantity=quantity, override_quantity=True)
    return redirect("shop:cart_detail")


@login_required
def checkout(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.error(request, "Your cart is empty.")
        return redirect("shop:cart_detail")

    try:
        total_price = cart.get_total_price()
        if total_price <= 0:
            messages.error(request, "Invalid cart total.")
            return redirect("shop:cart_detail")

        # Always use logged-in user's email
        email = request.user.email

        # Create PaymentIntent
        payment_intent_data = {
            "amount": int(total_price * 100),
            "currency": "gbp",
            "payment_method_types": ["card"],
            "metadata": {
                "user_id": str(request.user.id),
            },
            "receipt_email": email,
        }

        intent = stripe.PaymentIntent.create(**payment_intent_data)

        # Create order immediately (pending)
        order = Order.objects.create(
            user=request.user,
            email=email,
            payment_intent_id=intent.id,
            paid=False,
            status="pending",
        )

        # Add items to order
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                price_paid_pence=int(item["price"] * 100),
                quantity=item["quantity"],
                downloads_remaining=item["product"].download_limit,
            )

        context = {
            "client_secret": intent.client_secret,
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
            "cart": cart,
        }

        return render(request, "shop/checkout.html", context)

    except Exception as e:
        logger.error(f"Checkout error: {str(e)}")
        messages.error(request, "An error occurred during checkout. Please try again.")
        return redirect("shop:cart_detail")


@login_required
def payment_success(request):
    payment_intent_id = request.GET.get("payment_intent")
    if not payment_intent_id:
        messages.error(request, "No payment information found.")
        return redirect("shop:cart_detail")

    try:
        # Get the order created during checkout
        order = Order.objects.filter(
            payment_intent_id=payment_intent_id, user=request.user
        ).first()

        if not order:
            messages.error(request, "Order not found.")
            return redirect("shop:cart_detail")

        # Clear cart
        cart = Cart(request)
        cart.clear()

        return render(
            request,
            "shop/success.html",
            {"order": order, "is_guest": False},
        )

    except Exception as e:
        logger.error(f"Payment success error: {str(e)}")
        messages.error(request, "Error displaying your order.")
        return redirect("shop:cart_detail")


def payment_cancel(request):
    messages.error(request, "Payment was cancelled.")
    return redirect("shop:cart_detail")


@login_required
def download_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Ensure the logged-in user purchased this product
    order_item = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__status="completed",
    ).first()

    if not order_item:
        messages.error(request, "You have not purchased this product.")
        return redirect("shop:product_detail", slug=product.slug)

    # Enforce download limit for digital products only
    if product.product_type == "download":
        if order_item.download_count >= order_item.downloads_remaining:
            messages.error(
                request, "You have reached the download limit for this product."
            )
            return redirect("shop:purchases")

        # Increment download count
        order_item.download_count += 1
        order_item.save()

    # Email user the download link (optional)
    try:
        send_download_link_email(order_item)
    except Exception as e:
        logger.error(
            f"Failed to send download email for order item {order_item.id}: {str(e)}"
        )

    # Get direct download URL
    download_url = product.get_download_url()
    if not download_url:
        messages.error(request, "Download URL not available.")
        return redirect("shop:purchases")

    return redirect(download_url)


@login_required
def purchases(request):
    orders = Order.objects.filter(user=request.user).order_by("-created")
    return render(request, "shop/purchases.html", {"orders": orders})


def category_list(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(
        category=category, status__in=["publish", "soon", "full"], is_active=True
    ).order_by("order", "-created")
    categories = Category.objects.all()

    paginator = Paginator(products, 18)
    page = request.GET.get("page")
    products = paginator.get_page(page)

    return render(
        request,
        "shop/list.html",
        {
            "products": products,
            "categories": categories,
            "current_category": category,
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        },
    )


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by("-created")
    return render(request, "shop/order_history.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, "shop/order_detail.html", {"order": order})


@login_required
@require_http_methods(["GET"])
def secure_download(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)

    # Check if the order item belongs to the user
    if order_item.order.user != request.user:
        raise PermissionDenied

    # Check download limits for digital products only
    if order_item.product.product_type == "download":
        if order_item.download_count >= order_item.downloads_remaining:
            raise PermissionDenied("Download limit exceeded")

        # Decrement downloads_remaining and increment download_count
        order_item.downloads_remaining -= 1
        order_item.download_count += 1
        order_item.save()

    # Get the file path
    file_path = None
    if order_item.product.files:
        file_path = order_item.product.files.path

    if not file_path or not os.path.exists(file_path):
        raise Http404("File not found")

    # Get the file's mime type
    content_type, encoding = mimetypes.guess_type(file_path)
    content_type = content_type or "application/octet-stream"

    # Open the file
    with open(file_path, "rb") as file_obj:
        response = FileResponse(FileWrapper(file_obj), content_type=content_type)
        response["Content-Disposition"] = (
            f'attachment; filename="{os.path.basename(file_path)}"'
        )
        return response

    # Set content disposition
    response["Content-Disposition"] = (
        f'attachment; filename="{os.path.basename(file_path)}"'
    )

    return response


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Allow superusers to review without purchase verification
    if not request.user.is_superuser:
        if not product.can_review(request.user):
            messages.error(request, "You can only review products you have purchased.")
            return redirect("shop:product_detail", slug=product.slug)

    if request.method == "POST":
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.verified_purchase = True
            review.save()
            messages.success(request, "Your review has been added.")
            return redirect("shop:product_detail", slug=product.slug)
    else:
        form = ProductReviewForm()

    return render(request, "shop/add_review.html", {"form": form, "product": product})
