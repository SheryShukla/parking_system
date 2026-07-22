from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings

from .models import ParkingSlot, Booking, Profile
from .forms import RegisterForm, ParkingSlotForm, BookingForm


# ---------- helpers ----------
def is_manager(user):
    return user.is_authenticated and (user.is_superuser or
           (hasattr(user, 'profile') and user.profile.is_manager))


def release_expired_bookings(user=None):
    """Frees any slot whose time window has passed. Called opportunistically
    before we read booking/slot data, so users never see a slot marked
    booked after its time is up (a proper deployment would instead run this
    periodically via a management command / cron / Celery beat)."""
    qs = Booking.objects.filter(status='booked', end_time__lte=timezone.now())
    if user is not None:
        qs = qs.filter(user=user)
    for booking in qs.select_related('slot'):
        booking.release_if_expired()


def send_booking_email(booking, subject, message):
    """Best-effort email notification. Never blocks the booking flow if it fails."""
    if not booking.user.email:
        return
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            fail_silently=True,
        )
    except Exception:
        # Email should never be the reason a booking fails.
        pass


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


class CustomLoginView(LoginView):
    template_name = 'parking/login.html'


# ---------- dashboard  ----------
@login_required
def dashboard(request):
    if is_manager(request.user):
        return redirect('manager_dashboard')
    return redirect('slot_list')


# ---------- USER VIEWS ----------
@login_required
def slot_list(request):
    release_expired_bookings()
    slots = ParkingSlot.objects.filter(is_available=True)
    return render(request, 'parking/slot_list.html', {'slots': slots})


@login_required
def book_slot(request, slot_id):
    release_expired_bookings()
    slot = get_object_or_404(ParkingSlot, id=slot_id)
    if not slot.is_available:
        messages.error(request, 'This slot is already booked.')
        return redirect('slot_list')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            duration_hours = int(form.cleaned_data['duration_hours'])
            start_time = timezone.now()
            end_time = start_time + timedelta(hours=duration_hours)

            with transaction.atomic():
                # Lock the slot row so two people can't book it in the same instant.
                slot = ParkingSlot.objects.select_for_update().get(id=slot.id)
                if not slot.is_available:
                    messages.error(request, 'This slot was just booked by someone else.')
                    return redirect('slot_list')

                booking = Booking.objects.create(
                    user=request.user,
                    slot=slot,
                    start_time=start_time,
                    end_time=end_time,
                    duration_hours=duration_hours,
                )
                slot.is_available = False
                slot.save()

            send_booking_email(
                booking,
                subject='Parking slot booked',
                message=(
                    f'Slot {slot.slot_number} is booked for {duration_hours} hour(s), '
                    f'from {start_time.strftime("%Y-%m-%d %H:%M")} '
                    f'to {end_time.strftime("%Y-%m-%d %H:%M")}.'
                ),
            )
            messages.success(request, f'Slot {slot.slot_number} book ho gaya for {duration_hours}h!')
            return redirect('my_bookings')
    else:
        form = BookingForm()
    return render(request, 'parking/book_slot.html', {'form': form, 'slot': slot})


@login_required
def my_bookings(request):
    release_expired_bookings(user=request.user)
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
        send_booking_email(
            booking,
            subject='Parking booking cancelled',
            message=f'Your booking for slot {booking.slot.slot_number} has been cancelled.',
        )
        messages.success(request, 'Booking cancel ho gayi.')
    return redirect('my_bookings')


# ---------- MANAGER VIEWS ----------
@login_required
def manager_dashboard(request):
    if not is_manager(request.user):
        messages.error(request, 'Aapke paas manager access nahi hai.')
        return redirect('slot_list')
    release_expired_bookings()
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