from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stock_smart.urls')),  # Esta línea es importante - la ruta vacía ''
]