from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path(' ', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # user
    path('slots/', views.slot_list, name='slot_list'),
    path('slots/<int:slot_id>/book/', views.book_slot, name='book_slot'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    
    # manager
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    
]
