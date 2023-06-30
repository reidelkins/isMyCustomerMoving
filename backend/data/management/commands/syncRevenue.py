from datetime import datetime

from django.core.management.base import BaseCommand

from accounts.models import Company
from data.sync_clients import (
    get_service_titan_invoices,
)  # Renamed to match PEP8

from djstripe import models as djstripe_models


class Command(BaseCommand):
    help = "Retrieve revenue values from Service Titan."

    def add_arguments(self, parser):
        parser.add_argument("-c", "--company")

    def handle(self, *args, **options):
        company = options["company"]
        if company:
            get_service_titan_invoices.delay(company_id=company)
        else:
            # Define the day to run this command
            days_to_run = [0]  # Only on Monday
            current_day = datetime.now().weekday()

            # Check if current day is in the list of days to run
            if current_day in days_to_run:
                free_plan = djstripe_models.Plan.objects.get(
                    id="price_1MhxfPAkLES5P4qQbu8O45xy"
                )
                companies = Company.objects.filter(crm="ServiceTitan").exclude(
                    product=free_plan
                )
                for company in companies:
                    get_service_titan_invoices.delay(company.id)
