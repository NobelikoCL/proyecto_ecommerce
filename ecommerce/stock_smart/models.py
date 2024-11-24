from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from django.conf import settings
from django.core.exceptions import ValidationError
from unidecode import unidecode

class CustomUser(AbstractUser):
    CLIENTE = 'cliente'
    VENDEDOR = 'vendedor'
    ADMIN = 'admin'
    
    TIPO_USUARIO_CHOICES = [
        (CLIENTE, 'Cliente'),
        (VENDEDOR, 'Vendedor'),
        (ADMIN, 'Administrador'),
    ]

    email = models.EmailField(
        unique=True,
        verbose_name='Correo electrónico'
    )
    telefono = models.CharField(
        max_length=15,
        verbose_name='Teléfono'
    )
    tipo_usuario = models.CharField(
        max_length=10,
        choices=TIPO_USUARIO_CHOICES,
        default=CLIENTE,
        verbose_name='Tipo de usuario'
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro'
    )
    direccion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Dirección'
    )
    ciudad = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Ciudad'
    )
    pais = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='País'
    )
    nombre_tienda = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Nombre de la tienda'
    )
    descripcion_tienda = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción de la tienda'
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.email} - {self.get_tipo_usuario_display()}"

    def is_vendedor(self):
        return self.tipo_usuario == self.VENDEDOR

    def is_cliente(self):
        return self.tipo_usuario == self.CLIENTE

    def get_direccion_completa(self):
        partes = [self.direccion, self.ciudad, self.pais]
        return ', '.join(filter(None, partes))

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

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
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('AGOTADO', 'Agotado')
    ]

    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre del producto'
    )
    descripcion = models.TextField(
        verbose_name='Descripción'
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Precio'
    )
    imagen = models.ImageField(
        upload_to='productos/',
        verbose_name='Imagen'
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        related_name='productos',
        null=True,
        blank=True
    )
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Stock disponible'
    )
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='ACTIVO',
        verbose_name='Estado'
    )
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    ultima_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última modificación'
    )
    sku = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='SKU'
    )
    destacado = models.BooleanField(
        default=False,
        verbose_name='Producto destacado'
    )
    peso = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name='Peso (kg)'
    )
    marca = models.ForeignKey(
        Marca,
        on_delete=models.SET_NULL,
        verbose_name='Marca',
        related_name='productos_marca',
        null=True
    )
    activo = models.BooleanField(default=True)
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.nombre

    def actualizar_estado(self):
        if self.stock <= 0:
            self.estado = 'AGOTADO'
        elif self.estado == 'AGOTADO' and self.stock > 0:
            self.estado = 'ACTIVO'
        self.save()

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