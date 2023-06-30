from django.core.management.base import BaseCommand
from data.models import ZipCode, HomeListing


class Command(BaseCommand):
    help = "Download recently sold data for a single zip code to a csv file"

    def add_arguments(self, parser):
        parser.add_argument(
            "-z",
            "--zip",
            type=str,
            help="The zip code for which data is required.",
        )

    def handle(self, *args, **options):
        zip_code = options["zip"]
        if zip_code:
            try:
                zip_code_obj = ZipCode.objects.get(zip_code=zip_code)
            except ZipCode.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"No data found for zip code: {zip_code}"
                    )
                )
                return

            listings = HomeListing.objects.filter(
                zip_code=zip_code_obj, status="House Recently Sold (6)"
            )

            # save listings to a csv
            with open(f"./downloaded_data/{zip_code}.csv", "w") as f:
                f.write(
                    "Address,City,State,Zip Code,Sell Price,Date Listed\n"
                )
                for listing in listings:
                    f.write(
                        f"{listing.address},"
                        f"{listing.city},"
                        f"{listing.state},"
                        f"{listing.zip_code.zip_code},"
                        f"{listing.price},"
                        f"{listing.listed}\n"
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Data for zip code: {zip_code} has been "
                    f"successfully written to the csv file."
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR("Please provide a zip code with -z or --zip")
            )
