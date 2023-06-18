from django.core.management.base import BaseCommand

from accounts.models import Company
from data.models import Client
from data.utils import verify_address


class Command(BaseCommand):
    help = "Verify All Addresses Using USPS API"

    def add_arguments(self, parser):
        parser.add_argument("-c", "--company")

    def handle(self, *args, **options):
        company = options["company"]
        if company:
            comp = Company.objects.get(name=company)
            clients = Client.objects.filter(company=comp)
            print(len(clients))
            count = 0
            for client in clients:
                count += 1
                if count % 100 == 0:
                    print(count)
                verify_address.delay(client.id)
