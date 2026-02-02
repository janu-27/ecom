from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_featured', 'rating', 'created_at']
    list_filter = ['category', 'is_featured', 'created_at']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'discount_price', 'stock')
        }),
        ('Images & Media', {
            'fields': ('image', 'image_alt')
        }),
        ('Reviews & Rating', {
            'fields': ('rating', 'total_reviews')
        }),
        ('Display Options', {
            'fields': ('is_featured',)
        }),
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user__username']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'cart', 'quantity', 'added_at']
    list_filter = ['added_at']
    search_fields = ['product__name', 'cart__user__username']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'id']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'status', 'total_amount')
        }),
        ('Delivery Address', {
            'fields': ('shipping_address', 'phone', 'city', 'postal_code')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'order', 'quantity', 'price']
    search_fields = ['product__name', 'order__id']
