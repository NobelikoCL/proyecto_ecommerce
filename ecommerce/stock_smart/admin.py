from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from .models import Producto, Categoria, Marca, PerfilUsuario, Favorito, Subcategoria, Category

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio', 'precio_oferta', 'destacado', 'super_oferta', 'activo']
    list_filter = ['categoria', 'destacado', 'super_oferta', 'activo']
    search_fields = ['nombre', 'descripcion']
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ['precio', 'precio_oferta', 'destacado', 'super_oferta', 'activo']

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo']
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

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name_with_level', 'parent', 'order', 'is_active', 'product_count', 'image_preview']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_active']
    
    def name_with_level(self, obj):
        level = '-- ' * (obj.parent.level if obj.parent else 0)
        return format_html('{}{}'.format(level, obj.name))
    name_with_level.short_description = 'Nombre'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.image.url)
        return '-'
    image_preview.short_description = 'Vista previa'
    
    def product_count(self, obj):
        count = obj.product_set.count()
        return format_html('<span style="color: {};">{}</span>', 
                         'green' if count > 0 else 'red', 
                         count)
    product_count.short_description = 'Productos'

# Personalizar el admin
admin.site.site_header = 'Administración de Stock Smart'
admin.site.site_title = 'Stock Smart'
admin.site.index_title = 'Panel de Control'

# Eliminar la función dashboard_view si existe
# El panel de administración usará la vista por defecto de Django
