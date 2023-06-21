from django.core.management.base import BaseCommand
from datetime import datetime
from accounts.models import Company
from data.syncClients import get_serviceTitan_clients
from djstripe import models as djstripe_models


class Command(BaseCommand):
    help = "Get client list from ServiceTitan"

    def add_arguments(self, parser):
        parser.add_argument("-c", "--company")

    def handle(self, *args, **options):
        company = options["company"]
        if company:
            get_serviceTitan_clients.delay(company_id=company, task_id=None)
        else:
            days_to_run = [0, 1, 2, 3, 4]
            current_datetime = datetime.now()
            current_weekday = current_datetime.weekday()
            if current_weekday in days_to_run:
                free_plan = djstripe_models.Plan.objects.get(
                    id="price_1MhxfPAkLES5P4qQbu8O45xy"
                )
                companies = Company.objects.filter(crm="ServiceTitan").exclude(
                    product=free_plan
                )
                for company in companies:
                    get_serviceTitan_clients.delay(
                        company.id, task_id=None, automated=True
                    )
