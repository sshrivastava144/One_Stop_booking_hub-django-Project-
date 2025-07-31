# sabji_market/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import (
    Shop, Product, Cart, CartItem, Order, ShopReview, 
    ShopCategory, ProductCategory
)

class ShopRegistrationForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'owner_name', 'phone_number', 'email', 'address', 'city', 'pincode', 'shop_image', 'description', 'category']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes and placeholders
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your shop name'
        })
        
        self.fields['owner_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter owner name'
        })
        
        self.fields['phone_number'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '+91 98765 43210'
        })
        
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'shop@example.com'
        })
        
        self.fields['address'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter complete shop address',
            'rows': 3
        })
        
        self.fields['city'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter city name'
        })
        
        self.fields['pincode'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter 6-digit pincode'
        })
        
        self.fields['shop_image'].widget.attrs.update({
            'class': 'form-control'
        })
        
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Describe your shop and specialties...',
            'rows': 4
        })
        
        self.fields['category'].widget.attrs.update({
            'class': 'form-select'
        })
        
        # Set required fields
        self.fields['name'].required = True
        self.fields['owner_name'].required = True
        self.fields['phone_number'].required = True
        self.fields['address'].required = True
        self.fields['city'].required = True
        self.fields['pincode'].required = True

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'image', 'price', 'discount_percentage', 'unit', 'stock_quantity', 'is_organic']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if field_name == 'is_organic':
                field.widget.attrs.update({'class': 'form-check-input'})
            elif field_name == 'description':
                field.widget.attrs.update({'class': 'form-control', 'rows': 3})
            elif field_name in ['category', 'unit']:
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        
        # Add placeholders
        self.fields['name'].widget.attrs['placeholder'] = 'Enter product name'
        self.fields['description'].widget.attrs['placeholder'] = 'Describe your product...'
        self.fields['price'].widget.attrs['placeholder'] = '0.00'
        self.fields['discount_percentage'].widget.attrs['placeholder'] = '0'
        self.fields['stock_quantity'].widget.attrs['placeholder'] = '0'

class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'style': 'width: 80px;'
        })
    )

class CheckoutForm(forms.Form):
    DELIVERY_TYPE_CHOICES = [
        ('pickup', 'Pickup from Shop'),
        ('delivery', 'Home Delivery'),
    ]
    
    customer_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name'
        })
    )
    
    customer_phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+91 98765 43210'
        })
    )
    
    delivery_type = forms.ChoiceField(
        choices=DELIVERY_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    delivery_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter delivery address (required for home delivery)'
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Any special instructions...'
        })
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['customer_name'].initial = user.get_full_name() or user.username
            # You can add more user profile fields here if available

    def clean(self):
        cleaned_data = super().clean()
        delivery_type = cleaned_data.get('delivery_type')
        delivery_address = cleaned_data.get('delivery_address')
        
        if delivery_type == 'delivery' and not delivery_address:
            raise forms.ValidationError('Delivery address is required for home delivery.')
        
        return cleaned_data

class ShopReviewForm(forms.ModelForm):
    class Meta:
        model = ShopReview
        fields = ['rating', 'comment']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['rating'].widget = forms.Select(
            choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)],
            attrs={'class': 'form-select'}
        )
        
        self.fields['comment'].widget.attrs.update({
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Share your experience with this shop...'
        })

class ShopSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search shops...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=ShopCategory.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    delivery_available = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class ProductSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search products...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price',
            'step': '0.01'
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price',
            'step': '0.01'
        })
    )

class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'notes']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['status'].widget.attrs.update({
            'class': 'form-select'
        })
        
        self.fields['notes'].widget.attrs.update({
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add any notes about the order status...'
        })