from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from .emails import send_order_confirmation_email, send_download_link_email
from django.views.decorators.http import require_POST
import stripe
from .models import Category, Product, Order, OrderItem
from .cart import Cart

stripe.api_key = settings.STRIPE_SECRET_KEY

def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True)
    return render(request, 'shop/list.html', {
        'products': products,
        'categories': categories,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'shop/detail.html', {
        'product': product,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    })

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    return redirect('shop:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('shop:cart_detail')

@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity, override_quantity=True)
    return redirect('shop:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'shop/cart.html', {'cart': cart})

@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('shop:cart_detail')

    # Create Stripe payment intent
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(cart.get_total_price() * 100),  # Amount in cents
            currency='gbp',
            metadata={'user_id': request.user.id}
        )
        return render(request, 'shop/checkout.html', {
            'client_secret': intent.client_secret,
            'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            'cart': cart,
        })
    except stripe.error.StripeError as e:
        messages.error(request, 'Payment processing error. Please try again.')
        return redirect('shop:cart_detail')

@login_required
def payment_success(request):
    cart = Cart(request)
    
    # Create order
    order = Order.objects.create(
        user=request.user,
        email=request.user.email,
        payment_intent_id=request.GET.get('payment_intent'),
        paid=True,
        status='completed'
    )
    
    # Create order items
    for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            price_paid_pence=int(float(item['price']) * 100),  # Convert pounds to pence
            quantity=item['quantity'],
            downloads_remaining=item['product'].download_limit
        )
    
    # Send confirmation email
    send_order_confirmation_email(order)
    
    # Clear the cart
    cart.clear()
    
    return render(request, 'shop/success.html', {'order': order})

@login_required
def download_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    order_item = OrderItem.objects.filter(
        order__user=request.user,
        product=product
    ).first()
    
    if not order_item:
        messages.error(request, 'You have not purchased this product.')
        return redirect('shop:product_detail', slug=product.slug)
    
    if order_item.download_count >= settings.MAX_DOWNLOAD_LIMIT:
        messages.error(request, 'You have reached the download limit for this product.')
        return redirect('shop:purchases')
    
    # Increment download count
    order_item.download_count += 1
    order_item.save()
    
    # Send download link email
    send_download_link_email(order_item)
    
    # Generate download URL
    download_url = product.get_download_url()
    
    return redirect(download_url)


@login_required
def purchases(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'shop/purchases.html', {'orders': orders})

def category_list(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(
        category=category,
        status='publish'
    )
    return render(request, 'shop/category.html', {
        'category': category,
        'products': products
    })

def payment_cancel(request):
    messages.error(request, 'Payment was cancelled.')
    return redirect('shop:cart_detail')