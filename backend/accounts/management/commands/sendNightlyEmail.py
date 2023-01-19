from django.core.management.base import BaseCommand
from datetime import datetime

from accounts.utils import send_email

class Command(BaseCommand):
    help = 'Sends the email to each user with their data'
    
    def handle(self, *args, **options):
        daysToRun = [0, 1, 2, 3, 4]
        dt = datetime.now()
        weekday = dt.weekday()
        if weekday in daysToRun:
            send_email.delay()