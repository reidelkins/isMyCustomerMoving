from django.core.management.base import BaseCommand
from datetime import datetime


from data.utils import remove_error_flag


class Command(BaseCommand):
    help = "Remove All Error Flags From Over 180 days ago"

    def handle(self, *args, **options):
        daysToRun = [0, 1, 2, 3, 4]
        dt = datetime.now()
        weekday = dt.weekday()
        if weekday in daysToRun:
            remove_error_flag.delay()
