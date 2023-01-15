from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup
from celery import shared_task
from datetime import datetime, timedelta
import json
import requests
import math
import traceback
import pandas as pd
from scrapfly import ScrapeApiResponse, ScrapeConfig, ScrapflyClient
from typing import List, Optional
from typing_extensions import TypedDict

from .models import Task, Client, Company, ZipCode, HomeListing, CustomUser, ProgressUpdate, ClientUpdate
from .serializers import CompanySerializer

from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.core.management import call_command
from django.template.loader import get_template


scrapfly1 = ScrapflyClient(
    key=settings.SCRAPFLY_KEY,
    max_concurrency=1  # increase this for faster scraping
)
scrapfly2 = ScrapflyClient(
    key=settings.SCRAPFLY_KEY,
    max_concurrency=1  # increase this for faster scraping
)
scrapfly3 = ScrapflyClient(
    key=settings.SCRAPFLY_KEY,
    max_concurrency=1  # increase this for faster scraping
)
scrapfly4 = ScrapflyClient(
    key=settings.SCRAPFLY_KEY,
    max_concurrency=1  # increase this for faster scraping
)
scrapfly5 = ScrapflyClient(
    key=settings.SCRAPFLY_KEY,
    max_concurrency=1  # increase this for faster scraping
)


def makeCompany(companyName, email, phone, stripeID,):
    try:
        comp = {'name': companyName, 'phone': phone, 'email': email, 'stripeID': stripeID}
        serializer = CompanySerializer(data=comp)
        if serializer.is_valid():
            company = serializer.save()
            if company:
                mail_subject = "Access Token for Is My Customer Moving"
                messagePlain = "Your access token is: " + company.accessToken
                messagePlain = "Thank you for signing up for Is My Customer Moving. Your company name is: " + company.name +  "and your access token is: " + company.accessToken + ". Please use this info at https://app.ismycustomermoving.com/register to create your account."
                message = get_template("registration.html").render({
                    'company': company.name, 'accessToken': company.accessToken
                })
                send_mail(subject=mail_subject, message=messagePlain, from_email=settings.EMAIL_HOST_USER, recipient_list=[email], html_message=message, fail_silently=False)
                return company
            else:
                return {'Error': "Company with that name already exists"}
        else:
            print(serializer.errors)
            return {'Error': 'Serializer not valid'}
    except Exception as e:
        print(e)
        return {'Error': f'{e}'}

def parseStreets(street):
    conversions = {"Alley": "Aly", "Avenue": "Ave", "Boulevard": "Blvd", "Circle": "Cir", "Court": "Crt", "Cove": "Cv", "Canyon": "Cnyn", "Drive": "Dr", "Expressway": "Expy", "Highway": "Hwy", 
        "Lane": "Ln", "Parkway": "Pkwy", "Place": "Pl", "Pike": "Pk", "Point": "Pt", "Road": "Rd", "Square": "Sq", "Street": "St", "Terrace": "Ter", "Trail": "Trl", "South": "S", "North": "N",
        "West": "W", "East": "E", "Northeast": "NE", "Northwest": "NW", "Southeast": "SE", "Southwest":"SW", "Ne": "NE", "Nw": "NW", "Sw":"SW", "Se":"SE" }
    for word in street.split():
        if word in conversions:
            street = street.replace(word, conversions[word])
    return street

@shared_task
def saveClientList(clients, company_id, updater=None):
    if updater:
        updater = ProgressUpdate.objects.get(id=updater)
        updater.tasks = len(clients)
        updater.save()
    
    for i in range(len(clients)):
        try:
            street = (str(clients[i]['address'])).title()
            zip = clients[i]['zip code']
            city = clients[i]['city']
            state = clients[i]['state']
            name = clients[i]['name']
            task = Task.objects.create(updater=updater)
            saveClient.delay(street, zip, city, state, name, company_id, task=task.id)
            # if updater:
            #     x = math.floor((i/len(clients))*100)
            #     if x == 99:
            #         updater.percentDone = 100
            #     else:
            #         updater.percentDone = x
            #     updater.save()
        except Exception as e:
            print(e)
            continue


