from decimal import Decimal
from users.models import CustomUser
from wallet.models import Wallet
from django.db.models import F

def distribute_commission(user, product):
    if not product.special_commission_amount:
        return

    total = Decimal(product.special_commission_amount)
    share = total / Decimal(12)
    company = CustomUser.objects.filter(is_superuser=True).first()

    uplines_paid = 0
    current = user.parent_node

    # 1️⃣ Distribute to up to 10 uplines via parent_node chain
    while current and uplines_paid < 10:
        Wallet.objects.filter(user=current).update(balance=F('balance') + share)
        current = current.parent_node
        uplines_paid += 1

    # 2️⃣ Give 1 share to parent_sponsor (if exists)
    sponsor_paid = False
    if user.parent_sponsor:
        Wallet.objects.filter(user=user.parent_sponsor).update(balance=F('balance') + share)
        sponsor_paid = True

    # 3️⃣ Company gets:
    # - remaining of the 10 upline shares
    # - sponsor share if sponsor missing
    # - fixed 1 share
    remaining_shares = (10 - uplines_paid) + (0 if sponsor_paid else 1) + 1

    if company:
        Wallet.objects.filter(user=company).update(balance=F('balance') + (share * remaining_shares))
