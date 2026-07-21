from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import RegisterAPIView, ParkingSlotViewSet, BookingViewSet

router = DefaultRouter()
router.register(r'slots', ParkingSlotViewSet, basename='api-slots')
router.register(r'bookings', BookingViewSet, basename='api-bookings')

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='api_register'),
    path('', include(router.urls)),
]
