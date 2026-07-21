from django.contrib import admin
from .models import Profile, ParkingSlot, Booking


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)


@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    list_display = ('slot_number', 'location', 'price_per_hour', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('slot_number', 'location')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'slot', 'start_time', 'end_time', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'slot__slot_number')
