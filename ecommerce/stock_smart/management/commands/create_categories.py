from django.core.management.base import BaseCommand
from stock_smart.models import Category

class Command(BaseCommand):
    help = 'Crea las categorías iniciales para la tienda'

    def handle(self, *args, **options):
        self.stdout.write('Creando categorías...')

        categories_data = {
            'Computación': [
                'Notebooks',
                'PC Escritorio',
                'Monitores',
                'Impresoras',
                'Accesorios Computación'
            ],
            'Smartphones': [
                'Apple iPhone',
                'Samsung Galaxy',
                'Xiaomi',
                'Accesorios Celulares',
                'Smartwatch'
            ],
            'Gaming': [
                'Consolas',
                'Videojuegos',
                'Accesorios Gaming',
                'Sillas Gamer',
                'Notebooks Gamer'
            ],
            'Audio': [
                'Audífonos',
                'Parlantes',
                'Audio Profesional',
                'Micrófonos',
                'Equipos de Sonido'
            ]
        }

        try:
            # Eliminar categorías existentes (opcional)
            # Category.objects.all().delete()

            for main_category, subcategories in categories_data.items():
                # Crear categoría principal
                main_cat, created = Category.objects.get_or_create(
                    name=main_category,
                    defaults={
                        'order': list(categories_data.keys()).index(main_category),
                        'is_active': True,
                        'slug': None  # Se generará automáticamente en el save()
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Categoría principal creada: {main_category}')
                    )
                
                # Crear subcategorías
                for index, subcat_name in enumerate(subcategories):
                    subcat, created = Category.objects.get_or_create(
                        name=subcat_name,
                        parent=main_cat,
                        defaults={
                            'order': index,
                            'is_active': True,
                            'slug': None  # Se generará automáticamente en el save()
                        }
                    )
                    
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f'Subcategoría creada: {subcat_name} en {main_category}')
                        )

            self.stdout.write(
                self.style.SUCCESS('Todas las categorías han sido creadas exitosamente')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creando categorías: {str(e)}')
            )