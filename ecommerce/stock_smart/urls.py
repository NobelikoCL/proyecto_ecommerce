from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

app_name = 'stock_smart'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('terminos/', views.terminos, name='terminos'),
    path('politicas/', views.politicas, name='politicas'),
    path('about/', views.about, name='about'),
    path('seguimiento/', views.seguimiento_envio, name='seguimiento_envio'),
    path('ayuda/', views.ayuda, name='ayuda'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('favoritos/', views.favoritos, name='favoritos'),
    path('favoritos/agregar/<int:producto_id>/', views.agregar_favorito, name='agregar_favorito'),
    path('favoritos/eliminar/<int:producto_id>/', views.eliminar_favorito, name='eliminar_favorito'),
    path('pedidos/boleta/<int:pedido_id>/', views.descargar_boleta, name='descargar_boleta'),
    path('categoria/<slug:slug>/', views.categoria_detalle, name='categoria_detalle'),
    path('privacidad/', views.privacidad, name='privacidad'),
    path('cuenta/', views.cuenta_view, name='cuenta'),
    path('cuenta/login/', views.login_view, name='login'),
    path('cuenta/registro/', views.register_view, name='register'),
    path('cuenta/logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('producto/<slug:slug>/', views.producto_detalle, name='producto_detalle'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('contacto/', views.contacto, name='contacto'),
    path('comprar-ahora/<int:producto_id>/', views.comprar_ahora, name='comprar_ahora'),
    path('carrito/', views.ver_carrito, name='carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('ofertas/', views.ofertas, name='ofertas'),
    path('buscar/', views.buscar, name='buscar'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)