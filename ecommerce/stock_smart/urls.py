from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'stock_smart'

urlpatterns = [
    # URL principal
    path('', views.index, name='index'),
    
    # URLs de productos y categorías
    path('products/', views.products, name='products'),
    path('categories/', views.categories, name='categories'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('category/<slug:slug>/', views.category_view, name='category'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    
    # URLs de carrito y checkout
    path('api/cart/add/', views.add_to_cart, name='add_to_cart'),
    path('checkout/options/', views.checkout_options, name='checkout_options'),
    path('checkout/guest/', views.checkout_guest, name='checkout_guest'),
    path('checkout/<int:product_id>/', views.checkout_view, name='checkout'),
    path('checkout/', views.checkout_view, name='checkout'),
    
    # URLs de cuenta y autenticación
    path('account/', views.account_view, name='account'),
    path('account/register/', views.register_view, name='register'),
    path('account/login/', views.login_view, name='login'),
    path('account/logout/', views.logout_view, name='logout'),
    path('account/verify/<str:token>/', views.verify_email, name='verify_email'),
    path('profile/', views.profile, name='profile'),
    
    # Páginas informativas
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('terms/', views.terms_view, name='terms'),
    path('tracking/', views.tracking_view, name='tracking'),
    path('help/', views.help_view, name='help'),
    
    # URLs del carrito
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)