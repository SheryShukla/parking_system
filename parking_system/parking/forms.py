from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import ParkingSlot, Booking


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ParkingSlotForm(forms.ModelForm):
    class Meta:
        model = ParkingSlot
        fields = ['slot_number', 'location', 'price_per_hour', 'is_available']


# How long a user is allowed to hold a slot for. Extend this list freely.
DURATION_CHOICES = (
    (1, '1 hour'),
    (2, '2 hours'),
    (3, '3 hours'),
    (6, '6 hours'),
    (12, '12 hours'),
    (24, '24 hours'),
)


class BookingForm(forms.Form):
    """the user picks a duration, and the view computes start_time/end_time from it rather than the user picking raw
    datetimes."""
    duration_hours = forms.ChoiceField(
        choices=DURATION_CHOICES,
        label='Book for',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )