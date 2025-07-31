# cab_booking/forms.py
from django import forms
from .models import CabBooking, CabService, CabType

class CabBookingForm(forms.ModelForm):
    class Meta:
        model = CabBooking
        fields = [
            'cab_service', 
            'cab_type',
            'pickup_location',
            'drop_location', 
            'pickup_time',
            'special_instructions'
        ]
        widgets = {
            'pickup_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'pickup_location': forms.TextInput(attrs={'placeholder': 'Enter pickup location'}),
            'drop_location': forms.TextInput(attrs={'placeholder': 'Enter drop location'}),
            'special_instructions': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any special instructions...'}),
        }

class FareCalculatorForm(forms.Form):
    pickup_location = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Pickup location'}))
    drop_location = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Drop location'}))
    cab_service = forms.ModelChoiceField(queryset=CabService.objects.filter(is_active=True))
    cab_type = forms.ModelChoiceField(queryset=CabType.objects.all())

class BookingSearchForm(forms.Form):
    booking_id = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'Booking ID'}))
    status = forms.ChoiceField(choices=[('', 'All')] + CabBooking.STATUS_CHOICES, required=False)
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

class RatingForm(forms.ModelForm):
    class Meta:
        model = CabBooking
        fields = ['rating', 'feedback']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)]),
            'feedback': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience...'}),
        }