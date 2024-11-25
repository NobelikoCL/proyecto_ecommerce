from .models import Category

def categories_processor(request):
    main_categories = Category.objects.filter(
        parent__isnull=True,
        is_active=True
    ).prefetch_related('children')
    
    return {
        'main_categories': main_categories
    }