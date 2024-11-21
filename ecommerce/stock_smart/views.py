from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import CustomUser, Pedido

def index(request):
    return render(request, 'stock_smart/index.html')

def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        nombre = request.POST['nombre']
        telefono = request.POST['telefono']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Validaciones
        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('stock_smart:register')

        # Verificar si el email ya existe
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Este email ya está registrado')
            return redirect('stock_smart:register')

        try:
            # Crear el usuario
            user = CustomUser.objects.create_user(
                username=email,  # Usamos el email como username
                email=email,
                password=password,
                first_name=nombre,
                telefono=telefono
            )
            
            # Iniciar sesión automáticamente
            login(request, user)
            
            # Mensaje de éxito
            messages.success(request, '¡Registro exitoso! Bienvenido a Stock Smart')
            
            # Redirigir al inicio
            return redirect('stock_smart:index')

        except Exception as e:
            messages.error(request, f'Error al crear el usuario: {str(e)}')
            return redirect('stock_smart:register')

    return render(request, 'stock_smart/register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido de nuevo, {user.first_name or user.email}!')
            return redirect('stock_smart:index')
        else:
            messages.error(request, 'Email o contraseña incorrectos')
    
    return render(request, 'stock_smart/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, '¡Has cerrado sesión exitosamente!')
    return redirect('stock_smart:index')

def terminos(request):
    return render(request, 'stock_smart/terminos.html')

def privacidad(request):
    return render(request, 'stock_smart/privacidad.html')

def seguimiento_envio(request):
    numero_seguimiento = request.GET.get('numero')
    pedido = None
    error = None

    if numero_seguimiento:
        try:
            pedido = Pedido.objects.get(numero_seguimiento=numero_seguimiento)
        except Pedido.DoesNotExist:
            error = "Número de seguimiento no encontrado"

    return render(request, 'stock_smart/seguimiento.html', {
        'pedido': pedido,
        'error': error,
        'numero_seguimiento': numero_seguimiento
    })

def ayuda(request):
    return render(request, 'stock_smart/ayuda.html')