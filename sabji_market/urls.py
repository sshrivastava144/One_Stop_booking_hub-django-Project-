from django.urls import path
from . import views

app_name = 'sabji_market'

urlpatterns = [
    # Home and general pages
    path('', views.sabji_home, name='home'),
    
    # Shop registration and management
    path('register-shop/', views.register_shop, name='register_shop'),
    path('payment/<int:shop_id>/', views.shop_payment, name='payment'),
    path('dashboard/', views.shop_dashboard, name='shop_dashboard'),
    path('shop/<int:shop_id>/', views.shop_detail, name='shop_detail'),
    path('shop/<int:shop_id>/toggle-status/', views.toggle_shop_status, name='toggle_shop_status'),
    
    # Product management
    path('shop/<int:shop_id>/add-product/', views.add_product, name='add_product'),
    path('product/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    
    # Customer shopping views
    path('shops/', views.shop_list, name='shop_list'),
    path('shop/<int:shop_id>/products/', views.shop_products, name='shop_products'),
    path('categories/', views.product_categories, name='product_categories'),
    path('category/<int:category_id>/products/', views.products_by_category, name='products_by_category'),
    
    # Cart management
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    
    # Order management
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order/<str:order_id>/', views.order_detail, name='order_detail'),
    
    # Shop owner order management
    path('shop/<int:shop_id>/orders/', views.shop_orders, name='shop_orders'),
    path('order/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    
    # Reviews
    path('shop/<int:shop_id>/review/', views.add_review, name='add_review'),
]