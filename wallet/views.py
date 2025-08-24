from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
import uuid
from decimal import Decimal

from wallet.models import Wallet, WalletTransaction, Payout
from users.models import BankingDetails
from users.utils.razorpay_x import initiate_payout


@login_required
def wallet_transactions_view(request):
    user = request.user

    # Always get wallet
    try:
        wallet = Wallet.objects.get(user=user)
    except Wallet.DoesNotExist:
        return JsonResponse({"error": "Wallet not found."}, status=404)

    transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-timestamp')
    payouts = Payout.objects.filter(user=user).order_by('-created_at')

    if request.method == 'POST':
        try:
            amount = Decimal(str(request.POST.get('amount')))
            if amount <= 0:
                raise ValueError()
        except (TypeError, ValueError):
            return JsonResponse({"error": "Invalid amount"}, status=400)

        # ✅ Prevent duplicate submission: Check if a request_id already exists
        request_id = request.POST.get('request_id')
        if Payout.objects.filter(transaction_id=request_id).exists():
            messages.warning(request, "This withdrawal request was already processed.")
            return redirect('wallet_transactions')

        # ✅ Atomic DB transaction to avoid race conditions
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(user=user)

            if wallet.balance < amount:
                return JsonResponse({"error": "Insufficient wallet balance."}, status=400)

            # ✅ Get user's banking details
            try:
                banking = BankingDetails.objects.get(user=user)
            except BankingDetails.DoesNotExist:
                return JsonResponse({"error": "Banking details not found."}, status=404)

            # ✅ Initiate payout
            payout_response = initiate_payout(banking.razorpay_fund_account_id, float(amount))

            if not payout_response or 'id' not in payout_response:
                return JsonResponse({
                    "error": f"Failed to initiate payout. Response: {payout_response}"
                }, status=400)

            # ✅ Deduct from wallet
            wallet.balance -= amount
            wallet.save()

            # ✅ Record wallet transaction
            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type='debit',
                amount=amount,
                description=f'Payout initiated: ₹{amount}'
            )

            # ✅ Save payout with unique request_id
            Payout.objects.create(
                user=user,
                amount=amount,
                razorpay_payout_id=payout_response['id'],
                status=payout_response.get('status', 'initiated'),
                transaction_id=request_id or str(uuid.uuid4())  # unique ID
            )

        messages.success(request, f'Withdrawal of ₹{amount} initiated successfully.')

        # ✅ Redirect to prevent double submission on refresh
        return redirect('wallet_transactions')

    # GET request
    return render(request, 'wallet/wallet_transactions.html', {
        'wallet': wallet,
        'transactions': transactions,
        'payouts': payouts,
        'request_id': str(uuid.uuid4()),  # unique per form load
    })




# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.http import JsonResponse
# from django.contrib import messages

# from wallet.models import Wallet, WalletTransaction, Payout
# from users.models import BankingDetails
# from users.utils.razorpay_x import initiate_payout

# from decimal import Decimal


# @login_required
# def wallet_transactions_view(request):
#     user = request.user

#     # ✅ Always fetch wallet before checking method
#     try:
#         wallet = Wallet.objects.get(user=user)
#     except Wallet.DoesNotExist:
#         return JsonResponse({"error": "Wallet not found."}, status=404)

#     transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-timestamp')
#     payouts = Payout.objects.filter(user=user).order_by('-created_at')

#     if request.method == 'POST':
#         try:
#             amount = float(request.POST.get('amount'))
#             if amount <= 0:
#                 raise ValueError()
#         except (TypeError, ValueError):
#             return JsonResponse({"error": "Invalid amount"}, status=400)

#         # ✅ Check wallet balance
#         if wallet.balance < Decimal(str(amount)):
#             return JsonResponse({"error": "Insufficient wallet balance."}, status=400)

#         # ✅ Get user's banking details
#         try:
#             banking = BankingDetails.objects.get(user=user)
#         except BankingDetails.DoesNotExist:
#             return JsonResponse({"error": "Banking details not found."}, status=404)

#         # ✅ Initiate payout via Razorpay
#         payout_response = initiate_payout(banking.razorpay_fund_account_id, amount)

#         if not payout_response or 'id' not in payout_response:
#             return JsonResponse({
#                 "error": f"Failed to initiate payout. Response: {payout_response}"
#             }, status=400)

#         # ✅ Deduct amount from wallet
#         wallet.balance -= Decimal(str(amount))
#         wallet.save()

#         # ✅ Create a wallet transaction
#         WalletTransaction.objects.create(
#             wallet=wallet,
#             transaction_type='debit',
#             amount=amount,
#             description=f'Payout initiated: ₹{amount}'
#         )

#         # ✅ Save the payout
#         Payout.objects.create(
#             user=user,
#             amount=amount,
#             razorpay_payout_id=payout_response['id'],
#             status=payout_response.get('status', 'initiated'),
#             transaction_id=payout_response.get('reference_id') or payout_response['id']
#         )

#         messages.success(request, f'Withdrawal of ₹{amount} initiated successfully.')

#         # ✅ Refresh payouts & transactions
#         transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-timestamp')
#         payouts = Payout.objects.filter(user=user).order_by('-created_at')

#     return render(request, 'wallet/wallet_transactions.html', {
#         'wallet': wallet,
#         'transactions': transactions,
#         'payouts': payouts,
#     })


# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from wallet.models import WalletTransaction

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.http import JsonResponse
# from .models import WalletTransaction, Payout

# from django.contrib import messages
# from users.models import BankingDetails
# from users.utils.razorpay_x import initiate_payout


# @login_required
# def wallet_transactions_view(request):
#     user = request.user
#     transactions = WalletTransaction.objects.filter(wallet__user=user).order_by('-timestamp')
#     payouts = Payout.objects.filter(user=user).order_by('-created_at')

#     if request.method == 'POST':
#         try:
#             amount = float(request.POST.get('amount'))
#             if amount <= 0:
#                 raise ValueError()
#         except (TypeError, ValueError):
#             return JsonResponse({"error": "Invalid amount"}, status=400)

#         # ✅ Get user's banking details
#         try:
#             banking = BankingDetails.objects.get(user=user)
#         except BankingDetails.DoesNotExist:
#             return JsonResponse({"error": "Banking details not found."}, status=404)

#         # ✅ Initiate payout
#         payout_response = initiate_payout(banking.razorpay_fund_account_id, amount)

#         if not payout_response or 'id' not in payout_response:
#             return JsonResponse({"error": f"Failed to initiate payout. Response: {payout_response}"}, status=400)

#         # ✅ Save the payout
#         Payout.objects.create(
#             user=user,
#             amount=amount,
#             razorpay_payout_id=payout_response['id'],
#             status=payout_response.get('status', 'initiated'),
#             transaction_id = payout_response.get('reference_id') or payout_response['id']

#         )
#          # ✅ Add success message here
#         messages.success(request, f'Withdrawal of ₹{amount} initiated successfully.')
#         # ✅ Refresh payouts list
#         payouts = Payout.objects.filter(user=user).order_by('-created_at')

#     return render(request, 'wallet/wallet_transactions.html', {
#         'transactions': transactions,
#         'payouts': payouts
#     })
