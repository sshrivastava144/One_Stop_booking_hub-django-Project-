from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.utils import timezone
import uuid

from .models import (
    Shop, Product, ShopCategory, ProductCategory, Cart, CartItem, 
    Order, OrderItem, ShopReview, ShopRegistrationPayment
)
from .forms import (
    ShopRegistrationForm, ProductForm, AddToCartForm, CheckoutForm,
    ShopReviewForm, ShopSearchForm, ProductSearchForm, OrderStatusUpdateForm
)

# Home view
def sabji_home(request):
    categories = ShopCategory.objects.all()
    featured_shops = Shop.objects.filter(status='active', is_open=True)[:6]
    product_categories = ProductCategory.objects.all()[:8]
    
    context = {
        'categories': categories,
        'featured_shops': featured_shops,
        'product_categories': product_categories,
    }
    return render(request, 'sabji_market/home.html', context)

# Shop registration view
@login_required
def register_shop(request):
    if request.method == 'POST':
        form = ShopRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.owner = request.user
            shop.save()
            
            # Create payment record
            payment = ShopRegistrationPayment.objects.create(
                shop=shop,
                amount=10.00,
                payment_method='pending'
            )
            
            messages.success(request, 'Shop registered successfully! Please pay ₹10 registration fee to activate your shop.')
            return redirect('sabji_market:payment', shop_id=shop.id)
    else:
        form = ShopRegistrationForm()
    
    return render(request, 'sabji_market/register_shop.html', {'form': form})

# Payment view
@login_required
def shop_payment(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id, owner=request.user)
    payment = get_object_or_404(ShopRegistrationPayment, shop=shop)
    
    if request.method == 'POST':
        # Simulate payment processing
        payment.status = 'completed'
        payment.transaction_id = f"TXN{uuid.uuid4().hex[:10].upper()}"
        payment.save()
        
        shop.registration_fee_paid = True
        shop.status = 'active'
        shop.save()
        
        messages.success(request, 'Payment successful! Your shop is now active.')
        return redirect('sabji_market:shop_dashboard')
    
    context = {
        'shop': shop,
        'payment': payment,
    }
    return render(request, 'sabji_market/payment.html', context)

# Shop dashboard
@login_required
def shop_dashboard(request):
    shops = Shop.objects.filter(owner=request.user)
    context = {'shops': shops}
    return render(request, 'sabji_market/shop_dashboard.html', context)

# Shop detail view
@login_required
def shop_detail(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id, owner=request.user)
    products = Product.objects.filter(shop=shop)
    orders = Order.objects.filter(shop=shop).order_by('-created_at')[:10]
    
    context = {
        'shop': shop,
        'products': products,
        'orders': orders,
    }
    return render(request, 'sabji_market/shop_detail.html', context)

# Add product
@login_required
def add_product(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id, owner=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.shop = shop
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('sabji_market:shop_detail', shop_id=shop.id)
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'shop': shop,
    }
    return render(request, 'sabji_market/add_product.html', context)

# Edit product
@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, shop__owner=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('sabji_market:shop_detail', shop_id=product.shop.id)
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'sabji_market/edit_product.html', context)

# Shop list for customers
def shop_list(request):
    form = ShopSearchForm(request.GET)
    shops = Shop.objects.filter(status='active')
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        delivery_available = form.cleaned_data.get('delivery_available')
        
        if search:
            shops = shops.filter(Q(name__icontains=search) | Q(description__icontains=search))
        if category:
            shops = shops.filter(category=category)
        if delivery_available:
            shops = shops.filter(is_delivery_available=True)
    
    paginator = Paginator(shops, 12)
    page_number = request.GET.get('page')
    shops = paginator.get_page(page_number)
    
    context = {
        'shops': shops,
        'form': form,
    }
    return render(request, 'sabji_market/shop_list.html', context)

# Shop products view for customers
def shop_products(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id, status='active')
    form = ProductSearchForm(request.GET)
    products = Product.objects.filter(shop=shop, is_available=True)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        
        if search:
            products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))
        if category:
            products = products.filter(category=category)
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
    
    # Get reviews
    reviews = ShopReview.objects.filter(shop=shop).order_by('-created_at')[:5]
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'shop': shop,
        'products': products,
        'form': form,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
    }
    return render(request, 'sabji_market/shop_products.html', context)

# Add to cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    
    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            messages.success(request, f'{product.name} added to cart!')
            return redirect('sabji_market:shop_products', shop_id=product.shop.id)
    
    return redirect('sabji_market:shop_products', shop_id=product.shop.id)

# Cart view
@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    context = {'cart': cart}
    return render(request, 'sabji_market/cart.html', context)

# Update cart item
@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

# Remove cart item
@login_required
def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart!')
    return redirect('sabji_market:cart')

