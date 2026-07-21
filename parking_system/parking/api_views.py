from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ParkingSlot, Booking
from .serializers import RegisterSerializer, ParkingSlotSerializer, BookingSerializer


class IsManagerOrReadOnly(permissions.BasePermission):
    """Anyone authenticated can read. Only managers/superusers can write."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_superuser or getattr(request.user, 'profile', None) and request.user.profile.is_manager)
        )


class RegisterAPIView(generics.CreateAPIView):
    """POST username/email/password -> creates user (role defaults to 'user' via signal)."""
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class ParkingSlotViewSet(viewsets.ModelViewSet):
    """
    /api/slots/         GET (list), POST (create - manager only)
    /api/slots/<id>/     GET, PUT, PATCH, DELETE (manager only for write)
    """
    queryset = ParkingSlot.objects.all().order_by('slot_number')
    serializer_class = ParkingSlotSerializer
    permission_classes = [IsManagerOrReadOnly]


class BookingViewSet(viewsets.ModelViewSet):
    """
    /api/bookings/         GET (own bookings, or all if manager), POST (book a slot)
    /api/bookings/<id>/    GET, DELETE (cancel - sets status=cancelled instead of deleting)
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'profile') and user.profile.is_manager):
            return Booking.objects.all().order_by('-created_at')
        return Booking.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        slot = serializer.validated_data['slot']
        booking = serializer.save(user=self.request.user)
        slot.is_available = False
        slot.save()

    def destroy(self, request, *args, **kwargs):
        booking = self.get_object()
        if booking.status == 'booked':
            booking.status = 'cancelled'
            booking.save()
            booking.slot.is_available = True
            booking.slot.save()
        return Response({'detail': 'Booking cancelled.'}, status=status.HTTP_200_OK)
