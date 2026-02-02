from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from .models import Product, Category, Cart, CartItem, Order, OrderItem
from django.utils import timezone
import json
import google.generativeai as genai

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyAkbdarju5y4TRgDK29gVcXYSfUDeD1efc"
genai.configure(api_key=GEMINI_API_KEY)


def home(request):
    featured_products = Product.objects.filter(is_featured=True)[:8]
    latest_products = Product.objects.all()[:12]
    categories = Category.objects.all()

    context = {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'categories': categories,
    }
    return render(request, 'home/index.html', context)


def products(request):
    products_list = Product.objects.all()
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')
    sort_by = request.GET.get('sort', '-created_at')

    if category_id:
        products_list = products_list.filter(category_id=category_id)

    if search_query:
        products_list = products_list.filter(name__icontains=search_query) | \
                        products_list.filter(description__icontains=search_query)

    products_list = products_list.order_by(sort_by)

    paginator = Paginator(products_list, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'home/products.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(pk=pk)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'home/product_detail.html', context)


@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not item_created:
        cart_item.quantity += quantity
        cart_item.save()
    
    return redirect('view_cart')


@login_required(login_url='login')
def view_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        cart = None
        cart_items = []
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    total_items = sum(item.quantity for item in cart_items)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
        'total_items': total_items,
    }
    return render(request, 'home/cart.html', context)


@login_required(login_url='login')
@require_POST
def update_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart_item.delete()
    else:
        cart_item.quantity = quantity
        cart_item.save()
    
    return redirect('view_cart')


@login_required(login_url='login')
@require_POST
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    cart_item.delete()
    return redirect('view_cart')


@login_required(login_url='login')
def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        return redirect('view_cart')
    
    if not cart_items.exists():
        return redirect('view_cart')
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'home/checkout.html', context)


@login_required(login_url='login')
def select_address(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        return redirect('view_cart')
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    # Sample addresses - in production, get from user profile
    addresses = [
        {'id': 1, 'address': '123 Main Street, New York, NY 10001'},
        {'id': 2, 'address': '456 Oak Avenue, Los Angeles, CA 90001'},
    ]
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
        'addresses': addresses,
    }
    return render(request, 'home/select_address.html', context)


@login_required(login_url='login')
def payment(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        return redirect('view_cart')
    
    if not cart_items.exists():
        return redirect('view_cart')
    
    address_id = request.GET.get('address', 1)
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
        'address_id': address_id,
    }
    return render(request, 'home/payment.html', context)


@login_required(login_url='login')
@require_POST
def process_payment(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        return redirect('view_cart')
    
    if not cart_items.exists():
        return redirect('view_cart')
    
    address_id = request.POST.get('address_id')
    payment_method = request.POST.get('payment_method')
    
    # Create order
    total = sum(item.product.price * item.quantity for item in cart_items)
    order = Order.objects.create(
        user=request.user,
        total_price=total,
        status='pending',
        delivery_address=f"Address ID: {address_id}"
    )
    
    # Move cart items to order items
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )
    
    # Clear cart
    cart.items.all().delete()
    
    return redirect('order_confirmation', order_id=order.id)


@login_required(login_url='login')
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    order_items = order.orderitem_set.all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'home/order_confirmation.html', context)


@require_http_methods(["POST"])
def chatbot_query(request):
    """
    Handle chatbot queries using Gemini AI API
    Expected POST data: {"query": "user message"}
    """
    try:
        data = json.loads(request.body)
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return JsonResponse({'error': 'Query cannot be empty', 'success': False}, status=400)
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create system prompt for the chatbot
        system_context = """You are a helpful AI assistant for an ecommerce store named EStore. 
You help customers with:
- Product information and recommendations
- Order tracking and status
- Shipping and delivery information
- General customer service questions
- Troubleshooting common issues
- Pricing and discounts

Keep responses concise (2-3 sentences), friendly, and professional. If you don't know something about the store, suggest they contact support."""
        
        # Build the full prompt
        full_prompt = system_context + "\n\nCustomer Question: " + user_query
        
        # Generate response using Gemini with error handling
        try:
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=256,
                    temperature=0.7,
                )
            )
            
            # Check if we got a valid response
            if hasattr(response, 'text') and response.text and response.text.strip():
                return JsonResponse({
                    'success': True,
                    'response': response.text.strip(),
                    'query': user_query
                })
            else:
                return JsonResponse({
                    'success': True,
                    'response': "I'm here to help! Could you please rephrase your question or ask something about our products and services?",
                    'query': user_query
                })
        except Exception as api_error:
            print(f"Gemini API Error: {str(api_error)}")
            return JsonResponse({
                'success': True,
                'response': "I'm experiencing a temporary issue. Please try again in a moment or contact our support team for immediate assistance.",
                'query': user_query
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format', 'success': False}, status=400)
    except Exception as e:
        print(f"Chatbot Error: {str(e)}")
        return JsonResponse({
            'success': True,
            'response': "I encountered an error processing your request. Please try again or contact support.",
            'query': user_query if 'user_query' in locals() else 'unknown'
        })
