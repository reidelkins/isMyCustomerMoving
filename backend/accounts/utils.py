from .models import Client, Company, ZipCode, HomeListing, CustomUser
from time import sleep
import os
import http.client
import json
from celery import shared_task
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail, EmailMessage

from django.template import Context
from django.template.loader import get_template
from django.utils.html import strip_tags

# app = Celery()

def parseStreets(street):
    conversions = {"Alley": "Aly", "Avenue": "Ave", "Boulevard": "Blvd", "Circle": "Cir", "Court": "Crt", "Cove": "Cv", "Canyon": "Cnyn", "Drive": "Dr", "Expressway": "Expy", "Highway": "Hwy", 
        "Lane": "Ln", "Parkway": "Pkwy", "Place": "Pl", "Pike": "Pk", "Point": "Pt", "Road": "Rd", "Square": "Sq", "Street": "St", "Terrace": "Ter", "Trail": "Trl", "South": "S", "North": "N",
        "West": "W", "East": "E", "Northeast": "NE", "Northwest": "NW", "Southeast": "SE", "Southwest":"SW", "Ne": "NE", "Nw": "NW", "Sw":"SW", "Se":"SE" }
    for word in street.split():
        if word in conversions:
            street = street.replace(word, conversions[word])
    return street


@shared_task
def saveClientList(row, company_id):
    try:
        company = Company.objects.get(id=company_id)
        street = (str(row['street'])).title()
        street = parseStreets(street)
        try:
            if int(row['zip']) > 500 and int(row['zip']) < 99951:
            # if int(row['zip']) > 37770 and int(row['zip']) < 37775:
                zipCode, created = ZipCode.objects.get_or_create(zipCode=row["zip"])
                Client.objects.update_or_create(
                        name= row['name'],
                        address= street,
                        zipCode= zipCode,
                        company= company,
                        city= row['city'],
                        state = row['state'],
                        )
        except:
            try:
                if type(row['zip']) == float:
                    row['zip'] = int(row['zip'])
                if type(row['zip']) == str:
                    print(row['zip'])
                    row['zip'] = (row['zip'].split('-'))[0]
                if int(row['zip']) > 500 and int(row['zip']) < 99951:
                # if int(row['zip']) > 37770 and int(row['zip']) < 37775:
                    zipCode, created = ZipCode.objects.get_or_create(zipCode=row["zip"])
                    Client.objects.update_or_create(
                            name= row["name"],
                            address= street,
                            zipCode= zipCode,
                            company= company,
                            city= row['city'],
                            state = row['state'],
                            )
            except Exception as e:
                print(e)
    except Exception as e:
                print(e)


@shared_task
def getAllZipcodes(company):
    company_object = Company.objects.get(id=company)
    zipCode_objects = Client.objects.filter(company=company_object).values('zipCode')
    zipCodes = ZipCode.objects.filter(zipCode__in=zipCode_objects, lastUpdated__lt=datetime.today().strftime('%Y-%m-%d'))
    for zip in list(zipCodes.values('zipCode')):
        print(zip)
        getHomesForSale.delay(zip, company)
        # getHomesForRent.delay(zip, company)
        # getSoldHomes.delay(zip, company)

    # zipCodes.update(lastUpdated=datetime.today().strftime('%Y-%m-%d'))


@shared_task
def getHomesForSale(zip, company=None):       
    offset = 0
    zip = zip['zipCode']
    moreListings = False
    while(moreListings):
        try:
            conn = http.client.HTTPSConnection("us-real-estate.p.rapidapi.com")

            headers = {
                'X-RapidAPI-Key': settings.RAPID_API,
                'X-RapidAPI-Host': "us-real-estate.p.rapidapi.com"
                }

            conn.request("GET", f"/v2/for-sale-by-zipcode?zipcode={zip}&offset={offset}&limit=200&sort:newest", headers=headers)

            res = conn.getresponse()
            data = res.read().decode("utf-8")
            data = json.loads(data)
            total = data['data']['home_search']['total']
            # print(f"The total amount listed for sale at {zip} is {total} and the current offset is {offset}")
            offset += data['data']['home_search']['count']
            # print(f"The new offset is {offset}")
            if offset >= total:
                moreListings = False
            data = data['data']['home_search']['results']

            for listing in data:
                zip_object, created = ZipCode.objects.get_or_create(zipCode = listing['location']['address']['postal_code'])
                try:
                    HomeListing.objects.get_or_create(
                                zipCode= zip_object,
                                address= parseStreets((listing['location']['address']['line']).title()),
                                status= 'For Sale',
                                listed= listing['list_date']
                                )
                except Exception as e:
                    print(f"ERROR during getHomesForSale Single Listing: {e}")
        except Exception as e:
            print(f"ERROR during getHomesForSale: {e}")


        # try:
        #     with open(f"/Users/reidelkins/Work/isMyCustomerMoving/sep15_{count}_sale.json", "w+") as f:
        #         count += 1
        #         json.dump(data, f)
        # except:
        #     pass
    updateStatus(zip, company, 'For Sale')
   
       
