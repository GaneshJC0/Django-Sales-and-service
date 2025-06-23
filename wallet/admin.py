from django.contrib import admin
from .models import Wallet

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'updated_at')  # Shown in list view
    search_fields = ('user__username', 'user__email')  # Enable search
    list_filter = ('updated_at',)