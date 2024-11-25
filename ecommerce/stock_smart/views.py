from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import RegisterForm
from .models import CustomUser, Product, Category, Cart, CartItem
import json

def get_cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        return cart.get_total_items() if cart else 0
    else:
        return len(request.session.get('cart', {}))

def index(request):
    # Obtener categorías principales (sin padre)
    main_categories = Category.objects.filter(
        parent__isnull=True,
        is_active=True
    ).prefetch_related('children')
    
    # Obtener productos con descuento
    offer_products = Product.objects.filter(
        discount_percentage__gt=0,
        stock__gt=0
    ).order_by('-discount_percentage')[:8]
    
    # Productos destacados
    featured_products = Product.objects.filter(
        stock__gt=0
    ).order_by('-created_at')[:8]
    
    context = {
        'main_categories': main_categories,
        'offer_products': offer_products,
        'featured_products': featured_products,
        'cart_count': get_cart_count(request)
    }
    return render(request, 'stock_smart/home.html', context)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('stock_smart:account')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email  # Usamos el email como username
            user.verification_token = get_random_string(64)
            user.save()
            
            # Aquí puedes añadir el envío de email de verificación
            
            messages.success(request, 'Registro exitoso. Por favor verifica tu correo electrónico.')
            return redirect('stock_smart:login')
    else:
        form = RegisterForm()
    
    return render(request, 'stock_smart/auth/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('stock_smart:account')
        
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.email_verified:
                login(request, user)
                messages.success(request, '¡Bienvenido de vuelta!')
                return redirect('stock_smart:account')
            else:
                messages.warning(request, 'Por favor verifica tu correo electrónico.')
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')
    
    return render(request, 'stock_smart/auth/login.html')

@login_required
def account_view(request):
    return render(request, 'stock_smart/auth/account.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('stock_smart:home')

def verify_email(request, token):
    try:
        user = CustomUser.objects.get(verification_token=token)
        user.email_verified = True
        user.verification_token = None
        user.save()
        messages.success(request, '¡Email verificado exitosamente!')
    except CustomUser.DoesNotExist:
        messages.error(request, 'El enlace de verificación es inválido.')
    
    return redirect('stock_smart:login')

def search(request):
    """
    Vista para la búsqueda de productos
    """
    query = request.GET.get('q', '')
    products = []  # Lista vacía temporal
    
    # Cuando tengas el modelo Product implementado, descomenta esto:
    # if query:
    #     products = Product.objects.filter(
    #         Q(name__icontains=query) |
    #         Q(description__icontains=query)
    #     )
    
    context = {
        'query': query,
        'products': products,
    }
    return render(request, 'stock_smart/search.html', context)

def about_view(request):
    return render(request, 'stock_smart/about.html')

def contact_view(request):
    return render(request, 'stock_smart/contacto.html')

def terms_view(request):
    return render(request, 'stock_smart/terminos.html')

def tracking_view(request):
    return render(request, 'stock_smart/seguimiento.html')

def help_view(request):
    return render(request, 'stock_smart/ayuda.html')

def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    # Obtener productos de la categoría
    products = Product.objects.filter(
        category=category,
        stock__gt=0
    ).order_by('-created_at')
    
    # Obtener categorías para el mega menú
    main_categories = Category.objects.filter(
        parent__isnull=True,
        is_active=True
    ).prefetch_related('children')
    
    context = {
        'category': category,
        'products': products,
        'main_categories': main_categories,
    }
    return render(request, 'stock_smart/category.html', context)

@require_POST
@ensure_csrf_cookie
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product_id=product_id,
                defaults={'quantity': 0}
            )
            cart_item.quantity += 1
            cart_item.save()
            
            total_items = cart.get_total_items()
        else:
            cart = request.session.get('cart', {})
            cart_item = cart.get(str(product_id), {'quantity': 0})
            cart_item['quantity'] += 1
            cart[str(product_id)] = cart_item
            request.session['cart'] = cart
            
            total_items = sum(item['quantity'] for item in cart.values())

        return JsonResponse({
            'success': True,
            'message': 'Producto añadido al carrito',
            'total_items': total_items
        })
        
    except Exception as e:
        print(f"Error en add_to_cart: {str(e)}")  # Para debugging
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

def products(request):
    products_list = Product.objects.all()
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        products_list = products_list.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    
    # Ordenamiento
    order = request.GET.get('order')
    if order:
        if order == 'price_asc':
            products_list = products_list.order_by('price')
        elif order == 'price_desc':
            products_list = products_list.order_by('-price')
        elif order == 'name':
            products_list = products_list.order_by('name')
    
    # Paginación
    paginator = Paginator(products_list, 9)  # 9 productos por página
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'products': products,
    }
    return render(request, 'stock_smart/products.html', context)

