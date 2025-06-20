from django.contrib import admin
from .models import Order, OrderItem ,Cart ,CartItem
# Register your models here.



from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

# cart/admin.py
from django.contrib import admin
from .models import Cart, CartItem

class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_items')

    def total_items(self, obj):
        return obj.items.count()  # uses related_name='items'

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)



admin.site.register(OrderItem)
admin.site.register(Order)
