from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):

    ROLE_CHOICES = (
        ('user', 'User'),
        ('manager', 'Manager'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @property
    def is_manager(self):
        return self.role == 'manager' or self.user.is_superuser


class ParkingSlot(models.Model):
    slot_number = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=100, blank=True)
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2, default=20.00)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Slot {self.slot_number} - {'Available' if self.is_available else 'Booked'}"


class Booking(models.Model):
    STATUS_CHOICES = (
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(blank=True, null=True)
    duration_hours = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='booked')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.slot.slot_number} ({self.status})"

    @property
    def is_expired(self):
        """True once the booked time window has passed and it's still marked booked."""
        return (
            self.status == 'booked'
            and self.end_time is not None
            and self.end_time <= timezone.now()
        )

    @property
    def time_remaining(self):
        """timedelta left on an active booking, or None if not applicable."""
        if self.status != 'booked' or self.end_time is None:
            return None
        remaining = self.end_time - timezone.now()
        return remaining if remaining.total_seconds() > 0 else None

    def release_if_expired(self):
        """Frees the slot and marks the booking completed if its time is up.
        Returns True if it released something."""
        if self.is_expired:
            self.status = 'completed'
            self.save(update_fields=['status'])
            self.slot.is_available = True
            self.slot.save(update_fields=['is_available'])
            return True
        return False