@shared_task
def getHomesForRent(zip, company=None):
    offset = 0
    zip = zip['zipCode']
    moreListings = False
    while(moreListings):
        try:
            conn = http.client.HTTPSConnection("us-real-estate.p.rapidapi.com")

            headers = {
                'X-RapidAPI-Key': settings.RAPID_API,
                'X-RapidAPI-Host': "us-real-estate.p.rapidapi.com"
                }

            conn.request("GET", f"/v2/for-rent-by-zipcode?zipcode={zip}&offset={offset}&limit=200&sort=lowest_price", headers=headers)

            res = conn.getresponse()
            data = res.read().decode("utf-8")
            data = json.loads(data)
            
            total = data['data']['home_search']['total']
            
            # print(f"The total amount listed for rent at {zip} is {total} and the current offset is {offset}")
            offset += data['data']['home_search']['count']
            # print(f"The new offset is {offset}")
            if offset >= total:
                moreListings = False
            # with open(f"/Users/reidelkins/Work/isMyCustomerMoving/sep14_{count}_rent.json", "w+") as f:
            #     count += 1
            #     json.dump(data, f)

            data = data['data']['home_search']['results']

            for listing in data:
                zip_object, created  = ZipCode.objects.get_or_create(zipCode = listing['location']['address']['postal_code'])
                try:
                    if listing['list_date'] != None:
                        HomeListing.objects.get_or_create(
                                    zipCode= zip_object,
                                    address= parseStreets((listing['location']['address']['line']).title()),
                                    status= 'For Rent',
                                    listed= listing['list_date']
                                    )
                    else:
                        HomeListing.objects.get_or_create(
                                    zipCode= zip_object,
                                    address= parseStreets((listing['location']['address']['line']).title()),
                                    status= 'For Rent',
                                    )
                except Exception as e:
                    print(f"ERROR during getHomesForRent Single Listing: {e}")
        except Exception as e:
            print(f"Error during getHomesForRent: {e}")
            # try:
            #     with open(f"/Users/reidelkins/Work/isMyCustomerMoving/sep15_{count}_{zip}_rent.json", "w+") as f:
            #         count += 1
            #         json.dump(data, f)
            # except:
            #     pass
    updateStatus(zip, company, 'For Rent')


