from bs4 import BeautifulSoup
from celery import shared_task
from datetime import datetime, timedelta
import json
import requests
import math
import traceback
from scrapfly import ScrapeApiResponse, ScrapeConfig, ScrapflyClient
from typing import List, Optional
from typing_extensions import TypedDict

from .models import Client, Company, ZipCode, HomeListing, CustomUser, ClientUpdate, Task, ScrapeResponse
from .serializers import CompanySerializer

from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.core.management import call_command
from django.template.loader import get_template
import gc


scrapflies = []
for i in range(1, 21):
    scrapfly = ScrapflyClient( key=settings.SCRAPFLY_KEY, max_concurrency=1)
    scrapflies.append(scrapfly)

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

def formatZip(zip):
    try:
        if type(zip) == float:
            zip = int(zip)
        if type(zip) == str:
            zip = zip.replace(' ', '')
            zip = (zip.split('-'))[0]
        if int(zip) > 500 and int(zip) < 99951:
            if len(zip) == 4:
                zip = '0' + str(zip)
            elif len(zip) == 3:
                zip = '00' + str(zip)
            elif len(zip) != 5:
                return False
        return zip
    except:
        return False

@shared_task
def saveClientList(clients, company_id):
    #create
    clientsToAdd = []
    company = Company.objects.get(id=company_id)        
    badStreets = ['none', 'null', 'na', 'n/a', 'tbd', '.']
    for i in range(len(clients)):
        #service titan
        try:
            if 'active' in clients[i]:
                if clients[i]['active']:                    
                    street = parseStreets((str(clients[i]['address']['street'])).title())
                    if street.lower() in badStreets or 'tbd' in street.lower():
                        continue
                    zip = formatZip(clients[i]['address']['zip'])
                    if int(zip) < 500 or int(zip) > 99951:
                        continue
                    zipCode, zipCreated = ZipCode.objects.get_or_create(zipCode=str(zip))                     
                    city=clients[i]['address']['city'],
                    city= city[0]            
                    state=clients[i]['address']['state']
                    name=clients[i]['name']
                    if clients[i]['address']['zip'] == None or not street or not zip or not city or not state or not name or zip == 0:
                        continue
                    clientsToAdd.append(Client(address=street, zipCode=zipCode, city=city, state=state, name=name, company=company, servTitanID=clients[i]['customerId']))                   
            #file upload
            else:                
                street = parseStreets((str(clients[i]['address'])).title())
                if street.lower() in badStreets:
                        continue
                zip = formatZip(clients[i]['zip code'])
                zipCode, zipCreated = ZipCode.objects.get_or_create(zipCode=str(zip))
                city = clients[i]['city']
                state = clients[i]['state']
                name = clients[i]['name']
                if 'phone number' in clients[i]:
                    phoneNumber = clients[i]['phone number']
                else:
                    phoneNumber = ""
                if clients[i]['zip code'] == None or not street or not zip or not city or not state or not name or zip == 0:
                        continue
                clientsToAdd.append(Client(address=street, zipCode=zipCode, city=city, state=state, name=name, company=company, phoneNumber=phoneNumber))
        except Exception as e:
            print("create error")
            print(e)
    Client.objects.bulk_create(clientsToAdd, ignore_conflicts=True)
    try:
        del clientsToAdd
    except:
        pass
    try:
        del clients
    except:
        pass
    try:
        del company
    except:
        pass
    try:
        del company_id
    except:
        pass
    try:
        del badStreets
    except:
        pass


@shared_task
def updateClientList(numbers):
    phoneNumbers = {}
    for number in numbers:
        try:
            phoneNumbers[number['customerId']] = number['phoneSettings']['phoneNumber']
        except:
            continue
    clients = Client.objects.filter(servTitanID__in=list(phoneNumbers.keys()))
    for client in clients:
        client.phoneNumber = phoneNumbers[client.servTitanID]
        client.save()
    try:
        del phoneNumbers
    except:
        pass
    try:
        del clients
    except:
        pass
    try:
        del numbers   
    except:
        pass 


