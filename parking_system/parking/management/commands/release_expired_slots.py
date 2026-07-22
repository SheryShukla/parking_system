from django.core.management.base import BaseCommand
from django.utils import timezone
from parking.models import Booking


class Command(BaseCommand):
    help = (
        "Marks bookings whose time window has passed as 'completed' and "
        "frees their slot. Run this periodically (e.g. every few minutes "
        "via cron or Celery beat) so slots become available again without "
        "needing a user to load a page first:\n\n"
        "  */5 * * * * cd /path/to/project && python manage.py release_expired_slots"
    )

    def handle(self, *args, **options):
        expired = Booking.objects.filter(
            status='booked',
            end_time__lte=timezone.now(),
        ).select_related('slot')

        count = 0
        for booking in expired:
            if booking.release_if_expired():
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Released {count} expired booking(s).'))