from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from wallet.models import WalletTransaction

@login_required
def wallet_transactions_view(request):
    transactions = WalletTransaction.objects.filter(wallet__user=request.user).order_by('-timestamp')
    return render(request, 'wallet/wallet_transactions.html', {
        'transactions': transactions
    })