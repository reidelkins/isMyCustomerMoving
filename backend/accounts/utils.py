from asgiref.sync import sync_to_async
import asyncio
from bs4 import BeautifulSoup
from celery import shared_task
from datetime import datetime, timedelta
import http.client
import json
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


scrapfly = ScrapflyClient(
    key=settings.SCRAPFLY_KEY,
    max_concurrency=2  # increase this for faster scraping
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
        try:
            company = Company.objects.get(id=company_id)
            street = (str(row['street'])).title()
            street = parseStreets(street)
            try:
                if int(row['zip']) > 500 and int(row['zip']) < 99951:
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
    zipCodes = zipCode_objects.distinct()
    zipCodes = ZipCode.objects.filter(zipCode__in=zipCode_objects, lastUpdated__lt=(datetime.today()+timedelta(days=2)).strftime('%Y-%m-%d'))
    for zip in list(zipCodes.order_by('zipCode').values('zipCode')):
        asyncio.run(find_data(str(zip['zipCode']), company, "For Sale", "https://www.realtor.com/realestateandhomes-search"))
        asyncio.run(find_data(str(zip['zipCode']), company, "For Rent", "https://www.realtor.com/apartments"))
        asyncio.run(find_data(str(zip['zipCode']), company, "Recently Sold (6)", "https://www.realtor.com/realestateandhomes-search", "show-recently-sold/"))

        
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
        with open("errors.txt", "a") as f:
            f.write(f"page {result.context['url']} is not a property listing page\n")
        return
    data = dict(json.loads(data))
    try:
        if(searchType == "For Rent"):
            data = data["props"]["pageProps"]
        else:
            data = data["props"]["pageProps"]["searchResults"]["home_search"]
        return data
    except KeyError:
        with open("errors.txt", "a") as f:
            f.write(f"Data but, page {result.context['url']} is not a property listing page\n")
        print(f"page {result.context['url']} is not a property listing page")
        return False

@sync_to_async
def create_home_listings(results, status):
     for listing in results:
        zip_object, created = ZipCode.objects.get_or_create(zipCode = listing['location']['address']['postal_code'])
        try:
            if status == "Recently Sold (6)":
                listType = listing["description"]["sold_date"]
            else:
                listType = listing["list_date"]
            HomeListing.objects.get_or_create(
                        zipCode= zip_object,
                        address= parseStreets((listing['location']['address']['line']).title()),
                        status= status,
                        listed= listType
                        )
        except Exception as e: 
            print(f"ERROR during getHomesForSale Single Listing: {e} with zipCode {zip}")
            print(listing['location'])

@shared_task
async def find_data(zip, company, status, url, extra=""):
    try:
        first_page = f"{url}/{zip}/{extra}"
        first_result = await scrapfly.async_scrape(ScrapeConfig(first_page, country="US", asp=True))
        content = first_result.scrape_result['content']
        soup = BeautifulSoup(content, features='html.parser')
        url = first_result.context["url"] + "/pg-1"
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
        await create_home_listings(results, status)        
        if count == 0 or total == 0:
            return
        if count < 20: #I believe this can be 10
            total_pages = 1
        else:
            total_pages = math.ceil(total / count)
        to_scrape = []
        for page in range(2, total_pages+1):
            assert "pg-1" in url  # make sure we don't accidently scrape duplicate pages
            page_url = url.replace("pg-1", f"pg-{page}")        
            to_scrape.append(ScrapeConfig(url=page_url, country="US", asp=True))
        async for result in scrapfly.concurrent_scrape(to_scrape):
            parsed = parse_search(result, status)
            if parsed:
                if status == "For Rent":
                    await create_home_listings(parsed["properties"], status)
                else:
                    await create_home_listings(parsed["results"], status)
        await updateStatus(int(zip), company, status)
    except Exception as e:
        print(f"ERROR during getHomesForSale: {e} with zipCode {zip}")
        print(f"URL: {url}")
        with open("errors.txt", "a") as f:
            f.write(f"ERROR during getHomesForSale: {e} with zipCode {zip} URL: {url}\n")

@sync_to_async
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
    zipCode_objects = Client.objects.all().values('zipCode').distinct()
    zipCodes = ZipCode.objects.filter(zipCode__in=zipCode_objects)
    for zip in list(zipCodes.values('zipCode')):
        getHomesForSale.delay(zip)
        getHomesForRent.delay(zip)
        # getSoldHomes.delay(zip)
    zipCodes.update(lastUpdated=datetime.today().strftime('%Y-%m-%d'))


# def parse_search_rent(result: ScrapeApiResponse) -> SearchResults:
#     data = result.selector.css("script#__NEXT_DATA__::text").get()
#     with open("data.json", "w") as f:
#         f.write(data)
#     data = dict(json.loads(data))
#     with open("dataw.json", "w") as f:
#         f.write(json.dumps(data, indent=4))
#     if not data:
#         print(f"page {result.context['url']} is not a property listing page")
#         return
#     # data = json.loads(data)
#     try:
#         data = data["props"]["pageProps"]["properties"]
#         return data
#     except KeyError:
#         print(f"page {result.context['url']} is not a property listing page")
#         return False

# def parse_search_sale(result: ScrapeApiResponse) -> SearchResults:
#     data = result.selector.css("script#__NEXT_DATA__::text").get()
#     if not data:
#         print(f"page {result.context['url']} is not a property listing page")
#         return
#     data = json.loads(data)
#     try:
#         data = data["props"]["pageProps"]["searchResults"]["home_search"]
#         return data
#     except KeyError:
#         print(f"page {result.context['url']} is not a property listing page")
#         return False

# @shared_task
# def getHomesForSale(zip, company=None):       
#     offset = 0
#     zip = zip['zipCode']
#     moreListings = True
#     while(moreListings):
#         try:
#             conn = http.client.HTTPSConnection("us-real-estate.p.rapidapi.com")

#             headers = {
#                 'X-RapidAPI-Key': settings.RAPID_API,
#                 'X-RapidAPI-Host': "us-real-estate.p.rapidapi.com"
#                 }

#             conn.request("GET", f"/v2/for-sale-by-zipcode?zipcode={zip}&offset={offset}&limit=200&sort:newest", headers=headers)

#             res = conn.getresponse()
#             data = res.read().decode("utf-8")
#             data = json.loads(data)
#             total = data['data']['home_search']['total']
#             offset += data['data']['home_search']['count']
#             if offset >= total:
#                 moreListings = False
#             data = data['data']['home_search']['results']

#             for listing in data:
#                 zip_object, created = ZipCode.objects.get_or_create(zipCode = listing['location']['address']['postal_code'])
#                 try:
#                     HomeListing.objects.get_or_create(
#                                 zipCode= zip_object,
#                                 address= parseStreets((listing['location']['address']['line']).title()),
#                                 status= 'For Sale',
#                                 listed= listing['list_date']
#                                 )
#                 except Exception as e:
#                     print(f"ERROR during getHomesForSale Single Listing: {e} with zipCode {zip}")
#                     print(listing['location'])
#         except Exception as e:
#             moreListings = False
#             print(f"ERROR during getHomesForSale: {e} with zipCode {zip}")
#     updateStatus(zip, company, 'For Sale')
   
       
# @shared_task
# def getHomesForRent(zip, company=None):
#     offset = 0
#     zip = zip['zipCode']
#     moreListings = True
#     while(moreListings):
#         try:
#             conn = http.client.HTTPSConnection("us-real-estate.p.rapidapi.com")

#             headers = {
#                 'X-RapidAPI-Key': settings.RAPID_API,
#                 'X-RapidAPI-Host': "us-real-estate.p.rapidapi.com"
#                 }

#             conn.request("GET", f"/v2/for-rent-by-zipcode?zipcode={zip}&offset={offset}&limit=200&sort=lowest_price", headers=headers)

#             res = conn.getresponse()
#             data = res.read().decode("utf-8")
#             data = json.loads(data)
            
#             total = data['data']['home_search']['total']
            
#             offset += data['data']['home_search']['count']
#             if offset >= total:
#                 moreListings = False
#             data = data['data']['home_search']['results']

#             for listing in data:
#                 zip_object, created  = ZipCode.objects.get_or_create(zipCode = listing['location']['address']['postal_code'])

#                 try:
#                     if listing['list_date'] != None:
#                         HomeListing.objects.get_or_create(
#                                     zipCode= zip_object,
#                                     address= parseStreets((listing['location']['address']['line']).title()),
#                                     status= 'For Rent',
#                                     listed= listing['list_date']
#                                     )
#                     else:
#                         HomeListing.objects.get_or_create(
#                                     zipCode= zip_object,
#                                     address= parseStreets((listing['location']['address']['line']).title()),
#                                     status= 'For Rent',
#                                     )
#                 except Exception as e:
#                     print(f"ERROR during getHomesForRent Single Listing: {e} with zipCode {zip}")
#                     print(listing['location'])
#         except Exception as e:
#             moreListings = False
#             print(f"Error during getHomesForRent: {e} with zipCode {zip}")
#     updateStatus(zip, company, 'For Rent')


# @shared_task               
# def getSoldHomes(zip, company=None):
#     offset = 0
#     zip = zip['zipCode']
#     moreListings = True
#     while(moreListings):
#         try:
#             conn = http.client.HTTPSConnection("us-real-estate.p.rapidapi.com")

#             headers = {
#                 'X-RapidAPI-Key': settings.RAPID_API,
#                 'X-RapidAPI-Host': "us-real-estate.p.rapidapi.com"
#                 }

#             conn.request("GET", f"/v2/sold-homes-by-zipcode?zipcode={zip}&offset={offset}&limit=200&sort=sold_date&max_sold_days=400", headers=headers)

#             res = conn.getresponse()
#             data = res.read().decode("utf-8")
#             data = json.loads(data)
            

#             total = data['data']['home_search']['total']
#             offset += data['data']['home_search']['count']
#             if offset >= total:
#                 moreListings = False

#             data = data['data']['home_search']['results']

#             for listing in data:
#                 zip_object, created  = ZipCode.objects.get_or_create(zipCode = listing['location']['address']['postal_code'])
#                 sold_date = datetime.strptime(listing['description']['sold_date'], '%Y-%m-%d')
#                 halfYear = datetime.today() - timedelta(days=180)
#                 if sold_date > halfYear:
#                     status = 'Recently Sold (6)'
#                 else:
#                     status = 'Recently Sold (12)'
#                 try:
#                     HomeListing.objects.get_or_create(
#                                 zipCode= zip_object,
#                                 address= parseStreets((listing['location']['address']['line']).title()),
#                                 status= status,
#                                 listed= listing['description']['sold_date']
#                                 )
#                 except Exception as e:
#                     print(listing['location'])
#                     print(f"ERROR during getSoldHomes Single Listing: {e} with zipCode {zip}")
#         except Exception as e:
#             moreListings = False
#             print(f"Error during getSoldHomes: {e} with zipCode {zip}")
            
#     updateStatus(zip, company, 'Recently Sold (6)')
#     updateStatus(zip, company, 'Recently Sold (12)')
