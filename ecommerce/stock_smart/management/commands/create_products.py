from django.core.management.base import BaseCommand
from django.utils.text import slugify
from stock_smart.models import Category, Product
import random
from decimal import Decimal
import uuid

class Command(BaseCommand):
    help = 'Crea productos de ejemplo con características realistas'

    def generate_unique_slug(self, name):
        base_slug = slugify(name)
        unique_id = str(uuid.uuid4())[:8]
        return f"{base_slug}-{unique_id}"

    def generate_discount(self):
        """Genera un descuento realista"""
        # 70% sin descuento, 30% con descuento
        if random.random() > 0.7:
            return random.choice([10, 15, 20, 25, 30, 40, 50])
        return 0

    def handle(self, *args, **options):
        # Definir características por categoría
        product_specs = {
            'Notebooks': {
                'brands': ['Lenovo', 'HP', 'Dell', 'Asus', 'Acer'],
                'processors': ['Intel Core i3', 'Intel Core i5', 'Intel Core i7', 'AMD Ryzen 5', 'AMD Ryzen 7'],
                'ram': ['8GB', '16GB', '32GB'],
                'storage': ['256GB SSD', '512GB SSD', '1TB SSD', '1TB HDD'],
                'screen': ['14"', '15.6"', '17.3"'],
                'price_range': (399990, 1499990)
            },
            'PC Escritorio': {
                'brands': ['HP', 'Dell', 'Lenovo', 'Custom Build'],
                'processors': ['Intel Core i5', 'Intel Core i7', 'Intel Core i9', 'AMD Ryzen 5', 'AMD Ryzen 7'],
                'ram': ['8GB', '16GB', '32GB', '64GB'],
                'storage': ['512GB SSD', '1TB SSD', '2TB HDD'],
                'price_range': (499990, 2499990)
            },
            'Smartphones': {
                'models': {
                    'Apple iPhone': ['iPhone 13', 'iPhone 14', 'iPhone 15'],
                    'Samsung Galaxy': ['S23', 'S23+', 'S23 Ultra', 'A54', 'A34'],
                    'Xiaomi': ['Redmi Note 12', 'Poco X5', 'Mi 13']
                },
                'storage': ['128GB', '256GB', '512GB'],
                'colors': ['Negro', 'Blanco', 'Azul', 'Dorado'],
                'price_range': (199990, 1599990)
            },
            'Monitores': {
                'brands': ['Samsung', 'LG', 'Asus', 'BenQ', 'AOC'],
                'sizes': ['24"', '27"', '32"', '34"'],
                'resolution': ['1080p', '2K', '4K'],
                'panel': ['IPS', 'VA', 'TN'],
                'refresh_rate': ['60Hz', '75Hz', '144Hz', '165Hz'],
                'price_range': (99990, 799990)
            },
            'Consolas': {
                'products': [
                    ('PlayStation 5', 699990),
                    ('PlayStation 5 Digital', 599990),
                    ('Xbox Series X', 699990),
                    ('Xbox Series S', 399990),
                    ('Nintendo Switch OLED', 399990),
                    ('Nintendo Switch', 299990)
                ]
            },
            'Videojuegos': {
                'platforms': ['PS5', 'PS4', 'Xbox Series X|S', 'Nintendo Switch'],
                'genres': ['Acción', 'Aventura', 'Deportes', 'RPG', 'Shooter'],
                'price_range': (29990, 69990)
            },
            'Audífonos': {
                'brands': ['Sony', 'JBL', 'Apple', 'Samsung', 'Bose'],
                'types': ['In-ear', 'Over-ear', 'On-ear'],
                'wireless': ['Bluetooth', 'Alámbrico'],
                'price_range': (9990, 399990)
            }
        }

        try:
            # Limpiamos productos existentes
            Product.objects.all().delete()
            
            all_products = []  # Lista para almacenar todos los productos creados
            products_created = 0
            categories = Category.objects.all()

            for category in categories:
                if category.name in product_specs:
                    specs = product_specs[category.name]
                    
                    num_products = random.randint(30, 50)
                    
                    for _ in range(num_products):
                        if category.name == 'Consolas':
                            for console, price in specs['products']:
                                product = Product.objects.create(
                                    name=console,
                                    slug=self.generate_unique_slug(console),
                                    description=self.generate_description(category.name, console),
                                    price=price,
                                    discount_percentage=self.generate_discount(),
                                    category=category,
                                    stock=random.randint(5, 20),
                                    featured=False  # Se actualizará después
                                )
                                all_products.append(product)
                                products_created += 1
                                
                        elif category.name in ['Smartphones', 'Audífonos']:
                            # Lógica para smartphones y audífonos
                            if category.name == 'Smartphones':
                                brand = random.choice(list(specs['models'].keys()))
                                model = random.choice(specs['models'][brand])
                                storage = random.choice(specs['storage'])
                                color = random.choice(specs['colors'])
                                name = f"{brand} {model} {storage} {color}"
                            else:
                                brand = random.choice(specs['brands'])
                                type_ = random.choice(specs['types'])
                                wireless = random.choice(specs['wireless'])
                                name = f"{brand} {type_} {wireless}"
                            
                            price = random.randint(specs['price_range'][0], specs['price_range'][1])
                            discount = random.choice([0, 0, 0, 10, 15, 20])
                            
                            product = Product.objects.create(
                                name=name,
                                slug=self.generate_unique_slug(name),
                                description=self.generate_description(category.name, name),
                                price=price,
                                discount_percentage=self.generate_discount(),
                                category=category,
                                stock=random.randint(5, 50),
                                featured=False  # Se actualizará después
                            )
                            all_products.append(product)
                            products_created += 1
                            
                        else:
                            # Lógica general para otros productos
                            if 'brands' in specs:
                                brand = random.choice(specs['brands'])
                                if category.name == 'Notebooks':
                                    processor = random.choice(specs['processors'])
                                    ram = random.choice(specs['ram'])
                                    storage = random.choice(specs['storage'])
                                    screen = random.choice(specs['screen'])
                                    name = f"{brand} {processor} {ram} {storage} {screen}"
                                elif category.name == 'Monitores':
                                    size = random.choice(specs['sizes'])
                                    resolution = random.choice(specs['resolution'])
                                    refresh = random.choice(specs['refresh_rate'])
                                    name = f"{brand} Monitor {size} {resolution} {refresh}"
                                else:
                                    name = f"{brand} {category.name}"
                                
                                price = random.randint(specs['price_range'][0], specs['price_range'][1])
                                discount = random.choice([0, 0, 0, 10, 15, 20])
                                
                                product = Product.objects.create(
                                    name=name,
                                    slug=self.generate_unique_slug(name),
                                    description=self.generate_description(category.name, name),
                                    price=price,
                                    discount_percentage=self.generate_discount(),
                                    category=category,
                                    stock=random.randint(5, 50),
                                    featured=False  # Se actualizará después
                                )
                                all_products.append(product)
                                products_created += 1

            # Seleccionar 23 productos al azar para marcarlos como destacados
            featured_products = random.sample(all_products, 23)
            for product in featured_products:
                product.featured = True
                product.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Se crearon exitosamente {products_created} productos\n'
                    f'Se marcaron 23 productos como destacados\n'
                    f'Productos con descuento: {sum(1 for p in all_products if p.discount_percentage > 0)}'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creando productos: {str(e)}')
            )

    def generate_description(self, category, name):
        """Genera una descripción realista basada en la categoría y nombre del producto"""
        if 'Notebook' in category:
            return f"""
            {name}
            - Ideal para trabajo y productividad
            - Windows 11 Home
            - Pantalla antirreflejo
            - Webcam HD
            - Bluetooth 5.0
            - WiFi 6
            - Batería de larga duración
            """
        elif 'Smartphone' in category:
            return f"""
            {name}
            - Pantalla AMOLED
            - Cámara principal de alta resolución
            - Carga rápida
            - NFC
            - Bluetooth 5.0
            - Resistente al agua y polvo
            """
        elif 'Monitor' in category:
            return f"""
            {name}
            - Tiempo de respuesta 1ms
            - AMD FreeSync
            - HDMI y DisplayPort
            - Ajuste de altura
            - Modo Eye Saver
            """
        elif 'Consola' in category:
            return f"""
            {name}
            - Control inalámbrico incluido
            - Última generación
            - Capacidad de juego en 4K
            - Almacenamiento SSD ultrarrápido
            """
        else:
            return f"Descripción detallada de {name}. Producto de alta calidad y rendimiento."