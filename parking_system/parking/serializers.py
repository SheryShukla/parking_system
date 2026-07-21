from django.contrib.auth.models import User
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

    class Meta:
        model = Booking
        fields = ['id', 'user', 'slot', 'slot_number', 'start_time', 'end_time', 'status', 'created_at']
        read_only_fields = ['user', 'status', 'created_at']

    def validate_slot(self, slot):
        if not slot.is_available:
            raise serializers.ValidationError("This slot is not available.")
        return slot
