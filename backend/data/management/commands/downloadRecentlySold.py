from django.core.management.base import BaseCommand
from datetime import datetime

from data.models import ZipCode, HomeListing


class Command(BaseCommand):
    help = 'Download recently sold data for a single zip code to a csv file'

    def add_arguments(self , parser):
        parser.add_argument('-z', '--zip')
    
    def handle(self, *args, **options):
        zip = options['zip']
        if zip:
            zipCode = ZipCode.objects.get(zipCode=zip)
            listings = HomeListing.objects.filter(zipCode=zipCode, status='House Recently Sold (6)')
            # save listings to a csv
            with open(f'./downloadedData/{zip}.csv', 'w') as f:
                f.write('Address,City,State,Zip Code,Sell Price,Date Listed\n')
                for listing in listings:
                    f.write(f'{listing.address},{listing.city},{listing.state},{listing.zipCode.zipCode},{listing.price},{listing.listed}\n')