# Checkout
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('sabji_market:cart')
    
    # Group cart items by shop
    shops_data = {}
    for item in cart.items.all():
        shop = item.product.shop
        if shop not in shops_data:
            shops_data[shop] = {
                'items': [],
                'subtotal': 0,
                'delivery_charge': shop.delivery_charge if shop.is_delivery_available else 0,
            }
        shops_data[shop]['items'].append(item)
        shops_data[shop]['subtotal'] += item.get_total_price()
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            # Create orders for each shop
            for shop, data in shops_data.items():
                delivery_type = form.cleaned_data['delivery_type']
                delivery_charge = data['delivery_charge'] if delivery_type == 'delivery' else 0
                
                order = Order.objects.create(
                    order_id=f"ORD{uuid.uuid4().hex[:8].upper()}",
                    customer=request.user,
                    shop=shop,
                    customer_name=form.cleaned_data['customer_name'],
                    customer_phone=form.cleaned_data['customer_phone'],
                    delivery_address=form.cleaned_data['delivery_address'],
                    delivery_type=delivery_type,
                    subtotal=data['subtotal'],
                    delivery_charge=delivery_charge,
                    total_amount=data['subtotal'] + delivery_charge,
                )
                
                # Create order items
                for item in data['items']:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.get_discounted_price()
                    )
            
            # Clear cart
            cart.items.all().delete()
            
            messages.success(request, 'Order placed successfully!')
            return redirect('sabji_market:order_success')
    else:
        form = CheckoutForm(user=request.user)
    
    total_amount = sum([data['subtotal'] + data['delivery_charge'] for data in shops_data.values()])
    
    context = {
        'form': form,
        'shops_data': shops_data,
        'total_amount': total_amount,
    }
    return render(request, 'sabji_market/checkout.html', context)

# Order success
@login_required
def order_success(request):
    return render(request, 'sabji_market/order_success.html')

# My orders
@login_required
def my_orders(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    context = {'orders': orders}
    return render(request, 'sabji_market/my_orders.html', context)

# Order detail
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, customer=request.user)
    context = {'order': order}
    return render(request, 'sabji_market/order_detail.html', context)

# Shop orders (for shop owners)
@login_required
def shop_orders(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id, owner=request.user)
    orders = Order.objects.filter(shop=shop).order_by('-created_at')
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    context = {
        'shop': shop,
        'orders': orders,
    }
    return render(request, 'sabji_market/shop_orders.html', context)

# Update order status
@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, shop__owner=request.user)
    
    if request.method == 'POST':
        form = OrderStatusUpdateForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Order status updated successfully!')
            return redirect('sabji_market:shop_orders', shop_id=order.shop.id)
    else:
        form = OrderStatusUpdateForm(instance=order)
    
    context = {
        'form': form,
        'order': order,
    }
    return render(request, 'sabji_market/update_order_status.html', context)

# Add shop review
@login_required
def add_review(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id, status='active')
    
    # Check if user has ordered from this shop
    has_ordered = Order.objects.filter(customer=request.user, shop=shop, status='delivered').exists()
    
    if not has_ordered:
        messages.error(request, 'You can only review shops you have ordered from.')
        return redirect('sabji_market:shop_products', shop_id=shop.id)
    
    if request.method == 'POST':
        form = ShopReviewForm(request.POST)
        if form.is_valid():
            review, created = ShopReview.objects.get_or_create(
                shop=shop,
                customer=request.user,
                defaults={
                    'rating': form.cleaned_data['rating'],
                    'comment': form.cleaned_data['comment']
                }
            )
            
            if not created:
                review.rating = form.cleaned_data['rating']
                review.comment = form.cleaned_data['comment']
                review.save()
                messages.success(request, 'Review updated successfully!')
            else:
                messages.success(request, 'Review added successfully!')
            
            return redirect('sabji_market:shop_products', shop_id=shop.id)
    else:
        # Check if user has already reviewed
        existing_review = ShopReview.objects.filter(shop=shop, customer=request.user).first()
        form = ShopReviewForm(instance=existing_review)
    
    context = {
        'form': form,
        'shop': shop,
    }
    return render(request, 'sabji_market/add_review.html', context)

# Product categories
def product_categories(request):
    categories = ProductCategory.objects.all()
    context = {'categories': categories}
    return render(request, 'sabji_market/product_categories.html', context)

# Products by category
def products_by_category(request, category_id):
    category = get_object_or_404(ProductCategory, id=category_id)
    products = Product.objects.filter(category=category, is_available=True)
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': products,
        'search': search,
    }
    return render(request, 'sabji_market/products_by_category.html', context)

# Delete product
@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, shop__owner=request.user)
    
    if request.method == 'POST':
        shop_id = product.shop.id
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('sabji_market:shop_detail', shop_id=shop_id)
    
    context = {'product': product}
    return render(request, 'sabji_market/delete_product.html', context)

# Toggle shop status
@login_required
def toggle_shop_status(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id, owner=request.user)
    shop.is_open = not shop.is_open
    shop.save()
    
    status = "opened" if shop.is_open else "closed"
    messages.success(request, f'Shop {status} successfully!')
    return redirect('sabji_market:shop_dashboard')