"""
URL configuration for ecom project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as account_views
from home import views as home_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_views.home, name='home'),
    path('products/', home_views.products, name='products'),
    path('product/<int:pk>/', home_views.product_detail, name='product_detail'),
    
    # Cart URLs
    path('cart/', home_views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', home_views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:cart_item_id>/', home_views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:cart_item_id>/', home_views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout URLs
    path('checkout/', home_views.checkout, name='checkout'),
    path('checkout/address/', home_views.select_address, name='select_address'),
    path('checkout/payment/', home_views.payment, name='payment'),
    path('checkout/process-payment/', home_views.process_payment, name='process_payment'),
    path('order-confirmation/<int:order_id>/', home_views.order_confirmation, name='order_confirmation'),
    
    # Chatbot API
    path('api/chatbot/', home_views.chatbot_query, name='chatbot_query'),
    
    # Auth URLs
    path('signup/', account_views.signup, name='signup'),
    path('login/', account_views.user_login, name='login'),
    path('logout/', account_views.user_logout, name='logout'),
    path('profile/', account_views.profile, name='profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
