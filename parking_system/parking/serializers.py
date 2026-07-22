from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers
from .models import ParkingSlot, Booking


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        return user


class ParkingSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSlot
        fields = ['id', 'slot_number', 'location', 'price_per_hour', 'is_available']


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    slot_number = serializers.ReadOnlyField(source='slot.slot_number')
    # Write-only: the client sends how many hours they want, not raw start/end
    # datetimes. start_time/end_time are computed server-side on create().
    duration_hours = serializers.IntegerField(min_value=1, max_value=72, write_only=True)
    time_remaining_seconds = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'slot', 'slot_number', 'start_time', 'end_time',
            'duration_hours', 'time_remaining_seconds', 'status', 'created_at',
        ]
        read_only_fields = ['user', 'start_time', 'end_time', 'status', 'created_at']

    def get_time_remaining_seconds(self, obj):
        remaining = obj.time_remaining
        return int(remaining.total_seconds()) if remaining else 0

    def validate_slot(self, slot):
        if not slot.is_available:
            raise serializers.ValidationError("This slot is not available.")
        return slot

    def create(self, validated_data):
        duration_hours = validated_data.pop('duration_hours')
        start_time = timezone.now()
        validated_data['start_time'] = start_time
        validated_data['end_time'] = start_time + timedelta(hours=duration_hours)
        validated_data['duration_hours'] = duration_hours
        return super().create(validated_data)