from django.core.management.base import BaseCommand

from accounts.models import Company
from data.models import Client
from data.utils import verify_address


class Command(BaseCommand):
    help = (
        "Verify all addresses for a specific "
        "company or for all companies using USPS API."
    )

    def add_arguments(self, parser):
        parser.add_argument("-c", "--company")

    def handle(self, *args, **options):
        company_name = options["company"]
        if company_name:
            company = Company.objects.get(name=company_name)
            clients = Client.objects.filter(company=company)
            total_clients = len(clients)
            print(f"Total clients: {total_clients}")

            for count, client in enumerate(clients, start=1):
                if count % 100 == 0:
                    print(f"Processed clients: {count}")
                verify_address.delay(client.id)
