from .models import Categoria

def categorias_menu(request):
    """Context processor para tener las categorías disponibles en todos los templates"""
    categorias = Categoria.objects.filter(activo=True).prefetch_related('subcategoria_set')
    return {'categorias_menu': categorias}