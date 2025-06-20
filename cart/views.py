from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from cart.models import Cart, CartItem, Order, OrderItem
from store.models import Product
from users.forms import ShippingAddressForm
from users.models import ShippingAddress


@login_required
def cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()
    total_quantity = sum(item.quantity for item in items)
    order_total = sum((item.product.sale_price if item.product.is_sale else item.product.price) * item.quantity for item in items)

    context = {
        'cart_items': items,
        'total_quantity': total_quantity,
        'order_total': order_total,
    }
    return render(request, 'cart/cart.html', context)


@login_required
def cart_add(request):
    if request.POST.get('product_id'):
        product_id = int(request.POST.get('product_id'))
        quantity = int(request.POST.get('product_qty'))
        product = get_object_or_404(Product, id=product_id)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        available_stock = product.stock_quantity
        if not created:
            total_quantity = cart_item.quantity + quantity
            cart_item.quantity = min(total_quantity, available_stock)
        else:
            cart_item.quantity = min(quantity, available_stock)

        cart_item.save()

        messages.success(request, f"{product.name} added to cart.")
        cart_quantity = sum(item.quantity for item in cart.items.all())
        return JsonResponse({'qty': cart_quantity})

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from store.models import Product
from django.contrib.auth.decorators import login_required

@login_required
def cart_update(request):
    if request.method == 'POST' and request.POST.get('action') == 'post':
        try:
            cart_item_id = int(request.POST.get('product_id'))
            new_quantity = int(request.POST.get('product_qty'))

            print("✅ cart_update view triggered")
            print("🛒 CartItem ID received:", cart_item_id)

            # Get cart item by ID
            cart = get_object_or_404(Cart, user=request.user)
            cart_item = get_object_or_404(CartItem, cart=cart, id=cart_item_id)
            product = cart_item.product

            # Update quantity within product stock
            cart_item.quantity = min(new_quantity, product.stock_quantity)
            cart_item.save()

            return JsonResponse({'qty': cart_item.quantity})
        except Exception as e:
            print("❌ Error in cart_update:", e)
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def cart_delete(request):
    if request.POST.get('action') == 'post':
        cart_item_id = int(request.POST.get('product_id'))  # This is actually CartItem.id
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
        cart_item.delete()

        messages.info(request, f"{cart_item.product.name} removed from cart.")
        return JsonResponse({'product': cart_item_id})



@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.select_related('product').all()
    total_quantity = sum(item.quantity for item in cart_items)
    order_total = sum((item.product.sale_price if item.product.is_sale else item.product.price) * item.quantity for item in cart_items)

    try:
        shipping_address = ShippingAddress.objects.get(user=request.user)
    except ShippingAddress.DoesNotExist:
        shipping_address = None

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=shipping_address)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            request.session['shipping'] = request.POST
            messages.success(request, "Your shipping information has been updated.")
            return redirect('payment')  # or to a review page
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ShippingAddressForm(instance=shipping_address)

    context = {
        'cart_items': cart_items,
        'total_quantity': total_quantity,
        'order_total': order_total,
        'form': form,
        'user_profile': request.user.profile,
    }
    return render(request, 'cart/checkout.html', context)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-date_ordered')
    return render(request, 'users/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'users/order_detail.html', {'order': order})