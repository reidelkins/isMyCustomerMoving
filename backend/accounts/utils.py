from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup
from celery import shared_task
from datetime import datetime, timedelta
import json
import requests
import math
import pandas as pd
from scrapfly import ScrapeApiResponse, ScrapeConfig, ScrapflyClient
from typing import List, Optional
from typing_extensions import TypedDict

from .models import Client, Company, ZipCode, HomeListing, CustomUser
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


def makeCompany(companyName, email, phone):
    try:
        comp = {'name': companyName, 'phone': phone, 'email': email}
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
                return ""
            else:
                return {'Error': "Company with that name already exists"}
        else:
            print("Serializer not valid")
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
def saveClientList(reader, company_id):
    reader = pd.read_json(reader)
    
    for _, row in reader.iterrows():
        row = row.to_dict()
        street = (str(row['street'])).title()
        zip = row['zip']
        city = row['city']
        state = row['state']
        name = row['name']      
        saveClient.delay(street, zip, city, state, name, company_id)

@shared_task
def saveClient(street, zip, city, state, name, company_id):
    try:
        company = Company.objects.get(id=company_id)
        street = parseStreets(street)
        try:
            if int(zip) > 500 and int(zip) < 99951:
                zipCode, created = ZipCode.objects.get_or_create(zipCode=zip)
                Client.objects.update_or_create(
                        name= name,
                        address= street,
                        zipCode= zipCode,
                        company= company,
                        city= city,
                        state = state,
                        )
        except:
            try:
                if type(zip) == float:
                    zip = int(zip)
                if type(zip) == str:
                    zip = (zip.split('-'))[0]
                if int(zip) > 500 and int(zip) < 99951:
                    zipCode, created = ZipCode.objects.get_or_create(zipCode=zip)
                    Client.objects.update_or_create(
                            name= name,
                            address= street,
                            zipCode= zipCode,
                            company= company,
                            city= city,
                            state = state,
                            )
            except Exception as e:
                print(e)
    except Exception as e:
            print(e)

@shared_task
def getAllZipcodes(company):
    company_object = Company.objects.get(id=company)
    zipCode_objects = Client.objects.filter(company=company_object).values('zipCode')
    zipCodes = zipCode_objects.distinct()
    zipCodes = ZipCode.objects.filter(zipCode__in=zipCode_objects, lastUpdated__lt=(datetime.today()+timedelta(days=2)).strftime('%Y-%m-%d'))
    zips = list(zipCodes.order_by('zipCode').values('zipCode'))
    # zips = {'zipCodes': 37922}
    for i in range(len(zips) * 3):
    # for i in range(100, 300):
        extra = ""
        if i % 3 == 0:
            status = "For Sale"
            url = "https://www.realtor.com/realestateandhomes-search"
        elif i % 3 == 1:
            status = "For Rent"
            url = "https://www.realtor.com/apartments"
        elif i % 3 == 2:
            status = "Recently Sold (6)"
            url = "https://www.realtor.com/realestateandhomes-search"
            extra = "show-recently-sold/"
        find_data.delay(str(zips[i//3]['zipCode']), company, i, status, url, extra)

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
        first_result = scrapfly.scrape(ScrapeConfig(first_page, country="US", asp=True, proxy_pool="public_datacenter_pool"))

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
        # print(f"total pages: {total_pages}, zip: {zip}, status: {status}")
        with open("nums.txt", "a") as f:
            f.write(f"Pages: {total_pages} and Listings: {total}\n")
        for page in range(2, total_pages+1):
            assert "pg-1" in url  # make sure we don't accidently scrape duplicate pages
            page_url = url.replace("pg-1", f"pg-{page}")
            new_results = scrapfly.scrape(ScrapeConfig(url=page_url, country="US", asp=True))  
            parsed = parse_search(new_results, status)
            if status == "For Rent":
                results = parsed["properties"]
            else:
                results = parsed["results"]
            create_home_listings(results, status) 
        updateStatus(int(zip), company, status)
        print(i)
        if i % 3 == 2:
            print(int(zip))
    except Exception as e:
        print(f"ERROR during getHomesForSale: {e} with zipCode {zip}")
        print(f"URL: {url}")

def updateStatus(zip, company, status):
    if company:
        company_objects = Company.objects.filter(id=company)
    else:
        company_objects = Company.objects.all()

    for company_object in company_objects:
        zipCode_object = ZipCode.objects.get(zipCode=zip)
        listedAddresses = HomeListing.objects.filter(zipCode=zipCode_object, status=status).values('address')
        updatedClients = Client.objects.filter(company=company_object, address__in=listedAddresses).update(status=status)
        # update_serviceTitan_clients(updatedClients, company_object)
    
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

    #     next_email = (datetime.today() + timedelta(days=company.email_frequency)).strftime('%Y-%m-%d')
        emails = list(CustomUser.objects.filter(company=company).values_list('email'))
        subject = 'Did Your Customers Move?'
        
        # message = emailBody(company)
        emailStatuses = ['For Sale', 'For Rent']
        foundCustomers = Client.objects.filter(company=company, status__in=emailStatuses)
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

@shared_task
def auto_update():
    companies = Company.objects.all().values_list('id')
    for company in companies:
        getAllZipcodes(company[0])

@shared_task
def get_serviceTitan_clients(company):
    company = Company.objects.get(id=company)
    tenant = company.tenantID
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = f'grant_type=client_credentials&client_id={company.clientID}&client_secret={company.clientSecret}'
    response = requests.post('https://auth.servicetitan.io/connect/token', headers=headers, data=data)

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

    for client in clients:   
        try:
            zip = client['address']['zip']
            if len(zip) > 5:
                zip = zip[:5]
            name=client['name']
            city=client['address']['city'],
            city= city[0]            
            state=client['address']['state']
            street = parseStreets((str(client['address']['street'])).title())
            saveClient.delay(street, zip, city, state, name, company.id)
        except Exception as e:
            print(f"ERROR: {e} with client {client['name']}")

def update_serviceTitan_clients(clients, company):
    try:
        company = Company.objects.get(id=company)
        tenant = company.tenantID
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = f'grant_type=client_credentials&client_id={company.clientID}&client_secret={company.clientSecret}'
        response = requests.post('https://auth.servicetitan.io/connect/token', headers=headers, data=data)
        headers = {'Authorization': response.json()['access_token'], 'Content-Type': 'application/json', 'ST-App-Key': settings.ST_APP_KEY}
        customerIds = []
        payload={'customerIds': ['240000932'], 'tagTypeIds': ['71']}
        response = requests.delete(f'https://api.servicetitan.io/crm/v2/tenant/{tenant}/tags', headers=headers, json=payload)
    except Exception as e:
        print(f"ERROR: {e}")
