from datetime import datetime

from django.core.management.base import BaseCommand

from accounts.models import Company
from data.utils import update_clients_statuses


class Command(BaseCommand):
    help = (
        "Update client statuses for a specific company or for all companies."
    )

    def add_arguments(self, parser):
        parser.add_argument("-c", "--company")

    def handle(self, *args, **options):
        company_name = options["company"]
        if company_name:
            company_id = Company.objects.get(name=company_name).id
            update_clients_statuses.delay(company_id)
        else:
            # Define the days to run this command
            days_to_run = [0, 1, 2, 3, 4]  # Weekdays
            current_day = datetime.now().weekday()
            print("Current day: ", current_day)

            # Check if current day is in the list of days to run
            if current_day in days_to_run:
                print("Updating client statuses...")
                update_clients_statuses.delay()
