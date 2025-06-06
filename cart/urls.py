from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add/', views.cart_add, name='cart_add'),
    path('delete', views.cart_delete, name='cart_delete'),
    path('update', views.cart_update, name='cart_update'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
]