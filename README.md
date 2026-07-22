# Parking Slot Booking System

A Django + DRF app to book parking slots for a limited time, with JWT-based API auth and email notifications.

## Setup

```bash
python -m venv .venv (virtual enivornment)
.\.venv\Scripts\activate        # Windows

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
user - Anuj 
password - anuj@123
user - khushi 
password - shery@123
admin - shery
password - 1234
manager - shery
password - 1234

- Access token: 1 hour
- Refresh token: 7 days, rotates and blacklists old ones automatically

## Project Structure
```
parking/
├── management/commands/release_expired_slots.py   # cron-friendly slot cleanup
├── models.py        # Profile, ParkingSlot, Booking
├── views.py         # website views
├── api_views.py     # REST API (JWT protected)
├── forms.py         # booking duration form
├── serializers.py   # DRF serializers
└── templates/parking/
```
