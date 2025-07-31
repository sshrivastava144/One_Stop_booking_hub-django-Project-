# sabji_market/admin.py
from django.contrib import admin
from .models import (
    ShopCategory, ProductCategory, Shop, Product, Cart, CartItem,
    Order, OrderItem, ShopReview, ShopRegistrationPayment
)

@admin.register(ShopCategory)
class ShopCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'city', 'status', 'is_open', 'registration_fee_paid', 'created_at']
    list_filter = ['status', 'is_open', 'registration_fee_paid', 'is_delivery_available', 'city', 'created_at']
    search_fields = ['name', 'owner__username', 'owner__email', 'phone_number', 'city']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'name', 'owner_name', 'category')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'address', 'city', 'pincode')
        }),
        ('Shop Details', {
            'fields': ('shop_image', 'description')
        }),
        ('Status & Settings', {
            'fields': ('status', 'is_open', 'is_delivery_available', 'delivery_charge', 'registration_fee_paid')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Product)  
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'shop', 'category', 'price', 'get_discounted_price', 'stock_quantity', 'is_available', 'created_at']
    list_filter = ['is_available', 'is_organic', 'category', 'shop__city', 'created_at']
    search_fields = ['name', 'shop__name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('shop', 'name', 'category', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'discount_percentage', 'unit', 'stock_quantity')
        }),
        ('Settings', {
            'fields': ('image', 'is_available', 'is_organic')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['get_total_price']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_total_items', 'get_total_price', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['get_total_price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'customer', 'shop', 'status', 'delivery_type', 'total_amount', 'created_at']
    list_filter = ['status', 'delivery_type', 'shop__city', 'created_at']
    search_fields = ['order_id', 'customer__username', 'customer__email', 'shop__name', 'customer_phone']
    readonly_fields = ['order_id', 'created_at', 'updated_at']
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'customer', 'shop', 'status')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_phone', 'delivery_type', 'delivery_address')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'delivery_charge', 'total_amount')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    inlines = [OrderItemInline]

@admin.register(ShopReview)
class ShopReviewAdmin(admin.ModelAdmin):
    list_display = ['shop', 'customer', 'rating', 'created_at']
    list_filter = ['rating', 'created_at', 'shop__city']
    search_fields = ['shop__name', 'customer__username', 'comment']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ShopRegistrationPayment)
class ShopRegistrationPaymentAdmin(admin.ModelAdmin):
    list_display = ['shop', 'amount', 'status', 'payment_method', 'transaction_id', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['shop__name', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at']