# shop/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import stripe

from shop.forms import GuestDetailsForm
from .emails import send_order_confirmation_email, send_download_link_email
from .models import Category, GuestDetails, Product, Order, OrderItem
from .cart import Cart

stripe.api_key = settings.STRIPE_SECRET_KEY

def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.filter(
        is_active=True,
        status='publish'
    )
    return render(request, 'shop/list.html', {
        'products': products,
        'categories': categories,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    })

def product_detail(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug,
        is_active=True,
        status='publish'
    )
    return render(request, 'shop/detail.html', {
        'product': product,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    })

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'shop/cart.html', {'cart': cart})

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

def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('shop:cart_detail')

    guest_form = None
    
    # Handle guest checkout
    if not request.user.is_authenticated:
        if request.method == 'POST':
            guest_form = GuestDetailsForm(request.POST)
            if guest_form.is_valid():
                request.session['guest_details'] = {
                    'first_name': guest_form.cleaned_data['first_name'],
                    'last_name': guest_form.cleaned_data['last_name'],
                    'email': guest_form.cleaned_data['email'],
                    'phone': guest_form.cleaned_data['phone'],
                }
            else:
                return HttpResponseBadRequest('Invalid form data')
        else:
            guest_form = GuestDetailsForm()

    try:
        # Create base payment intent data
        payment_intent_data = {
            'amount': int(cart.get_total_price() * 100),
            'currency': settings.STRIPE_CURRENCY,
            'payment_method_types': ['card'],
            'metadata': {
                'user_id': str(request.user.id) if request.user.is_authenticated else 'guest',
                'is_guest': str(not request.user.is_authenticated)
            }
        }

        # Add customer email if available
        if request.user.is_authenticated:
            payment_intent_data['receipt_email'] = request.user.email
        elif 'guest_details' in request.session:
            payment_intent_data['receipt_email'] = request.session['guest_details']['email']

        # Create the payment intent
        intent = stripe.PaymentIntent.create(**payment_intent_data)

        # Prepare context for template
        context = {
            'client_secret': intent.client_secret,
            'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            'cart': cart,
            'guest_form': guest_form,
            'is_guest': not request.user.is_authenticated,
            'payment_intent_id': intent.id,
        }
        
        return render(request, 'shop/checkout.html', context)
        
    except stripe.error.StripeError as e:
        messages.error(request, f'Payment processing error: {str(e)}')
        return redirect('shop:cart_detail')


def payment_success(request):
    payment_intent_id = request.GET.get('payment_intent')
    if not payment_intent_id:
        messages.error(request, 'No payment information found.')
        return redirect('shop:cart_detail')

    try:
        # Verify payment with Stripe
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if payment_intent.status != 'succeeded':
            messages.error(request, 'Payment was not successful.')
            return redirect('shop:cart_detail')

        cart = Cart(request)
        guest_details = request.session.get('guest_details', {})
        
        # Get email safely
        email = None
        if request.user.is_authenticated:
            email = request.user.email
        elif guest_details:
            email = guest_details.get('email')
        
        if not email:
            messages.error(request, 'User email not found.')
            return redirect('shop:cart_detail')

        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            email=email,
            payment_intent_id=payment_intent_id,
            paid=True,
            status='completed'
        )
        
        # Handle guest details
        if not request.user.is_authenticated and guest_details:
            GuestDetails.objects.create(
                order=order,
                first_name=guest_details.get('first_name', ''),
                last_name=guest_details.get('last_name', ''),
                email=guest_details.get('email', ''),
                phone=guest_details.get('phone', '')
            )
            request.session.pop('guest_details', None)  # Safer than del
        
        # Create order items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price_paid_pence=int(float(item['price']) * 100),
                quantity=item['quantity'],
                downloads_remaining=item['product'].download_limit
            )
        
        # Send confirmation email
        send_order_confirmation_email(order)
        
        # Clear cart
        cart.clear()
        
        return render(request, 'shop/success.html', {
            'order': order,
            'is_guest': not request.user.is_authenticated
        })

    except stripe.error.StripeError as e:
        messages.error(request, f'Error processing payment: {str(e)}')
        return redirect('shop:cart_detail')


def payment_cancel(request):
    messages.error(request, 'Payment was cancelled.')
    return redirect('shop:cart_detail')

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
    
    # Get download URL
    download_url = product.get_download_url()
    if not download_url:
        messages.error(request, 'Download URL not available.')
        return redirect('shop:purchases')
    
    return redirect(download_url)

@login_required
def purchases(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'shop/purchases.html', {'orders': orders})

def category_list(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(
        category=category,
        status='publish',
        is_active=True
    )
    return render(request, 'shop/category.html', {
        'category': category,
        'products': products
    })

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'shop/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        handle_successful_payment(payment_intent)
    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        handle_failed_payment(payment_intent)

    return HttpResponse(status=200)

def handle_successful_payment(payment_intent):
    # Update order status if needed
    order = Order.objects.filter(payment_intent_id=payment_intent.id).first()
    if order and not order.paid:
        order.paid = True
        order.status = 'completed'
        order.save()

def handle_failed_payment(payment_intent):
    # Handle failed payment
    order = Order.objects.filter(payment_intent_id=payment_intent.id).first()
    if order:
        order.status = 'failed'
        order.save()