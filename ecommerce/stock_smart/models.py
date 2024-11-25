from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from django.conf import settings
from django.core.exceptions import ValidationError
from unidecode import unidecode
from decimal import Decimal

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    rut = models.CharField(max_length=12, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)
    
    # Campos para verificación de email
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    # Agregar related_name para evitar conflictos
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.'
    )

    def __str__(self):
        return self.email

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de envío'),
        ('PREPARACION', 'En preparación'),
        ('ENVIADO', 'Enviado'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]

    cliente = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='pedidos'
    )
    numero_seguimiento = models.CharField(
        max_length=15, 
        unique=True,
        editable=False,
        verbose_name='Número de seguimiento'
    )
    fecha_pedido = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha del pedido'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE',
        verbose_name='Estado del pedido'
    )
    direccion_envio = models.TextField(
        verbose_name='Dirección de envío',
        default=''
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Subtotal'
    )
    descuento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Descuento'
    )
    iva = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='IVA'
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Total del pedido'
    )

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_pedido']

    def save(self, *args, **kwargs):
        if not self.numero_seguimiento:
            fecha = timezone.now()
            pedidos_hoy = Pedido.objects.filter(
                fecha_pedido__date=fecha.date()
            ).count()
            self.numero_seguimiento = f"{fecha.strftime('%d%m%Y')}{str(pedidos_hoy + 1).zfill(3)}"
        
        if not self.iva:
            self.iva = round(float(self.subtotal) * 0.19, 2)
        
        if not self.total:
            self.total = self.subtotal + self.iva - self.descuento
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pedido {self.numero_seguimiento}"

    @property
    def items(self):
        return self.pedidoitem_set.all()

class SeguimientoPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='seguimientos'
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de actualización'
    )
    estado = models.CharField(
        max_length=20,
        choices=Pedido.ESTADO_CHOICES,
        verbose_name='Estado'
    )
    descripcion = models.TextField(
        verbose_name='Descripción del estado'
    )
    ubicacion = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Ubicación'
    )

    class Meta:
        verbose_name = 'Seguimiento de pedido'
        verbose_name_plural = 'Seguimientos de pedidos'
        ordering = ['-fecha']

    def __str__(self):
        return f"Seguimiento {self.pedido.numero_seguimiento} - {self.estado}"

class Favorito(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    producto = models.ForeignKey(
        'stock_smart.Producto',
        on_delete=models.CASCADE
    )
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'producto')

    def __str__(self):
        return f"{self.usuario.username} - {self.producto.nombre}"

class ConfiguracionTienda(models.Model):
    nombre_tienda = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='tienda/')
    favicon = models.ImageField(upload_to='tienda/')
    descripcion = models.TextField()
    email_contacto = models.EmailField()
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()
    meta_description = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)
    google_analytics_id = models.CharField(max_length=50, blank=True)
    facebook_pixel_id = models.CharField(max_length=50, blank=True)

class RedSocial(models.Model):
    nombre = models.CharField(max_length=50)
    url = models.URLField()
    activa = models.BooleanField(default=True)
    pixel_id = models.CharField(max_length=100, blank=True)
    tracking_code = models.TextField(blank=True)

class ConfiguracionEnvio(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tiempo_estimado = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)
    regiones = models.ManyToManyField('Region')
    precio_por_peso = models.BooleanField(default=False)

class Region(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
    
class MetodoPago(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    activo = models.BooleanField(default=True)
    comision = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    imagen = models.ImageField(upload_to='metodos_pago/')

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.nombre))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

class Marca(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

    def clean(self):
        if not self.nombre or not self.nombre.strip():
            raise ValidationError('El nombre de la marca no puede estar vacío')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, null=True)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos'
    )
    activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    super_oferta = models.BooleanField(default=False)
    stock = models.PositiveIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    featured = models.BooleanField(default=False, verbose_name="Destacado")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Porcentaje de descuento")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nombre)
            slug = base_slug
            n = 1
            # Mientras exista un producto con el mismo slug, agregar un número al final
            while Producto.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['-fecha_creacion']

    def get_discount_amount(self):
        """Calcula el monto del descuento"""
        return int((self.price * self.discount_percentage) / 100)

    def get_final_price(self):
        """Calcula el precio final después del descuento"""
        return self.price - self.get_discount_amount()

class Subcategoria(models.Model):
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(
        'stock_smart.Categoria',
        on_delete=models.CASCADE
    )
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class ConfiguracionHome(models.Model):
    productos_por_columna = models.IntegerField(
        default=5,
        help_text="Número de productos por columna"
    )
    productos_destacados_visible = models.BooleanField(
        default=True,
        verbose_name="Mostrar Productos Destacados"
    )
    productos_vendidos_visible = models.BooleanField(
        default=True,
        verbose_name="Mostrar Productos Más Vendidos"
    )
    productos_nuevos_visible = models.BooleanField(
        default=True,
        verbose_name="Mostrar Productos Nuevos"
    )

    class Meta:
        verbose_name = "Configuración del Home"
        verbose_name_plural = "Configuraciones del Home"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def cargar(cls):
        config, _ = cls.objects.get_or_create(pk=1)
        return config

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    direccion = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f'Perfil de {self.user.username}'

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                             related_name='children', verbose_name="Categoría padre")
    image = models.ImageField(upload_to='categories/', null=True, blank=True, 
                            verbose_name="Imagen")
    order = models.IntegerField(default=0, verbose_name="Orden")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def has_products(self):
        return self.product_set.exists() or any(child.product_set.exists() for child in self.children.all())
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['order', 'name']

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Descripción")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Porcentaje de descuento")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name="Categoría")
    stock = models.IntegerField(default=0, verbose_name="Stock")
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="Imagen")
    featured = models.BooleanField(default=False, verbose_name="Destacado")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_discount_amount(self):
        """Calcula el monto del descuento"""
        return int((self.price * self.discount_percentage) / 100)

    def get_final_price(self):
        """Calcula el precio final después del descuento"""
        return self.price - self.get_discount_amount()

    @property
    def has_discount(self):
        return self.discount_percentage > 0

    def get_discount_amount(self):
        """Calcula el monto del descuento"""
        if self.discount_percentage > 0:
            return (self.price * self.discount_percentage) / 100
        return 0

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_items(self):
        return sum(item.quantity for item in self.cartitem_set.all())

    def get_total_price(self):
        return sum(item.get_subtotal() for item in self.cartitem_set.all())

    def __str__(self):
        return f"Carrito de {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_subtotal(self):
        return self.product.get_final_price() * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product.name} en carrito de {self.cart.user.username}"

    class Meta:
        unique_together = ('cart', 'product')