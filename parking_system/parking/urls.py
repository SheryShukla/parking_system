from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # user
    path('slots/', views.slot_list, name='slot_list'),
    path('slots/<int:slot_id>/book/', views.book_slot, name='book_slot'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('my-bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),

    # manager
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/slots/add/', views.add_slot, name='add_slot'),
    path('manager/slots/<int:slot_id>/edit/', views.edit_slot, name='edit_slot'),
    path('manager/slots/<int:slot_id>/delete/', views.delete_slot, name='delete_slot'),
]