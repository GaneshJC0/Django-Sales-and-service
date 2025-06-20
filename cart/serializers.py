from rest_framework import serializers
from store.models import Product
from .models import Cart, CartItem

from django.contrib.auth import authenticate


# Product details inside cart
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'sale_price', 'is_sale']

# CartItem serializer with product and quantity
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

# Full Cart with items
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at']