def checkout_options(request):
    # Obtener el total y cantidad de items del carrito
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
        total = sum(item.product.get_final_price() * item.quantity for item in cart.cartitem_set.all())
        item_count = cart.get_total_items()
    else:
        cart = request.session.get('cart', {})
        total = 0
        item_count = 0
        for product_id, item_data in cart.items():
            product = Product.objects.get(id=product_id)
            total += product.get_final_price() * item_data['quantity']
            item_count += item_data['quantity']

    context = {
        'total': total,
        'item_count': item_count
    }
    return render(request, 'stock_smart/checkout_options.html', context)

def checkout_view(request, product_id=None):
    # Si el usuario no está autenticado y no viene de checkout_options, redirigir
    if not request.user.is_authenticated and 'guest_checkout' not in request.session:
        return redirect('stock_smart:checkout_options')
    
    # Resto de la lógica del checkout...
    return render(request, 'stock_smart/checkout.html', context)

def checkout_guest(request):
    # Marcar que el usuario eligió checkout como invitado
    request.session['guest_checkout'] = True
    return redirect('stock_smart:checkout')

def categories(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'stock_smart/categories.html', context)

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'stock_smart/categoria_detalle.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'stock_smart/producto_detalle.html', context)

@login_required
def profile(request):
    user = request.user
    context = {
        'user': user,
        # Puedes agregar más información del usuario aquí
        'orders': user.order_set.all() if hasattr(user, 'order_set') else [],
    }
    return render(request, 'stock_smart/profile.html', context)

def cart_view(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.cartitem_set.all()
    else:
        cart_items = []
        cart_data = request.session.get('cart', {})
        for product_id, item_data in cart_data.items():
            product = Product.objects.get(id=product_id)
            cart_items.append({
                'product': product,
                'quantity': item_data['quantity']
            })

    # Calcular totales
    subtotal = 0
    total_discount = 0
    for item in cart_items:
        product = item['product'] if isinstance(item, dict) else item.product
        quantity = item['quantity'] if isinstance(item, dict) else item.quantity
        
        original_price = product.price * quantity
        subtotal += original_price
        
        if product.discount_percentage > 0:
            discount = (original_price * product.discount_percentage) / 100
            total_discount += discount

    total = subtotal - total_discount

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total_discount': total_discount,
        'total': total,
        'cart_count': len(cart_items)
    }
    return render(request, 'stock_smart/cart.html', context)

def update_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        change = data.get('change', 0)
        
        try:
            product = Product.objects.get(id=product_id)
            
            if request.user.is_authenticated:
                cart, _ = Cart.objects.get_or_create(user=request.user)
                cart_item, _ = CartItem.objects.get_or_create(cart=cart, product=product)
                cart_item.quantity = max(1, cart_item.quantity + change)
                cart_item.save()
                cart_items = cart.cartitem_set.all()
            else:
                cart = request.session.get('cart', {})
                if str(product_id) not in cart:
                    cart[str(product_id)] = {'quantity': 1}
                else:
                    cart[str(product_id)]['quantity'] = max(1, cart[str(product_id)]['quantity'] + change)
                request.session['cart'] = cart
                request.session.modified = True
                
                # Crear lista de items para carrito de sesión
                cart_items = []
                for pid, item_data in cart.items():
                    p = Product.objects.get(id=pid)
                    cart_items.append({
                        'product': p,
                        'quantity': item_data['quantity']
                    })

            # Calcular totales
            subtotal = 0
            total_discount = 0
            cart_count = 0
            item_total = 0

            for item in cart_items:
                p = item.product if hasattr(item, 'product') else item['product']
                q = item.quantity if hasattr(item, 'quantity') else item['quantity']
                
                if str(p.id) == str(product_id):
                    item_total = p.get_final_price() * q
                
                subtotal += p.price * q
                if p.discount_percentage > 0:
                    discount = (p.price * p.discount_percentage / 100) * q
                    total_discount += discount
                
                cart_count += q

            total = subtotal - total_discount

            return JsonResponse({
                'success': True,
                'item_total': float(item_total),
                'subtotal': float(subtotal),
                'total_discount': float(total_discount),
                'total': float(total),
                'cart_count': cart_count
            })
            
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'})
            
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def remove_from_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
            cart.cartitem_set.filter(product_id=product_id).delete()
        else:
            cart = request.session.get('cart', {})
            if str(product_id) in cart:
                del cart[str(product_id)]
                request.session['cart'] = cart
                request.session.modified = True
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

