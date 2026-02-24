from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('products/', views.products, name='products'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),

    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path(
        'cart/update/<int:id>/<str:action>/',
        views.update_cart_quantity,
        name='update_cart_quantity'
    ),
    path(
    'cart/remove/<int:id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),

path('wishlist/toggle/<int:id>/', views.toggle_wishlist, name='toggle_wishlist'),
path('wishlist/', views.wishlist_view, name='wishlist'),

    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.orders, name='orders'),
    # ADMIN
path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
path('dashboard/add-product/', views.admin_add_product, name='admin_add_product'),
path('dashboard/delete-product/<int:id>/', views.admin_delete_product, name='admin_delete_product'),
path(
    'dashboard/update-order/<int:id>/',
    views.admin_update_order_status,
    name='admin_update_order_status'
),
]