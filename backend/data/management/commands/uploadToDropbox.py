from django.core.management.base import BaseCommand
from django.http import HttpResponse
from django.db.models import QuerySet
from accounts.models import Company, Enterprise
from config import settings
from data.models import Client


import csv
from datetime import date
import dropbox


class Command(BaseCommand):
    help = "Create a file into the best postcards folder in dropbox."

    def write_to_csv(self, option, clients):
        for client in clients:
            if option == "_new_address":
                row = [
                    client.company.name,
                    client.name,
                    client.new_address,
                    client.new_city,
                    client.new_state,
                    client.new_zip_code.zip_code
                ]
            else:
                if option == "_recently_sold":
                    client_name = "New Home Owner"
                else:
                    client_name = client.name
                row = [
                    client.company.name,
                    client_name,
                    client.address,
                    client.city,
                    client.state,
                    client.zip_code.zip_code
                ]

            self.writer.writerow(row)

    def add_arguments(self, parser):
        parser.add_argument("-c", "--company")
        parser.add_argument("-e", "--enterprise")
        parser.add_argument("-r", "--recently_sold",
                            action="store_true", default=False)
        parser.add_argument(
            "-m", "--moving", action="store_true", default=False)
        parser.add_argument("-n", "--new_address",
                            action="store_true", default=False)

    def handle(self, *args, **options):
        dbx = dropbox.Dropbox(
            settings.DROPBOX_APP_KEY
        )
        company_name = options["company"]
        enterprise_name = options["enterprise"]
        name = False
        if company_name:
            name = company_name
        elif enterprise_name:
            name = enterprise_name
        if name:
            if enterprise_name:
                enterprise = Enterprise.objects.get(name=name)
                companies = Company.objects.filter(enterprise=enterprise)
                clients = Client.objects.filter(company__in=companies)
            if company_name:
                companies = Company.objects.filter(name=company_name)
                clients = Client.objects.filter(company__in=companies)

            header = [
                "company",
                "name",
                "address",
                "city",
                "state",
                "zip_code"
            ]
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="tmp.csv"'
            self.writer = csv.writer(response)
            self.writer.writerow(header)

            status_type = ""
            tmp1, tmp2, tmp3 = QuerySet(), QuerySet(), QuerySet()
            if options["recently_sold"]:
                recently_sold_clients = clients.filter(
                    status="House Recently Sold (6)")
                status_type += "_recently_sold"
                self.write_to_csv(status_type, recently_sold_clients)

            if options["moving"]:
                moving_clients = clients.filter(status="House For Sale")
                status_type += "_for_sale"
                self.write_to_csv(status_type, moving_clients)

            if options["new_address"]:
                tmp3 = clients.exclude(new_address__isnull=True)
                status_type += "_new_address"
                self.write_to_csv(status_type, tmp3)

            today = date.today()
            d1 = today.strftime("%m-%d-%Y")
            dbx.files_upload(response.getvalue(), f"/BestPostcards/{name}_{d1}{status_type}.csv",
                             mode=dropbox.files.WriteMode.overwrite)
