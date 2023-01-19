from django.core.management.base import BaseCommand
from datetime import datetime


from accounts.utils import auto_update


class Command(BaseCommand):
    help = 'Scrape data from realtor.com and update the database'
    
    def handle(self, *args, **options):
        daysToRun = [0, 1, 2, 3, 4]
        dt = datetime.now()
        weekday = dt.weekday()
        if weekday in daysToRun:
            auto_update.delay()