@shared_task               
def getSoldHomes(zip, company=None):
    offset = 0
    zip = zip['zipCode']
    moreListings = False
    while(moreListings):
        try:
            conn = http.client.HTTPSConnection("us-real-estate.p.rapidapi.com")

            headers = {
                'X-RapidAPI-Key': settings.RAPID_API,
                'X-RapidAPI-Host': "us-real-estate.p.rapidapi.com"
                }

            conn.request("GET", f"/v2/sold-homes-by-zipcode?zipcode={zip}&offset={offset}&limit=200&sort=sold_date&max_sold_days=400", headers=headers)

            res = conn.getresponse()
            data = res.read().decode("utf-8")
            data = json.loads(data)
            

            total = data['data']['home_search']['total']
            # print(f"The total amount that have been sold at {zip} is {total} and the current offset is {offset}")
            offset += data['data']['home_search']['count']
            # print(f"The new offset is {offset}")
            if offset >= total:
                moreListings = False

            data = data['data']['home_search']['results']

            for listing in data:
                zip_object, created  = ZipCode.objects.get_or_create(zipCode = listing['location']['address']['postal_code'])
                sold_date = datetime.strptime(listing['description']['sold_date'], '%Y-%m-%d')
                halfYear = datetime.today() - timedelta(days=180)
                if sold_date > halfYear:
                    status = 'Recently Sold (6)'
                else:
                    status = 'Recently Sold (12)'
                try:
                    HomeListing.objects.get_or_create(
                                zipCode= zip_object,
                                address= parseStreets((listing['location']['address']['line']).title()),
                                status= status,
                                listed= listing['description']['sold_date']
                                )
                except Exception as e:
                    print(f"ERROR during getSoldHomes Single Listing: {e}")
        except Exception as e:
            print(f"Error during getSoldHomes: {e}")
        # try:
        #     with open(f"/Users/reidelkins/Work/isMyCustomerMoving/sep15_{count}_{zip}_sold.json", "w+") as f:
        #         count += 1
        #         json.dump(data, f)
        # except:
        #     pass
    updateStatus(zip, company, 'Recently Sold (6)')
    updateStatus(zip, company, 'Recently Sold (12)')


def updateStatus(zip, company, status):
    if company:
        company_objects = Company.objects.filter(id=company)
    else:
        company_objects = Company.objects.all()

    for company_object in company_objects:
        zipCode_object = ZipCode.objects.get(zipCode=zip)
        listedAddresses = HomeListing.objects.filter(zipCode=zipCode_object, status=status).values('address')
        Client.objects.filter(company=company_object, address__in=listedAddresses).update(status=status)
    
def emailBody(company):
    foundCustomers = Client.objects.filter(company=company).exclude(status='No Change')
    foundCustomers = foundCustomers.exclude(contacted=True)
    foundCustomers = foundCustomers.order_by('status')
    # body = f"{len(foundCustomers)}"
    body = ""
    for customer in foundCustomers:
        body += f"The home belonging to {customer.name} was found to be {customer.status}. No one from your team has contacted them yet, be the first!\n"

    return body

@shared_task
def send_email():
    
    #https://mailtrap.io/blog/django-send-email/
    today = datetime.today().strftime('%Y-%m-%d')
    # companies = Company.objects.filter(next_email_date=today)
    companies = Company.objects.all()
    # print("no errors yet")
    for company in companies:
        # print(f"sending email to {company.name}")

    #     next_email = (datetime.today() + timedelta(days=company.email_frequency)).strftime('%Y-%m-%d')
        emails = list(CustomUser.objects.filter(company=company).values_list('email'))
        subject = 'Did Your Customers Move?'
        
        # message = emailBody(company)
        foundCustomers = Client.objects.filter(company=company).exclude(status='No Change')
        foundCustomers = foundCustomers.exclude(contacted=True)
        foundCustomers = foundCustomers.order_by('status')
        message = get_template("dailyEmail.html").render({
            'clients': foundCustomers, 'customer': company
        })
        
        # if not message:
        #     message = "There were no updates found today for your client list but look back tomorrow for new leads!"
        
        # print(f"the message is {message}")

        for email in emails:
            email = email[0]
            msg = EmailMessage(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email]
                # html_message=message,
            )
            msg.content_subtype ="html"# Main content is now text/html
            msg.send()

                # send_mail(
                #     subject,
                #     strip_tags(message)
                #     settings.EMAIL_HOST_USER,
                #     [email]
                #     html_message=message
                # )

@shared_task
def send_password_reset_email(email):
    #https://mailtrap.io/blog/django-send-email/
    subject = 'Password Reset: Did My Customers Move'
    message = get_template("resetPassword.html").render()
    
    # message = "There were no updates found today for your client list but look back tomorrow for new leads!"

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email]
    )

@shared_task
def auto_update():
    zipCode_objects = Client.objects.all().values('zipCode').distinct()
    zipCodes = ZipCode.objects.filter(zipCode__in=zipCode_objects)
    for zip in list(zipCodes.values('zipCode')):
        getHomesForSale.delay(zip)
        getHomesForRent.delay(zip)
        getSoldHomes.delay(zip)
    zipCodes.update(lastUpdated=datetime.today().strftime('%Y-%m-%d'))

