from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.forms import AuthenticationForm

from payment import razorpay
from .forms import (
    CustomUserRegistrationForm, UpdateUserForm, UpdateUserPassword, 
    UpdateInfoForm, ShippingAddressForm
)
from .models import CustomUser, Profile, ShippingAddress
import json
from cart.models import Cart, CartItem
from cart.models import Order
from django.contrib.auth.decorators import login_required 
from wallet.models import Wallet, WalletTransaction

# Register User with Referral System# Register User with Referral System
def register_user(request):
    # Check if referral ID is in GET request and store it in session
    if 'ref' in request.GET:
        referral_id = request.GET.get('ref')
        request.session['referral_id'] = referral_id  # Store in session
        print(f"Referral ID received and stored in session: {referral_id}")

    # Retrieve referral ID from session (if available)
    referral_id = request.session.get('referral_id')
    print(f"Referral ID used for registration: {referral_id}")  # Debugging

    parent_sponsor = None
    if referral_id:
        try:
            parent_sponsor = CustomUser.objects.get(unique_id=referral_id)
            print(f"Parent Sponsor Found: {parent_sponsor.email}")  # Debugging
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid referral link.")
            return redirect('register')

    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.parent_sponsor = parent_sponsor  # Assign sponsor
            user.save()
            print(f"User {user.email} saved with Parent Sponsor: {user.parent_sponsor.email if user.parent_sponsor else 'None'}")  # Debugging
            
            # Clear the referral ID from session after use
            request.session.pop('referral_id', None)

            login(request, user)
            messages.success(request, 'Registration successful. Please fill in your shipping info.')
            return redirect('update_info')
        else:
            print(form.errors)  # 👈 Add this
            messages.error(request, 'Unsuccessful registration. Invalid information.')
    else:
        form = CustomUserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


# Login User
def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                # Restore previous cart
                current_user = Profile.objects.get(user=request.user)
                saved_cart = current_user.old_cart
                if saved_cart:
                    cart = Cart(request)
                    for key, value in json.loads(saved_cart).items():
                        cart.db_add(product=key, quantity=value)

                messages.success(request, 'Login successful!')
                return redirect('home')
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})

# Logout User
def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out!')
    return redirect('home')

def update_user(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, request.FILES, instance=user)
        if user_form.is_valid():
            user_form.save()

            # Save profile image if provided
            if 'image' in request.FILES:
                profile.image = request.FILES['image']
                profile.save()

            messages.success(request, 'User details updated.')
            return redirect('home')
    else:
        user_form = UpdateUserForm(instance=user, initial={'image': profile.image})

    return render(request, 'users/update_user.html', {'user_form': user_form})

# Update User Profile Info
def update_info(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        form = UpdateInfoForm(request.POST or None, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile info has been updated.")
            return redirect('home')
        return render(request, 'users/update_info.html', {'form': form})
    messages.error(request, "You must be logged in to update your info.")
    return redirect('login')

# Update User Password
def update_password(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = UpdateUserPassword(request.user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been updated. Log in with your new password.")
                return redirect('login')
            messages.error(request, "Please correct the errors below.")
        else:
            form = UpdateUserPassword(request.user)
        return render(request, 'users/update_password.html', {'form': form})
    messages.error(request, "You must be logged in to update your password.")
    return redirect('home')

# User Profile View
@login_required
def user_profile(request):
    if request.user.is_authenticated:
        # Get user profile
        profile = Profile.objects.get(user=request.user)
        
        # Get or create wallet
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        
        # Fetch wallet transactions if wallet exists
        transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-timestamp') if wallet else []
        
        # Build user data dictionary
        user_data = {
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'unique_id': request.user.unique_id,
            'referral_link': f"{request.scheme}://{request.get_host()}/users/register/?ref={request.user.unique_id}",
            'parent_sponsor': request.user.parent_sponsor.unique_id if request.user.parent_sponsor else "None",
            'profile_image': profile.image.url if profile.image else '/media/default/pic.png',
        }
        
        # Fetch user's orders
        orders = Order.objects.filter(user=request.user).order_by('-date_ordered')
        
        # Render the user profile page with all the data
        return render(request, 'users/user_profile.html', {
            'user_data': user_data,
            'orders': orders,
            'wallet': wallet,
            'transactions': transactions,
        })

    # Redirect unauthenticated users with an error message
    messages.error(request, "You must be logged in to view your profile.")
    return redirect('login')

@login_required
def my_referrals_view(request):
    referred_users = request.user.sponsored_users.all()
    return render(request, 'users/my_referrals.html', {'referred_users': referred_users})


# users/views.py

from .models import BankingDetail
from .forms import BankingDetailForm
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


from .models import BankingDetail
from .forms import BankingDetailForm
from razorpay.errors import BadRequestError

@login_required
def billing_info(request):
    user = request.user

    # Check if banking detail already exists
    try:
        banking_detail = BankingDetail.objects.get(user=user)
        has_detail = True
    except BankingDetail.DoesNotExist:
        banking_detail = None
        has_detail = False

    if request.method == 'POST':
        form = BankingDetailForm(request.POST)
        if form.is_valid():
            account_holder_name = form.cleaned_data['account_holder_name']
            bank_name = form.cleaned_data['bank_name']
            account_number = form.cleaned_data['account_number']
            ifsc_code = form.cleaned_data['ifsc_code']

            
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            try:
                # Try to create a customer
                customer = client.customer.create({
                    "name": account_holder_name,
                    "email": user.email,
                    "contact": "9999999999",
                    "fail_existing": 0
                })

                customer_id = customer["id"]

                last4 = account_number[-4:] if len(account_number) >= 4 else account_number

                if has_detail:
                    banking_detail.razorpay_contact_id = customer_id
                    banking_detail.bank_name = bank_name
                    banking_detail.account_last4 = last4
                    banking_detail.verified = True
                    banking_detail.save()
                else:
                    BankingDetail.objects.create(
                        user=user,
                        razorpay_contact_id=customer_id,
                        razorpay_fund_account_id="N/A",  # Placeholder since fund_account is not used here
                        bank_name=bank_name,
                        account_last4=last4,
                        verified=True,
                    )

                messages.success(request, "Billing information saved successfully.")
                return redirect('billing_info')

            except BadRequestError as e:
                messages.error(request, f"Razorpay Error: {str(e)}")
                return redirect('billing_info')

        else:
            messages.error(request, "Please correct the errors below.")
    else:
        initial_data = {
            'account_holder_name': '',
            'bank_name': banking_detail.bank_name if banking_detail else '',
        }
        form = BankingDetailForm(initial=initial_data)

    context = {
        'form': form,
        'banking_detail': banking_detail,
    }
    return render(request, 'users/billing_info.html', context)