@shared_task
def saveClient(street, zip, city, state, name, company_id, serviceTitanID=None, task=None):
    try:
        if task:
            task = Task.objects.get(id=task)
        company = Company.objects.get(id=company_id)
        street = parseStreets(street)
        if type(zip) == float:
            zip = int(zip)
        if type(zip) == str:
            zip = (zip.split('-'))[0]
        if int(zip) > 500 and int(zip) < 99951:
            if len(zip) == 4:
                zip = '0' + str(zip)
            elif len(zip) == 3:
                zip = '00' + str(zip)
            elif len(zip) != 5:
                return

        zipCode, zipCreated = ZipCode.objects.get_or_create(zipCode=str(zip))
        client, created = Client.objects.get_or_create(
                name= name,
                address= street,
                zipCode= zipCode,
                company= company,
                city= city,
                state = state,                
                )
        if created and company.product.customerLimit-Client.objects.filter(company=company).count() < 0:
            client.delete()
            if zipCreated:
                zipCode.delete()
            if task:
                task.complete = True
                task.deleted = True
                task.save()
            return
        client.servTitanID = serviceTitanID
        client.save()
        if task:
            task.complete = True
            task.save()
            
    except Exception as e:
        print(e)

@shared_task
def getAllZipcodes(company):
    company_object = Company.objects.get(id=company)
    zipCode_objects = Client.objects.filter(company=company_object).values('zipCode')
    zipCodes = zipCode_objects.distinct()
    zipCodes = ZipCode.objects.filter(zipCode__in=zipCode_objects, lastUpdated__lt=(datetime.today()).strftime('%Y-%m-%d'))
    zips = list(zipCodes.order_by('zipCode').values('zipCode'))
    # zips = [{'zipCode': '37922'}]
    for i in range(len(zips) * 2):
    # for i in range(100, 130):
        extra = ""
        if i % 3 == 0:
            status = "For Sale"
            url = "https://www.realtor.com/realestateandhomes-search"
        elif i % 3 == 1:
            status = "Recently Sold (6)"
            url = "https://www.realtor.com/realestateandhomes-search"
            extra = "show-recently-sold/"
        # elif i % 3 == 2:
        #     status = "For Rent"
        #     url = "https://www.realtor.com/apartments"
        find_data.delay(str(zips[i//2]['zipCode']), company, i, status, url, extra)

    zipCodes.update(lastUpdated=datetime.today().strftime('%Y-%m-%d'))

class PropertyPreviewResult(TypedDict):
    property_id: str
    listing_id: str
    permalink: str
    list_price: int
    price_reduces_amount: Optional[int]
    description: dict
    location: dict
    photos: List[dict]
    list_date: str
    last_update_date: str
    tags: List[str]

class SearchResults(TypedDict):
    count: int
    total: int
    results: List[PropertyPreviewResult]

def parse_search(result: ScrapeApiResponse, searchType: str) -> SearchResults:
    data = result.selector.css("script#__NEXT_DATA__::text").get()
    if not data:
        print(f"page {result.context['url']} is not a property listing page")
        return
    data = dict(json.loads(data))
    try:
        if(searchType == "For Rent"):
            data = data["props"]["pageProps"]
        else:
            data = data["props"]["pageProps"]["searchResults"]["home_search"]
        return data
    except KeyError:
        print(f"page {result.context['url']} is not a property listing page")
        return False

def create_home_listings(results, status):
     for listing in results:
        zip_object, created = ZipCode.objects.get_or_create(zipCode = listing['location']['address']['postal_code'])
        try:
            if status == "Recently Sold (6)":
                listType = listing["description"]["sold_date"]
            else:
                listType = listing["list_date"]
            if listType == None:
                listType = "2022-01-01"
            HomeListing.objects.get_or_create(
                        zipCode= zip_object,
                        address= parseStreets((listing['location']['address']['line']).title()),
                        status= status,
                        listed= listType
                        )
        except Exception as e: 
            print(f"ERROR for Single Listing: {e} with zipCode {zip_object}")
            print((listing['location']['address']['line']).title())
            

@shared_task
def find_data(zip, company, i, status, url, extra):
    if i % 5 == 0:
        scrapfly = scrapfly1
    elif i % 5 == 1:
        scrapfly = scrapfly2
    elif i % 5 == 2:
        scrapfly = scrapfly3
    elif i % 5 == 3:
        scrapfly = scrapfly4
    elif i % 5 == 4:
        scrapfly = scrapfly5
    
    try:
        first_page = f"{url}/{zip}/{extra}"
        first_result = scrapfly.scrape(ScrapeConfig(first_page, country="US", asp=False, proxy_pool="public_datacenter_pool"))

        content = first_result.scrape_result['content']
        soup = BeautifulSoup(content, features='html.parser')
        if "pg-1" not in first_result.context["url"]:
            url = first_result.context["url"] + "/pg-1"
        else:
            url = first_result.context["url"]
        first_data = parse_search(first_result, status)
        if not first_data:
            return
        if status == "For Rent":
            results = first_data["properties"]
            total = int(soup.find('div', {'data-testid': 'total-results'}).text)
            count = len(results)
            url += "/pg-1"
        else:
            results = first_data["results"]
            total = soup.find('span', {'class': 'result-count'}).text
            total = int(total.split(' ')[0])
            count = first_data["count"]
        create_home_listings(results, status)        
        if count == 0 or total == 0:
            return
        if count < 20: #I believe this can be 10
            total_pages = 1
        else:
            total_pages = math.ceil(total / count)
        for page in range(2, total_pages+1):
            assert "pg-1" in url  # make sure we don't accidently scrape duplicate pages
            page_url = url.replace("pg-1", f"pg-{page}")
            new_results = scrapfly.scrape(ScrapeConfig(url=page_url, country="US", asp=False, proxy_pool="public_datacenter_pool"))
            parsed = parse_search(new_results, status)
            if status == "For Rent":
                results = parsed["properties"]
            else:
                results = parsed["results"]
            create_home_listings(results, status) 
        # updateStatus(zip, company, status)
        
    except Exception as e:
        print(f"ERROR during getHomesForSale: {e} with zipCode {zip}")
        print(f"URL: {url}")

def updateStatus(zip, company, status):
    try:
        zipCode_object = ZipCode.objects.get(zipCode=zip)
    except Exception as e:
        print(f"ERROR during updateStatus: {e} with zipCode {zip}")
        return
    #addresses from all home listings with the provided zip code and status
    listedAddresses = HomeListing.objects.filter(zipCode=zipCode_object, status=status).values('address')
    
    clientsToUpdate = Client.objects.filter(company=company, address__in=listedAddresses)
    previousListed = Client.objects.filter(company=company, zipCode=zipCode_object, status=status)
    newlyListed = clientsToUpdate.difference(previousListed)
    unlisted = previousListed.difference(clientsToUpdate)
    for toUnlist in unlisted:
        toUnlist.status = "No Change"
        toUnlist.save()
    for toList in newlyListed:
        toList.status = status
        toList.save()
        listing = HomeListing.objects.get(zipCode=zipCode_object, address=toList.address, status=status)
        ClientUpdate.objects.get_or_create(client=toList, status=status, listed=listing.listed)

    update_serviceTitan_clients(clientsToUpdate, company, status)
    
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
    for company in companies:
        zipCode_objects = Client.objects.filter(company=company).values('zipCode')
        zipCodes = zipCode_objects.distinct()
        zips = list(zipCodes.order_by('zipCode').values('zipCode'))
        for zip in zips:
            zip = zip['zipCode']
            # stay in this order so if was for sale and then sold, it will show as such
            updateStatus(zip, company, "For Sale")
            updateStatus(zip, company, "Recently Sold (6)")

        # company.next_email_date = (datetime.today() + timedelta(days=company.email_frequency)).strftime('%Y-%m-%d')
        # company.save()


        emails = list(CustomUser.objects.filter(company=company).values_list('email'))
        subject = 'Did Your Customers Move?'
        
        # message = emailBody(company)
        emailStatuses = ['For Sale', 'Recently Sold (6)']
        foundCustomers = Client.objects.filter(company=company, status__in=emailStatuses)
        foundCustomers = foundCustomers.exclude(contacted=True)
        foundCustomers = foundCustomers.order_by('status')
        print(f"found {len(foundCustomers)} customers for {company} to email")
        message = get_template("dailyEmail.html").render({
            'clients': foundCustomers, 'customer': company
        })
        
      
        if foundCustomers:
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

@shared_task
def auto_update():
    companies = Company.objects.all().values_list('id')
    for company in companies:
        getAllZipcodes(company[0])

@shared_task
def get_serviceTitan_clients(company, updater=None):
    
    company = Company.objects.get(id=company)
    tenant = company.tenantID
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = f'grant_type=client_credentials&client_id={company.clientID}&client_secret={company.clientSecret}'
    response = requests.post('https://auth.servicetitan.io/connect/token', headers=headers, data=data)

    headers = {'Authorization': response.json()['access_token'], 'Content-Type': 'application/json', 'ST-App-Key': settings.ST_APP_KEY}
    clients = []
    frm = ""
    moreClients = True
    while(moreClients):
        response = requests.get(f'https://api.servicetitan.io/crm/v2/tenant/{tenant}/export/customers?from={frm}', headers=headers)
        for client in response.json()['data']:
            clients.append(client)
        if response.json()['hasMore']:
            frm = response.json()['continueFrom']
        else:
            moreClients = False
    if updater:
        
        count = 0
        for client in clients:
            if client['active']:
                count+=1
        updater = ProgressUpdate.objects.get(id=updater)
        updater.tasks = count
        updater.save()    
    for i in range(len(clients)):
        if clients[i]['active']:
            try:
                zip = clients[i]['address']['zip']
                if len(zip) > 5:
                    zip = zip[:5]
                name=clients[i]['name']
                city=clients[i]['address']['city'],
                city= city[0]            
                state=clients[i]['address']['state']
                street = parseStreets((str(clients[i]['address']['street'])).title())
                task = Task.objects.create(updater=updater)
                saveClient.delay(street, zip, city, state, name, company.id, clients[i]['id'], task=task.id)
            except Exception as e:
                print(f"ERROR: {e} with client {client['name']}")

def update_serviceTitan_clients(clients, company, status):
    if clients and (company.serviceTitanForSaleTagID or company.serviceTitanRecentlySoldTagID):
        try:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            data = f'grant_type=client_credentials&client_id={company.clientID}&client_secret={company.clientSecret}'
            response = requests.post('https://auth.servicetitan.io/connect/token', headers=headers, data=data)
            headers = {'Authorization': response.json()['access_token'], 'Content-Type': 'application/json', 'ST-App-Key': settings.ST_APP_KEY}
            if status == 'For Sale':
                tagType = [str(company.serviceTitanForSaleTagID)]
            elif status == 'Recently Sold (6)':
                tagType = [str(company.serviceTitanRecentlySoldTagID)]
            # forSaleClients = list(Client.objects.filter(status=status, company=company).values_list('servTitanID'))
            forSale = []
            for client in clients:
                if client.servTitanID:
                    forSale.append(str(client.servTitanID))
            if status == 'Recently Sold (6)':
                payload={'customerIds': forSale, 'tagTypeIds': [str(company.serviceTitanForSaleTagID)]}
                response = requests.delete(f'https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tags', headers=headers, json=payload)
            payload={'customerIds': forSale, 'tagTypeIds': tagType}
            response = requests.put(f'https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tags', headers=headers, json=payload)
            if response.status_code != 200:
                resp = response.json()
                error = resp['errors'][''][0]
                error = error.replace('(', "").replace(')', "").replace(',', " ").replace(".", "").split()
                for word in error:
                    if word.isdigit():
                        Client.objects.filter(servTitanID=word).delete()
                        forSale.remove(word)
                if status == 'Recently Sold (6)':
                    payload={'customerIds': forSale, 'tagTypeIds': [str(company.serviceTitanForSaleTagID)]}
                    response = requests.delete(f'https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tags', headers=headers, json=payload)
                payload={'customerIds': forSale, 'tagTypeIds': tagType}
                response = requests.put(f'https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tags', headers=headers, json=payload)
            # else:
            #     recentlySold = []
            #     recentlySoldClients = list(Client.objects.filter(status=status, company=company).values_list('servTitanID'))
            #     for client in recentlySoldClients:
            #         if client[0] != None:
            #             recentlySold.append(str(client[0]))
            #     headers = {
            #         'Content-Type': 'application/x-www-form-urlencoded',
            #     }
            #     payload={'customerIds': recentlySold, 'tagTypeIds': [str(company.serviceTitanRecentlySoldTagID)]}
            #     response = requests.put(f'https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tags', headers=headers, json=payload)
            #     if response.status_code != 200:
            #         resp = response.json()
            #         error = resp['errors'][''][0]
            #         error = error.replace('(', "").replace(')', "").replace(',', " ").replace(".", "").split()
            #         for word in error:
            #             if word.isdigit():
            #                 #TODO: should the client just be deleted?
            #                 Client.objects.filter(servTitanID=word).update(servTitanID=None)
            #                 recentlySold.remove(word)
            #         payload={'customerIds': recentlySold, 'tagTypeIds': [str(company.serviceTitanRecentlySoldTagID)]}
            #         response = requests.put(f'https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tags', headers=headers, json=payload)
        except Exception as e:
            print("updating service titan clients failed")
            print(f"ERROR: {e}")
            print(traceback.format_exc())
