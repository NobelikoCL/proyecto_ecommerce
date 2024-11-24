from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime
from .models import Producto, Categoria, PerfilUsuario, Favorito
from .forms import PerfilUsuarioForm, CustomUserCreationForm, CustomAuthenticationForm
from django.db import models

def index(request):
    """Vista para la página principal"""
    productos_oferta = Producto.objects.filter(activo=True).order_by('?')[:8]
    categorias = Categoria.objects.filter(activo=True)
    return render(request, 'stock_smart/index.html', {
        'productos_oferta': productos_oferta,
        'categorias': categorias
    })

def register_view(request):
    """Vista para el registro de usuarios"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        perfil_form = PerfilUsuarioForm(request.POST)
        
        if form.is_valid() and perfil_form.is_valid():
            user = form.save()
            perfil = perfil_form.save(commit=False)
            perfil.usuario = user
            perfil.save()
            
            login(request, user)
            messages.success(request, '¡Registro exitoso!')
            return redirect('index')
    else:
        form = CustomUserCreationForm()
        perfil_form = PerfilUsuarioForm()
    
    return render(request, 'registration/register.html', {
        'form': form,
        'perfil_form': perfil_form
    })

def login_view(request):
    """Vista para el inicio de sesión"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido {username}!')
                return redirect('index')
            else:
                messages.error(request, 'Usuario o contraseña inválidos.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'stock_smart/login.html', {'form': form})

def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.success(request, '¡Sesión cerrada exitosamente!')
    return redirect('index')

@login_required
def cuenta_view(request):
    """Vista para la página principal de la cuenta del usuario"""
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=request.user.perfilusuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('cuenta')
    else:
        perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
        form = PerfilUsuarioForm(instance=perfil)
    
    return render(request, 'stock_smart/cuenta.html', {'form': form})

def categoria_detalle(request, slug):
    """Vista para mostrar los productos de una categoría específica"""
    categoria = get_object_or_404(Categoria, slug=slug)
    subcategoria_slug = request.GET.get('subcategoria')
    
    productos = Producto.objects.filter(categoria=categoria, activo=True)
    
    if subcategoria_slug:
        productos = productos.filter(subcategoria__slug=subcategoria_slug)
    
    context = {
        'categoria': categoria,
        'productos': productos,
        'subcategoria_slug': subcategoria_slug
    }
    return render(request, 'stock_smart/categoria_detalle.html', context)

@login_required
def favoritos(request):
    """Vista para mostrar y gestionar los favoritos del usuario"""
    favoritos = Favorito.objects.filter(usuario=request.user).select_related('producto')
    return render(request, 'stock_smart/favoritos.html', {'favoritos': favoritos})

@login_required
def agregar_favorito(request, producto_id):
    """Vista para agregar un producto a favoritos"""
    producto = get_object_or_404(Producto, id=producto_id)
    Favorito.objects.get_or_create(usuario=request.user, producto=producto)
    messages.success(request, 'Producto agregado a favoritos')
    return redirect('favoritos')

@login_required
def eliminar_favorito(request, producto_id):
    """Vista para eliminar un producto de favoritos"""
    Favorito.objects.filter(usuario=request.user, producto_id=producto_id).delete()
    messages.success(request, 'Producto eliminado de favoritos')
    return redirect('favoritos')

@login_required
def mis_pedidos(request):
    """Vista para mostrar los pedidos del usuario"""
    # pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha')
    context = {
        'pedidos': [],  # Lista vacía por ahora
    }
    return render(request, 'stock_smart/mis_pedidos.html', context)

@login_required
def descargar_boleta(request, pedido_id):
    """Vista para generar y descargar la boleta en PDF"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="boleta_{pedido_id}.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Contenido del PDF
    elements.append(Paragraph("STOCK SMART", styles['Title']))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Av. Ejemplo 1234, Santiago", styles['Normal']))
    elements.append(Paragraph("RUT: 12.345.678-9", styles['Normal']))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"BOLETA ELECTRÓNICA N°: B-{pedido_id:06d}", styles['Heading2']))
    elements.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
    elements.append(Paragraph(f"Cliente: {request.user.get_full_name()}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Tabla de productos
    data = [
        ['Producto', 'Cantidad', 'Precio Unit.', 'Subtotal'],
        ['Producto 1', '2', '$19.990', '$39.980'],
        ['Producto 2', '1', '$59.990', '$59.990'],
    ]

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Total: $99.990", styles['Heading2']))
    elements.append(Spacer(1, 30))

    # Pie de página
    footer_style = ParagraphStyle(
        'footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1,
    )
    elements.append(Paragraph("Gracias por su compra", footer_style))
    elements.append(Paragraph("Este documento es una representación impresa de un documento tributario electrónico", footer_style))
    elements.append(Paragraph("www.stocksmart.cl", footer_style))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

# Páginas estáticas
def terminos(request):
    """Vista para la página de términos y condiciones"""
    return render(request, 'stock_smart/terminos.html')

def politicas(request):
    """Vista para la página de políticas de privacidad"""
    return render(request, 'stock_smart/politicas.html')

def privacidad(request):
    """Vista para la página de política de privacidad"""
    return render(request, 'stock_smart/privacidad.html')

def about(request):
    """Vista para la página Acerca de"""
    return render(request, 'stock_smart/about.html')

def ayuda(request):
    """Vista para la página de ayuda"""
    return render(request, 'stock_smart/ayuda.html')

def seguimiento_envio(request):
    """Vista para el seguimiento de envíos"""
    if request.method == 'POST':
        numero_seguimiento = request.POST.get('numero_seguimiento')
        messages.info(request, f'Buscando envío #{numero_seguimiento}')
        return render(request, 'stock_smart/seguimiento.html', {
            'numero_seguimiento': numero_seguimiento,
            'estado': 'En proceso'
        })
    return render(request, 'stock_smart/seguimiento.html')

@login_required
def profile(request):
    """Vista para el perfil del usuario"""
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=request.user.perfilusuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('profile')
    else:
        perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
        form = PerfilUsuarioForm(instance=perfil)
    
    context = {
        'form': form,
        'user': request.user
    }
    return render(request, 'stock_smart/profile.html', context)

def producto_detalle(request, slug):
    """Vista para mostrar el detalle de un producto"""
    producto = get_object_or_404(Producto, slug=slug, activo=True)
    
    # Productos relacionados de la misma categoría
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        activo=True
    ).exclude(id=producto.id)[:4]
    
    context = {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
    }
    return render(request, 'stock_smart/producto_detalle.html', context)

@login_required
def perfil_usuario(request):
    """Vista para el perfil del usuario"""
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=request.user.perfilusuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('perfil_usuario')
    else:
        perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
        form = PerfilUsuarioForm(instance=perfil)
    
    # Obtener pedidos del usuario
    # pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_creacion')[:5]
    
    context = {
        'form': form,
        'user': request.user,
        'perfil': perfil,
        # 'pedidos_recientes': pedidos
    }
    return render(request, 'stock_smart/perfil_usuario.html', context)

@login_required
def agregar_carrito(request, producto_id):
    """Vista para agregar un producto al carrito"""
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    cantidad = int(request.POST.get('cantidad', 1))
    
    # Inicializar el carrito en la sesión si no existe
    if 'carrito' not in request.session:
        request.session['carrito'] = {}
    
    carrito = request.session['carrito']
    
    # Agregar o actualizar producto en el carrito
    if str(producto_id) in carrito:
        carrito[str(producto_id)]['cantidad'] += cantidad
    else:
        carrito[str(producto_id)] = {
            'cantidad': cantidad,
            'precio': float(producto.precio),
            'nombre': producto.nombre
        }
    
    request.session.modified = True
    messages.success(request, f'{producto.nombre} agregado al carrito')
    
    # Si es una solicitud AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'message': 'Producto agregado al carrito',
            'cart_count': sum(item['cantidad'] for item in carrito.values())
        })
    
    return redirect('carrito')

@login_required
def comprar_ahora(request, producto_id):
    """Vista para comprar un producto inmediatamente"""
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    
    # Limpiar el carrito actual
    request.session['carrito'] = {
        str(producto_id): {
            'cantidad': 1,
            'precio': float(producto.precio),
            'nombre': producto.nombre
        }
    }
    request.session.modified = True
    
    return redirect('checkout')

@login_required
def ver_carrito(request):
    """Vista para ver el contenido del carrito"""
    carrito = request.session.get('carrito', {})
    
    # Obtener los productos completos desde la base de datos
    productos = []
    total = 0
    
    for producto_id, item in carrito.items():
        try:
            producto = Producto.objects.get(id=producto_id)
            precio = float(producto.precio_oferta if producto.precio_oferta else producto.precio)
            subtotal = item['cantidad'] * precio
            total += subtotal
            productos.append({
                'producto': producto,
                'cantidad': item['cantidad'],
                'subtotal': subtotal
            })
        except Producto.DoesNotExist:
            # Si el producto ya no existe, lo removemos del carrito
            del carrito[producto_id]
            request.session.modified = True
    
    return render(request, 'stock_smart/carrito.html', {
        'productos': productos,
        'total': total
    })

@login_required
def checkout(request):
    """Vista para el proceso de checkout"""
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('carrito')
    
    # Aquí irá la lógica del checkout
    return render(request, 'stock_smart/checkout.html')

def contacto(request):
    """Vista para la página de contacto"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')
        
        # Aquí puedes agregar la lógica para enviar el email
        # Por ahora solo mostraremos un mensaje de éxito
        messages.success(request, 'Mensaje enviado correctamente. Nos pondremos en contacto contigo pronto.')
        return redirect('contacto')
        
    return render(request, 'stock_smart/contacto.html')

def ofertas(request):
    """Vista para mostrar productos en oferta"""
    productos = Producto.objects.filter(
        activo=True,
        precio_oferta__isnull=False
    ).order_by('-precio_oferta')
    
    context = {
        'productos': productos,
        'titulo': 'Ofertas',
        'descripcion': 'Los mejores descuentos en nuestros productos'
    }
    return render(request, 'stock_smart/productos_lista.html', context)

def buscar(request):
    """Vista para el buscador de productos"""
    query = request.GET.get('q', '')
    productos = []
    
    if query:
        productos = Producto.objects.filter(
            activo=True
        ).filter(
            models.Q(nombre__icontains=query) |
            models.Q(descripcion__icontains=query) |
            models.Q(categoria__nombre__icontains=query)
        ).distinct()
    
    context = {
        'productos': productos,
        'query': query,
        'titulo': f'Resultados para: {query}' if query else 'Buscar productos'
    }
    return render(request, 'stock_smart/productos_lista.html', context)

