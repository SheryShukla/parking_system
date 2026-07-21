from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.core.mail import send_mail
from django.http import HttpResponse
# from rest_framework.authentication import JWTAuthentication
from .models import ParkingSlot, Booking, Profile
from .forms import RegisterForm, ParkingSlotForm, BookingForm


# ---------- helpers ----------
def is_manager(user):
    return user.is_authenticated and (user.is_superuser or
           (hasattr(user, 'profile') and user.profile.is_manager))


# ---------- auth ----------
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account ban gaya! Welcome.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'parking/register.html', {'form': form})


# # ------ EMAIL --------------
def trigger_notification(request):
    
    send_mail(
        subject="Notification: Action Required",
        message="Hello! You have successfully booked your slot",
        from_email="your_email@gmail.com",
        recipient_list=["user@example.com"],
        fail_silently=False,
    )
    
    return HttpResponse("Notification email sent successfully!")

class CustomLoginView(LoginView):
    template_name = 'parking/login.html'


# ---------- dashboard (role based redirect) ----------
@login_required
def dashboard(request):
    if is_manager(request.user):
        return redirect('manager_dashboard')
    return redirect('slot_list')


# ---------- USER VIEWS ----------
@login_required
def slot_list(request):
    slots = ParkingSlot.objects.filter(is_available=True)
    return render(request, 'parking/slot_list.html', {'slots': slots})


@login_required
def book_slot(request, slot_id):
    slot = get_object_or_404(ParkingSlot, id=slot_id)
    if not slot.is_available:
        messages.error(request, 'This slot is already booked.')
        return redirect('slot_list')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                booking = form.save(commit=False)
                booking.user = request.user
                booking.slot = slot
                booking.start_time = timezone.now()
                booking.save()
                slot.is_available = False
                slot.save()
            messages.success(request, f'Slot {slot.slot_number} book ho gaya!')
            return redirect('my_bookings')
    else:
        form = BookingForm()
    return render(request, 'parking/book_slot.html', {'form': form, 'slot': slot})


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'parking/my_bookings.html', {'bookings': bookings})


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status == 'booked':
        with transaction.atomic():
            booking.status = 'cancelled'
            booking.end_time = timezone.now()
            booking.save()
            booking.slot.is_available = True
            booking.slot.save()
        messages.success(request, 'Booking cancel ho gayi.')
    return redirect('my_bookings')


# ---------- MANAGER VIEWS ----------
@login_required
def manager_dashboard(request):
    if not is_manager(request.user):
        messages.error(request, 'Aapke paas manager access nahi hai.')
        return redirect('slot_list')
    slots = ParkingSlot.objects.all()
    bookings = Booking.objects.select_related('user', 'slot').order_by('-created_at')[:50]
    return render(request, 'parking/manager_dashboard.html', {'slots': slots, 'bookings': bookings})


@login_required
def add_slot(request):
    if not is_manager(request.user):
        return redirect('slot_list')
    if request.method == 'POST':
        form = ParkingSlotForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Naya slot add ho gaya.')
            return redirect('manager_dashboard')
    else:
        form = ParkingSlotForm()
    return render(request, 'parking/slot_form.html', {'form': form, 'title': 'Add Slot'})


@login_required
def edit_slot(request, slot_id):
    if not is_manager(request.user):
        return redirect('slot_list')
    slot = get_object_or_404(ParkingSlot, id=slot_id)
    if request.method == 'POST':
        form = ParkingSlotForm(request.POST, instance=slot)
        if form.is_valid():
            form.save()
            messages.success(request, 'Slot update ho gaya.')
            return redirect('manager_dashboard')
    else:
        form = ParkingSlotForm(instance=slot)
    return render(request, 'parking/slot_form.html', {'form': form, 'title': 'Edit Slot'})


@login_required
def delete_slot(request, slot_id):
    if not is_manager(request.user):
        return redirect('slot_list')
    slot = get_object_or_404(ParkingSlot, id=slot_id)
    slot.delete()
    messages.success(request, 'Slot delete ho gaya.')
    return redirect('manager_dashboard')
