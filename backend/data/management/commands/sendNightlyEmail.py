from datetime import datetime

from django.core.management.base import BaseCommand

from data.utils import send_daily_email  # Renamed to match PEP8 standard


class Command(BaseCommand):
    help = "Send an email to each user with their data."

    def add_arguments(self, parser):
        parser.add_argument("-c", "--company")

    def handle(self, *args, **options):
        company = options["company"]
        if company:
            send_daily_email.delay(company)
        else:
            # Define the days when the email should be sent
            days_to_run = [0, 1, 2, 3, 4]
            current_day = datetime.now().weekday()

            # Check if current day is in the list of days to run
            if current_day in days_to_run:
                send_daily_email.delay()
