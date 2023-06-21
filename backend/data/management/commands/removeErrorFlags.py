from django.core.management.base import BaseCommand
from datetime import datetime
from data.utils import remove_error_flag


class Command(BaseCommand):
    help = "Remove all error flags from over 180 days ago"

    def handle(self, *args, **options):
        days_to_run = [
            0,
            1,
            2,
            3,
            4,
        ]  # Defines on which weekdays the command should run
        current_datetime = datetime.now()
        current_weekday = current_datetime.weekday()

        # Checks if the current weekday is in the days_to_run list
        if current_weekday in days_to_run:
            remove_error_flag.delay()
