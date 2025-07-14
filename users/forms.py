from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django import forms
from .models import CustomUser, Profile, ShippingAddress


class CustomUserCreationForm(UserCreationForm):
    """Form for Django admin user creation"""
    unique_id = forms.CharField(max_length=50, required=False, disabled=True, widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = CustomUser
        fields = ("email", "unique_id")


class CustomUserChangeForm(UserChangeForm):
    """Form for Django admin user updates"""
    unique_id = forms.CharField(max_length=50, required=False, disabled=True, widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = CustomUser
        fields = ("email", "unique_id")


class CustomUserRegistrationForm(UserCreationForm):
    """Form for user registration with additional required fields"""
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email',  'password1', 'password2')

    def clean_email(self):
        """Ensure the email is unique"""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class UpdateUserForm(forms.ModelForm):
    """Form to update CustomUser + Profile image"""
    password = None  # Hide password field

    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    unique_id = forms.CharField(max_length=50, required=False, disabled=True, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    
    # From Profile model
    image = forms.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'unique_id']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class UpdateUserPassword(PasswordChangeForm):
    """Form for changing user password with improved placeholders"""
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Current Password'}), 
        label="Current Password"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}), 
        label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm New Password'}), 
        label="Confirm New Password"
    )


class UpdateInfoForm(forms.ModelForm):
    """Form for updating user profile information"""
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone'}))
    address1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Address 1'}))
    address2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Address 2'}))
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'City'}))
    state = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'State'}))
    zipcode = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Zip Code'}))
    country = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Country'}))

    class Meta:
        model = Profile
        fields = ["phone", "address1", "address2", "city", "state", "zipcode", "country"]

class ShippingAddressForm(forms.ModelForm):
    """Form for adding/updating a shipping address"""
    full_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone'}))
    address1 = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Address 1'}))
    address2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Address 2'}))
    city = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'City'}))
    state = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'State'}))
    zipcode = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Zip Code'}))
    country = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Country'}))

    class Meta:
        model = ShippingAddress
        fields = ["full_name", "email", "phone", "address1", "address2", "city", "state", "zipcode", "country"]


from .models import BankingDetail

# users/forms.py

from django import forms
from django import forms
from .models import BankingDetail
from django import forms

class BankingDetailForm(forms.Form):
    account_holder_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Holder Name'})
    )
    bank_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank Name'})
    )
    account_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Number'})
    )
    ifsc_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IFSC Code'})
    )

    def clean_account_number(self):
        account_number = self.cleaned_data.get('account_number')
        if not account_number.isdigit():
            raise forms.ValidationError("Account number should contain only digits.")
        if len(account_number) < 9 or len(account_number) > 18:
            raise forms.ValidationError("Account number must be between 9 and 18 digits long.")
        return account_number


    def clean_ifsc_code(self):
        ifsc = self.cleaned_data.get('ifsc_code')
        if len(ifsc) != 11:
            raise forms.ValidationError("IFSC code must be 11 characters long.")
        return ifsc.upper()