@shared_task
def getAllZipcodes(company):
    company_object = Company.objects.get(id=company)
    zipCode_objects = Client.objects.filter(company=company_object).values('zipCode')
    zipCodes = zipCode_objects.distinct()
    zipCodes = ZipCode.objects.filter(zipCode__in=zipCode_objects, lastUpdated__lt=(datetime.today()).strftime('%Y-%m-%d'))
    zips = list(zipCodes.order_by('zipCode').values('zipCode'))
    zipCodes.update(lastUpdated=datetime.today().strftime('%Y-%m-%d'))
    # zips = [{'zipCode': '37922'}, {'zipCode': '37830'}, {'zipCode': '37934'}, {'zipCode': '37932'}, {'zipCode': '37918'}]
    for i in range(len(zips) * 2):
    # for i in range(len(zips)):
        extra = ""
        if i % 2 == 0:
            status = "House For Sale"
            url = "https://www.realtor.com/realestateandhomes-search"
        elif i % 2 == 1:
            status = "House Recently Sold (6)"
            url = "https://www.realtor.com/realestateandhomes-search"
            extra = "show-recently-sold/"
        # elif i % 3 == 2:
        #     status = "For Rent"
        #     url = "https://www.realtor.com/apartments"
        find_data.delay(str(zips[i//2]['zipCode']), i, status, url, extra)
    del zipCodes
    del zipCode_objects
    del zips
    del company_object

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

def create_home_listings(results, status, resp=None):
    two_years_ago = datetime.now() - timedelta(days=365*2)
    for listing in results:
        zip_object, created = ZipCode.objects.get_or_create(zipCode = listing['location']['address']['postal_code'])
        try:
            if status == "House Recently Sold (6)":
                listType = listing["last_update_date"]
                if listType != None:
                    try:
                        dateCompare = datetime.strptime(listType, "%Y-%m-%dT%H:%M:%SZ")
                    except:
                        dateCompare = datetime.strptime(listType, "%Y-%m-%d")
                    if dateCompare < two_years_ago:
                        continue
                else:
                    listType = listing["description"]["sold_date"]
                    if listType != None:
                        try:
                            dateCompare = datetime.strptime(listType, "%Y-%m-%dT%H:%M:%SZ")
                        except:
                            dateCompare = datetime.strptime(listType, "%Y-%m-%d")
                        if dateCompare < two_years_ago:
                            continue

            else:
                listType = listing["list_date"]
            if listType == None:
                listType = "2022-01-01"
            #if the found date is after 2022, it is valid
            if resp: 
                HomeListing.objects.get_or_create(
                            zipCode= zip_object,
                            address= parseStreets((listing['location']['address']['line']).title()),
                            status= status,
                            listed= listType[:10],
                            ScrapeResponse= ScrapeResponse.objects.get(id=resp),
                            )
            else:
                HomeListing.objects.get_or_create(
                            zipCode= zip_object,
                            address= parseStreets((listing['location']['address']['line']).title()),
                            status= status,
                            listed= listType[:10],
                            )

        except Exception as e: 
            print(f"ERROR for Single Listing: {e} with zipCode {zip_object}")
            print((listing['location']['address']['line']).title())
    try:
        del results
    except:
        pass
    try:
        del zip_object
    except:
        pass
    try:
        del created
    except:
        pass
    try:
        del listType
    except:
        pass

            
@shared_task
def find_data(zip, i, status, url, extra):
    scrapfly = scrapflies[i % 20]    
    try:
        first_page = f"{url}/{zip}/{extra}"
        first_result = scrapfly.scrape(ScrapeConfig(first_page, country="US", asp=False, proxy_pool="public_datacenter_pool"))        
        if first_result.status_code >= 400:
            scrapfly = scrapflies[i+5 % 20]
            first_result = scrapfly.scrape(ScrapeConfig(first_page, country="US", asp=False, proxy_pool="public_datacenter_pool"))
        content = first_result.scrape_result['content']
        soup = BeautifulSoup(content, features='html.parser')
        # resp = ScrapeResponse.objects.create(response=str(content), zip=zip, status=status, url=first_page)
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
        # create_home_listings(results, status, resp.id)
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
            if first_result.status_code >= 400:
                scrapfly = scrapflies[i+5 % 20]
                new_results = scrapfly.scrape(ScrapeConfig(url=page_url, country="US", asp=False, proxy_pool="public_datacenter_pool"))
            content = new_results.scrape_result['content']
            # resp = ScrapeResponse.objects.create(response=str(content), zip=zip, status=status, url=page_url)
            parsed = parse_search(new_results, status)            
            if status == "For Rent":
                results = parsed["properties"]
            else:
                results = parsed["results"]
            # create_home_listings(results, status, resp.id)  
            create_home_listings(results, status)
    except Exception as e:
        print(f"ERROR during getHomesForSale: {e} with zipCode {zip}")
        print(f"URL: {url}")
    try:
        del scrapfly
    except:
        pass
    try:
        del first_page
    except:
        pass
    try:
        del first_result
    except:
        pass
    try:
        del content
    except:
        pass
    try:
        del soup
    except:
        pass
    try:
        del first_data
    except:
        pass
    try:
        del results
    except:
        pass
    try:
        del total
    except:
        pass
    try:
        del count
    except:
        pass
    try:
        del url
    except:
        pass
    try:
        del extra
    except:
        pass
    try:
        del page_url
    except:
        pass
    try:
        del new_results
    except:
        pass
    try:
        del parsed
    except:
        pass


@shared_task
def updateStatus(zip, company, status):
    company = Company.objects.get(id=company)
    try:
        zipCode_object = ZipCode.objects.get(zipCode=zip)
    except Exception as e:
        print(f"ERROR during updateStatus: {e} with zipCode {zip}")
        return
    #addresses from all home listings with the provided zip code and status
    listedAddresses = HomeListing.objects.filter(zipCode=zipCode_object, status=status).values('address')       
    clientsToUpdate = Client.objects.filter(company=company, address__in=listedAddresses, zipCode=zipCode_object)
    previousListed = Client.objects.filter(company=company, zipCode=zipCode_object, status=status)
    newlyListed = clientsToUpdate.difference(previousListed)
    #TODO add logic so if date for one listing is older than date of other, it will not update status
    for toList in newlyListed:
        toList.status = status
        toList.save()
        try:
            listing = HomeListing.objects.filter(zipCode=zipCode_object, address=toList.address, status=status)
            ClientUpdate.objects.get_or_create(client=toList, status=status, listed=listing[0].listed)
        except Exception as e:
            print("Cant find listing to list")
            print("This should not be the case")
    # TODO There is an issue where clients uploaded with wrong zip code and are being marked to be unlisted when they should not be
    # unlisted = previousListed.difference(clientsToUpdate)
    # for toUnlist in unlisted:
    #     toUnlist.status = "Taken Off Market"
    #     toUnlist.save()
    #     ClientUpdate.objects.create(client=toUnlist, status="Taken Off Market")


    clientsToUpdate = list(clientsToUpdate.values_list('servTitanID', flat=True))
    if clientsToUpdate:
        update_serviceTitan_client_tags.delay(clientsToUpdate, company.id, status)
    gc.collect()
    try:
        del company
    except:
        pass
    try:
        del zipCode_object
    except:
        pass
    try:
        del listedAddresses
    except:
        pass
    try:
        del clientsToUpdate
    except:
        pass
    try:
        del previousListed
    except:
        pass
    try:
        del newlyListed
    except:
        pass
    try:
        del unlisted
    except:
        pass
    try:
        del toUnlist
    except:
        pass
    try:
        del toList
    except:
        pass
    try:
        del listing
    except:
        pass
    try:
        del clientsToUpdate
    except:
        pass

@shared_task
def update_clients_statuses(company_id=None):
    if company_id:
        companies = Company.objects.filter(id=company_id)
    else:
        companies = Company.objects.all()
    for company in companies:
        zipCode_objects = Client.objects.filter(company=company).values('zipCode')
        zipCodes = zipCode_objects.distinct()
        zips = list(zipCodes.order_by('zipCode').values('zipCode'))
        for zip in zips:
            zip = zip['zipCode']
            updateStatus.delay(zip, company.id, "House For Sale")
        for zip in zips:
            zip = zip['zipCode']
            updateStatus.delay(zip, company.id, "House Recently Sold (6)")
                
    gc.collect()
    try:
        del companies
    except:
        pass
    try:
        del companies
    except:
        pass
    try:
        del zipCode_objects
    except:
        pass
    try:
        del zipCodes
    except:
        pass
    try:
        del zips
    except:
        pass
    try:
        del zip
    except:
        pass
    try:
        del company
    except:
        pass                  

@shared_task
def sendDailyEmail(company_id=None):
    if company_id:
        companies = Company.objects.filter(id=company_id)
    else:
        companies = Company.objects.all()
    for company in companies:
        emails = list(CustomUser.objects.filter(company=company).values_list('email'))
        subject = 'Did Your Customers Move?'
        
        forSaleCustomers = Client.objects.filter(company=company, status="House For Sale")
        forSaleCustomers = forSaleCustomers.exclude(contacted=True)
        forSaleCustomers = forSaleCustomers.count()
        soldCustomers = Client.objects.filter(company=company, status="House Recently Sold (6)")
        soldCustomers = soldCustomers.exclude(contacted=True)
        soldCustomers = soldCustomers.count()
        message = get_template("dailyEmail.html").render({
            'forSale': forSaleCustomers, 'sold': soldCustomers
        })
        
        if soldCustomers > 0 or forSaleCustomers > 0:
            for email in emails:
                email = email[0]
                msg = EmailMessage(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [email]
                )
                msg.content_subtype ="html"
                msg.send()
    # if not company_id:
    #     HomeListing.objects.all().delete()
    ZipCode.objects.filter(lastUpdated__lt = datetime.today() - timedelta(days=3)).delete()
    try:
        del companies
    except:
        pass
    try:
        del emails
    except:
        pass
    try:
        del subject
    except:
        pass
    try:
        del forSaleCustomers
    except:
        pass
    try:
        del soldCustomers
    except:
        pass
    try:
        del message
    except:
        pass
    try:
        del email
    except:
        pass
    try:
        del msg
    except:
        pass

@shared_task
def auto_update(company_id=None):
    if company_id:
        try:
            company = Company.objects.get(id=company_id)
            getAllZipcodes(company_id)

        except:
            print("Company does not exist")
            return
    else:
        companies = Company.objects.all().values_list('id')
        for company in companies:
            getAllZipcodes(company[0])
    try:
        del company
    except:
        pass
    try:
        del companies
    except:
        pass
    try:
        del company_id
    except:
        pass

@shared_task
def get_serviceTitan_clients(company_id, task_id):
    
    company = Company.objects.get(id=company_id)
    tenant = company.tenantID
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = f'grant_type=client_credentials&client_id={company.clientID}&client_secret={company.clientSecret}'
    response = requests.post('https://auth.servicetitan.io/connect/token', headers=headers, data=data)

    headers = {'Authorization': response.json()['access_token'], 'Content-Type': 'application/json', 'ST-App-Key': settings.ST_APP_KEY}
    clients = []
    moreClients = True
    #get client data
    page = 1
    while(moreClients):
        print(f'getting page {page} of clients')
        response = requests.get(f'https://api.servicetitan.io/crm/v2/tenant/{tenant}/locations?page={page}&pageSize=2500', headers=headers)
        page += 1
        clients = response.json()['data']
        if response.json()['hasMore'] == False:
            moreClients = False
        saveClientList.delay(clients, company_id)
        try:
            del clients
        except:
            pass
        try:
            del response
        except:
            pass
    clients = Client.objects.filter(company=company)
    diff = clients.count() - company.product.customerLimit
    task = Task.objects.get(id=task_id)
    if diff > 0:
        deleteClients = clients[:diff].values_list('id')
        Client.objects.filter(id__in=deleteClients).delete()
        task.deletedClients = diff
    task.completed = True
    task.save()

    # clearing out old data    
    try:
        deleteClients
    except:
        pass
    try:
        del diff
    except:
        pass
    gc.collect()
    frm = ""
    moreClients = True
    page = 0
    while(moreClients):
        page += 1
        print(f'getting phone page {page} of clients')
        response = requests.get(f'https://api.servicetitan.io/crm/v2/tenant/{tenant}/export/customers/contacts?from={frm}', headers=headers)
        # for number in response.json()['data']:
        #     numbers.append(number)
        numbers = response.json()['data']
        if response.json()['hasMore'] == True:
            frm = response.json()['continueFrom']
        else:
            moreClients = False        
        updateClientList.delay(numbers)
        try:
            del numbers
        except:
            pass
        try:
            del response
        except:
            pass
    gc.collect()        
    try:
        del frm
    except:
        pass
    try:
        del moreClients
    except:
        pass
    try:
        del headers
    except:
        pass
    try:
        del data
    except:
        pass
    try:
        del company
    except:
        pass
    try:
        del tenant
    except:
        pass    

@shared_task
def update_serviceTitan_client_tags(forSale, company, status):
    try:
        company = Company.objects.get(id=company)
        if forSale and (company.serviceTitanForSaleTagID or company.serviceTitanRecentlySoldTagID):
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            data = f'grant_type=client_credentials&client_id={company.clientID}&client_secret={company.clientSecret}'
            response = requests.post('https://auth.servicetitan.io/connect/token', headers=headers, data=data)
            headers = {'Authorization': response.json()['access_token'], 'Content-Type': 'application/json', 'ST-App-Key': settings.ST_APP_KEY}
            if status == 'House For Sale':
                tagType = [str(company.serviceTitanForSaleTagID)]
            elif status == 'House Recently Sold (6)':
                tagType = [str(company.serviceTitanRecentlySoldTagID)]
                payload={'customerIds': forSale, 'tagTypeIds': [str(company.serviceTitanForSaleTagID)]}
                response = requests.delete(f'https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tags', headers=headers, json=payload)
            payload={'customerIds': forSale, 'tagTypeIds': tagType}
            response = requests.put(f'https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tags', headers=headers, json=payload)
            if response.status_code != 200:
                resp = response.json()
                error = resp['errors'][0]
                error = error.replace('(', "").replace(')', "").replace(',', " ").replace(".", "").split()
                for word in error:
                    if word.isdigit():
                        # Client.objects.filter(servTitanID=word).delete()
                        if word in forSale:
                            forSale.remove(word)
                if status == 'House Recently Sold (6)':
                    payload={'customerIds': forSale, 'tagTypeIds': [str(company.serviceTitanForSaleTagID)]}
                    response = requests.delete(f'https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tags', headers=headers, json=payload)
                payload={'customerIds': forSale, 'tagTypeIds': tagType}
                response = requests.put(f'https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tags', headers=headers, json=payload)
    except Exception as e:
        print("updating service titan clients failed")
        print(f"ERROR: {e}")
        print(traceback.format_exc())
    try:
        del headers
    except:
        pass
    try:
        del data
    except:
        pass
    try:
        del response
    except:
        pass
    try:
        del payload
    except:
        pass
    try:
        del company
    except:
        pass
    try:
        del status
    except:
        pass
    try:
        del tagType
    except:
        pass
    try:
        del forSale
    except:
        pass
    try:
        del resp
    except:
        pass
    try:
        del error
    except:
        pass
    try:
        del word
    except:
        pass

@shared_task
def remove_all_serviceTitan_tags(company):
    try:
        company = Company.objects.get(id=company)
        if company.serviceTitanForSaleTagID or company.serviceTitanRecentlySoldTagID:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            data = f'grant_type=client_credentials&client_id={company.clientID}&client_secret={company.clientSecret}'
            response = requests.post('https://auth.servicetitan.io/connect/token', headers=headers, data=data)
            headers = {'Authorization': response.json()['access_token'], 'Content-Type': 'application/json', 'ST-App-Key': settings.ST_APP_KEY}
            tagTypes = [[str(company.serviceTitanForSaleTagID)], [str(company.serviceTitanRecentlySoldTagID)]]
            for tag in tagTypes:
                # get a list of all the servTitanIDs for the clients with one from this company
                # clients = list(Client.objects.filter(company=company).values_list('servTitanID'))
                clients = list(Client.objects.filter(company=company).exclude(status="No Change").exclude(servTitanID=None).values_list('servTitanID', flat=True))
                payload={'customerIds': clients, 'tagTypeIds': tag}
                response = requests.delete(f'https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tags', headers=headers, json=payload)                
                if response.status_code != 200:
                    resp = response.json()
                    error = resp['title']
                    error = error.replace('(', "").replace(')', "").replace(',', " ").replace(".", "")
                    error = error.split()
                    for word in error:
                        if word.isdigit():
                            word = int(word)
                            # Client.objects.filter(servTitanID=word).delete()
                            if (word) in clients:
                                clients.remove(word)

                    payload={'customerIds': clients, 'tagTypeIds': tag}
                    response = requests.delete(f'https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tags', headers=headers, json=payload)
                    print(response.status_code)
            Client.objects.filter(company=company).update(status="No Change")
                    
                    
                
    except Exception as e:
        print("updating service titan clients failed")
        print(f"ERROR: {e}")
        print(traceback.format_exc())



def update_serviceTitan_tasks(clients, company, status):
    if clients and (company.serviceTitanForSaleTagID or company.serviceTitanRecentlySoldTagID):
        try:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            data = f'grant_type=client_credentials&client_id={company.clientID}&client_secret={company.clientSecret}'
            response = requests.post('https://auth.servicetitan.io/connect/token', headers=headers, data=data)
            headers = {'Authorization': response.json()['access_token'], 'Content-Type': 'application/json', 'ST-App-Key': settings.ST_APP_KEY}
            response = requests.get(f'https://api.servicetitan.io/taskmanagement/v2/tenant/{str(company.tenantID)}/data', headers=headers)
            with open('tasks.json', 'w') as f:
                json.dump(response.json(), f)
            # if response.status_code != 200:
            #     resp = response.json()
            #     error = resp['errors'][''][0]
            #     error = error.replace('(', "").replace(')', "").replace(',', " ").replace(".", "").split()
            #     for word in error:
            #         if word.isdigit():
            #             Client.objects.filter(servTitanID=word).delete()
            #             forSale.remove(word)
            #     payload={'customerIds': forSale, 'taskTypeId': str(company.serviceTitanTaskID)}
            #     response = requests.put(f'https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tasks', headers=headers, json=payload)
        except Exception as e:
            print("updating service titan tasks failed")
            print(f"ERROR: {e}")
            print(traceback.format_exc())
    try:
        del headers
    except:
        pass
    try:
        del data
    except:
        pass
    try:
        del response
    except:
        pass
    try:
        del company
    except:
        pass
    try:
        del status
    except:
        pass


    