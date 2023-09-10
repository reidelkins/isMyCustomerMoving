from django.core.management.base import BaseCommand
from datetime import datetime
from accounts.models import Company
from data.utils import auto_update


class Command(BaseCommand):
    help = (
        "Scrape data from realtor.com and update "
        "the database for a single zip code or a company"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "-c",
            "--company",
            type=str,
            help="The company for which data is required.",
        )
        parser.add_argument(
            "-z",
            "--zip",
            type=str,
            help="The zip code for which data is required.",
        )

    def handle(self, *args, **options):
        company = options["company"]
        zip_code = options["zip"]
        company = Company.objects.get(name=company).id
        # Prioritizes company over zip code
        if company:
            auto_update.delay(company_id=company)
        elif zip_code:
            auto_update.delay(zip=zip_code)
        else:
            days_to_run = [
                0,
                1,
                2,
                3,
                6,
            ]  # Defines on which weekdays the command should run
            current_datetime = datetime.now()
            current_weekday = current_datetime.weekday()

            # Check if the current day is in days_to_run list
            if current_weekday in days_to_run:
                auto_update.delay()
