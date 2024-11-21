from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'stock_smart'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('terminos/', views.terminos, name='terminos'),
    path('privacidad/', views.privacidad, name='privacidad'),
    path('seguimiento/', views.seguimiento_envio, name='seguimiento_envio'),
    path('ayuda/', views.ayuda, name='ayuda'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)