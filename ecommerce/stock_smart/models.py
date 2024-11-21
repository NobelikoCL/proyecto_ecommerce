from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    # Opciones para el tipo de usuario
    CLIENTE = 'cliente'
    VENDEDOR = 'vendedor'
    ADMIN = 'admin'
    
    TIPO_USUARIO_CHOICES = [
        (CLIENTE, 'Cliente'),
        (VENDEDOR, 'Vendedor'),
        (ADMIN, 'Administrador'),
    ]

    # Campos básicos
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

    # Campos adicionales
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
    
    # Si es vendedor
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

    # Configuración del modelo
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.email} - {self.get_tipo_usuario_display()}"

    # Métodos de ayuda
    def is_vendedor(self):
        return self.tipo_usuario == self.VENDEDOR

    def is_cliente(self):
        return self.tipo_usuario == self.CLIENTE

    def get_direccion_completa(self):
        partes = [self.direccion, self.ciudad, self.pais]
        return ', '.join(filter(None, partes))

    def save(self, *args, **kwargs):
        # Asegurarse de que el email y el username sean iguales
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

    numero_seguimiento = models.CharField(
        max_length=15, 
        unique=True,
        editable=False,
        verbose_name='Número de seguimiento'
    )
    cliente = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='pedidos'
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
    direccion_envio = models.TextField(verbose_name='Dirección de envío')
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Total del pedido'
    )

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_pedido']

    def save(self, *args, **kwargs):
        if not self.numero_seguimiento:
            # Generar número de seguimiento
            fecha = timezone.now()
            # Contar pedidos del día
            pedidos_hoy = Pedido.objects.filter(
                fecha_pedido__date=fecha.date()
            ).count()
            # Formato: DDMMAAAA + número secuencial de 3 dígitos
            self.numero_seguimiento = f"{fecha.strftime('%d%m%Y')}{str(pedidos_hoy + 1).zfill(3)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pedido {self.numero_seguimiento}"

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