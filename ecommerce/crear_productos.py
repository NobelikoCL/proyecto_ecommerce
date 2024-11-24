# crear_productos.py
import os
import django
import random
import string

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

# Importar modelos
from stock_smart.models import Producto, Categoria, Marca

def generar_sku():
    # Genera un SKU único de 8 caracteres
    letras = ''.join(random.choices(string.ascii_uppercase, k=3))
    numeros = ''.join(random.choices(string.digits, k=5))
    return f"{letras}{numeros}"

def crear_productos_por_categoria():
    # Plantillas de productos por tipo de categoría
    plantillas = {
        "Procesadores": [
            {"base": "Core i3", "precio_base": 129990},
            {"base": "Core i5", "precio_base": 199990},
            {"base": "Core i7", "precio_base": 399990},
            {"base": "Core i9", "precio_base": 699990},
            {"base": "Ryzen 5", "precio_base": 249990},
            {"base": "Ryzen 7", "precio_base": 449990},
            {"base": "Ryzen 9", "precio_base": 749990},
        ],
        "Tarjetas de Video": [
            {"base": "RTX 4060", "precio_base": 399990},
            {"base": "RTX 4070", "precio_base": 849990},
            {"base": "RTX 4080", "precio_base": 1499990},
            {"base": "RTX 4090", "precio_base": 2499990},
            {"base": "RX 7600", "precio_base": 349990},
            {"base": "RX 7700", "precio_base": 799990},
            {"base": "RX 7800", "precio_base": 999990},
        ],
        "Memorias RAM": [
            {"base": "DDR4", "precio_base": 49990},
            {"base": "DDR5", "precio_base": 89990},
        ],
        "Almacenamiento": [
            {"base": "SSD", "precio_base": 49990},
            {"base": "M.2 NVMe", "precio_base": 79990},
            {"base": "HDD", "precio_base": 39990},
        ]
    }

    # Variaciones para cada tipo de producto
    variaciones = {
        "Procesadores": ["", "K", "F", "KF", "X", "XT"],
        "Tarjetas de Video": ["Gaming", "OC", "Gaming OC", "SUPER", "Ti"],
        "Memorias RAM": ["8GB", "16GB", "32GB", "RGB", "Pro", "Elite"],
        "Almacenamiento": ["250GB", "500GB", "1TB", "2TB", "4TB", "8TB"]
    }

    productos_creados = 0
    errores = 0

    # Obtener todas las categorías activas
    categorias = Categoria.objects.filter(activo=True)
    marcas = Marca.objects.filter(activo=True)

    print("Iniciando creación de productos...")

    for categoria in categorias:
        # Encontrar la plantilla adecuada para la categoría
        plantilla_key = next((k for k in plantillas.keys() if k.lower() in categoria.nombre.lower()), None)
        
        if plantilla_key:
            plantilla = plantillas[plantilla_key]
            variacion = variaciones.get(plantilla_key, ["Standard"])
            
            # Crear 100 productos para esta categoría
            for i in range(100):
                try:
                    # Seleccionar una plantilla base aleatoria
                    base = random.choice(plantilla)
                    marca = random.choice(marcas)
                    var = random.choice(variacion)
                    
                    # Generar precio con variación
                    precio_base = base["precio_base"]
                    precio = int(precio_base * random.uniform(0.9, 1.1))
                    
                    # Generar nombre del producto
                    nombre = f"{marca.nombre} {base['base']} {var}".strip()
                    
                    # Crear producto
                    nuevo_producto = Producto.objects.create(
                        nombre=nombre,
                        descripcion=f"Producto {marca.nombre} de alta calidad. {nombre} con garantía oficial.",
                        precio=precio,
                        stock=random.randint(5, 50),
                        categoria=categoria,
                        marca=marca,
                        sku=generar_sku(),
                        activo=True
                    )
                    
                    productos_creados += 1
                    if productos_creados % 10 == 0:  # Mostrar progreso cada 10 productos
                        print(f"Creados {productos_creados} productos...")
                    
                except Exception as e:
                    errores += 1
                    print(f"Error creando producto para {categoria.nombre}: {str(e)}")

    print(f"\nResumen:")
    print(f"Productos creados exitosamente: {productos_creados}")
    print(f"Errores encontrados: {errores}")
    print(f"Total productos en BD: {Producto.objects.count()}")
    
    # Mostrar resumen por categoría
    print("\nProductos por categoría:")
    for cat in Categoria.objects.all():
        count = Producto.objects.filter(categoria=cat).count()
        if count > 0:
            print(f"- {cat.nombre}: {count} productos")

if __name__ == '__main__':
    print("Verificando categorías y marcas...")
    print(f"Categorías disponibles: {Categoria.objects.count()}")
    print(f"Marcas disponibles: {Marca.objects.count()}")
    
    crear_productos_por_categoria()