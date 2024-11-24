from django.contrib import admin
from django.db.models import Count
from .models import Producto, Categoria, Marca, PerfilUsuario, Favorito, Subcategoria

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'marca', 'activo')
    list_filter = ('categoria', 'marca', 'activo')
    search_fields = ('nombre', 'descripcion')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'telefono']
    search_fields = ['usuario__username', 'telefono']

@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'producto', 'fecha_agregado']
    list_filter = ['fecha_agregado']
    search_fields = ['usuario__username', 'producto__nombre']

@admin.register(Subcategoria)
class SubcategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'activo']
    list_filter = ['activo', 'categoria']
    search_fields = ['nombre']

# Personalizar el admin
admin.site.site_header = 'Administración de Stock Smart'
admin.site.site_title = 'Stock Smart'
admin.site.index_title = 'Panel de Control'

# Eliminar la función dashboard_view si existe
# El panel de administración usará la vista por defecto de Django
