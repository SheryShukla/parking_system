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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='booked')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.slot.slot_number} ({self.status})"
