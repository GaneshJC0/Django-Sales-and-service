from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ProductImageViewSet, ProfileViewSet, MobileBannerViewSet, ShippingAddressViewSet, create_order, user_order_history_api 
from . import views
from cart.api_views import CartView, AddToCartView, UpdateCartView, DeleteFromCartView, CartTotalView
from wallet.api_views import get_wallet_balance,get_wallet_transactions
from payment.api_views import PaymentViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-images', ProductImageViewSet)
router.register(r'banners', MobileBannerViewSet)
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'shipping-address', ShippingAddressViewSet, basename='shipping_address')
router.register(r'payment', PaymentViewSet, basename='payment')


urlpatterns = [
    path('', include(router.urls)),
    path('get_csrf_token/', views.get_csrf_token, name='get_csrf_token'),
   
    path('orders/history/', user_order_history_api, name='user_order_history'),
    path('user/referrals/', views.referred_users_view, name='user-referrals'),
    path('cart/', CartView.as_view(), name='api_cart'),
    path('cart/add/', AddToCartView.as_view(), name='api_cart_add'),
    path('cart/update/', UpdateCartView.as_view(), name='api_cart_update'),
    path('cart/delete/', DeleteFromCartView.as_view(), name='api_cart_delete'),
    path('cart/total/', CartTotalView.as_view(), name='api_cart_total'),
    path('wallet/balance/', get_wallet_balance, name='wallet-balance'),
    path('wallet/transactions/', get_wallet_transactions, name='wallet-transactions'),
	
]



