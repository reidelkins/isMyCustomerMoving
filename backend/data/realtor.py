from accounts.models import Company
from config import settings
from .models import Client, HomeListing, ZipCode, HomeListingTags, Realtor
from .utils import delVariables, parseStreets

from bs4 import BeautifulSoup
from celery import shared_task
from datetime import datetime, timedelta
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q
from django.db import transaction
import json
import math
from scrapfly import ScrapeApiResponse, ScrapeConfig, ScrapflyClient
from typing import List, Optional
from typing_extensions import TypedDict

zipScrapflies = []
for i in range(1, 21):
    scrapfly = ScrapflyClient( key=settings.SCRAPFLY_KEY, max_concurrency=1)
    zipScrapflies.append(scrapfly)

detailScrapflies = []
for i in range(1, 21):
    scrapfly = ScrapflyClient( key=settings.SCRAPFLY_KEY, max_concurrency=1)
    detailScrapflies.append(scrapfly)

@shared_task
def getAllZipcodes(company, zip=None):
    company_object, zipCode_objects, zipCodes, zips = "", "", "", ""
    try:
        company_object = Company.objects.get(id=company)
        zipCode_objects = Client.objects.filter(company=company_object, active=True).values('zipCode')
        zipCodes = zipCode_objects.distinct()
        zipCodes = ZipCode.objects.filter(zipCode__in=zipCode_objects, lastUpdated__lt=(datetime.today()).strftime('%Y-%m-%d'))
        zips = list(zipCodes.order_by('zipCode').values('zipCode'))
        zipCodes.update(lastUpdated=datetime.today().strftime('%Y-%m-%d'))
         # zips = [{'zipCode': '37919'}]
    except:
        if zip:
            zips = [{'zipCode': str(zip)}]
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
    delVariables([company_object, zipCode_objects, zipCodes, zips, company])

@shared_task
def find_data(zip, i, status, url, extra):
    scrapfly, first_page, first_result, content, soup, first_data, results, total, count, new_results, parsed, page_url, total = "", "", "", "", "", "", "", "", "", "", "", "", ""
    scrapfly = zipScrapflies[i % 20]    
    try:
        first_page = f"{url}/{zip}/{extra}"
        first_result = scrapfly.scrape(ScrapeConfig(first_page, country="US", asp=False, proxy_pool="public_datacenter_pool"))        
        if first_result.status_code >= 400:
            scrapfly = zipScrapflies[i+5 % 20]
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
                scrapfly = zipScrapflies[i+5 % 20]
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
    vars = [scrapfly, first_page, first_result, content, soup, first_data, results, total, count, url, extra, new_results, parsed, page_url, total]
    delVariables(vars)

def create_home_listings(results, status, resp=None):
    zip_object, created, listType, homeListing, currTag = "", "", "", "", ""
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
            if listing['list_price']:
                price = listing['list_price']
            elif listing['description']['sold_price']:
                price = listing['description']['sold_price']
            else:
                price = 0
            if listing['description']['year_built']:
                year_built = listing['description']['year_built']
            else:
                year_built = 0
            homeListing = HomeListing.objects.get_or_create(
                        zipCode= zip_object,
                        address= parseStreets((listing['location']['address']['line']).title()),
                        status= status,
                        listed= listType[:10],
                        price = price,
                        housingType = listing['description']['type'],
                        year_built = year_built,
                        state = listing['location']['address']['state_code'],
                        city = listing['location']['address']['city'],
                        )
            # if resp:
            #     homeListing[0].ScrapeResponse = ScrapeResponse.objects.get(id=resp)
            #     homeListing[0].save()
            if listing["tags"]:
                for tag in listing["tags"]:
                    currTag = HomeListingTags.objects.get_or_create(tag=tag)
                    homeListing[0].tag.add(currTag[0])


        except Exception as e:
            print(f"Listing: {listing['location']['address']}")
            print(e)
    delVariables([zip_object, created, listType, homeListing, currTag, results])


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
        print(f"page {result.context['url']} is not a property listing page: Not Data")
        return
    
    data = dict(json.loads(data))
    try:
        if(searchType == "For Rent"):
            data = data["props"]["pageProps"]
        else:
            data = data["props"]["pageProps"]["searchResults"]["home_search"]
        return data
    except KeyError:
        print(f"page {result.context['url']} is not a property listing page: KeyError")
        return False



@shared_task
def get_realtor_property_records(address, city, state):    
    street = address.split(" ", 1)[1].replace(" ", "-")
    city = city.replace(" ", "-")
    scrapfly = ScrapflyClient( key=settings.SCRAPFLY_KEY, max_concurrency=1)
    allProps = []
    pages, props = get_realtor_property_records_loop(city, state, street, 1, scrapfly)
    print(len(props))
    allProps.extend(props)
    for page in range(2, pages+1):
        pages, props = get_realtor_property_records_loop(city, state, street, page, scrapfly)
        print(len(props))
        allProps.extend(props)
    with transaction.atomic():
        for property in allProps:
            try:
                zip_code = ZipCode.objects.get(zipCode=property['zipCode'])  # assuming you have zip_code as field in ZipCode model

                HomeListing.objects.update_or_create(
                    address=property['streetAddress'],
                    city=property['city'],
                    state=property['state'],
                    zipCode=zip_code,  # Use the ZipCode instance

                    # Provide the new values for 'permalink' field
                    defaults={'permalink': property['permalink']},
                )
            except MultipleObjectsReturned as e:
                HomeListing.objects.filter(
                    address=property['streetAddress'],
                    city=property['city'],
                    state=property['state'],
                    zipCode=zip_code,  # Use the ZipCode instance
                ).update(permalink=property['permalink'])

                print(f"ERROR: Multiple objects returned for {property['streetAddress']}, {property['city']}, {property['state']}, {property['zipCode']}")

def get_realtor_property_records_loop(city, state, street, page, scrapfly):
    url = f"https://www.realtor.com/propertyrecord-search/{city}_{state}/{street}/pg-{page}"
    result = scrapfly.scrape(ScrapeConfig(url, country="US", asp=False, proxy_pool="public_datacenter_pool"))
    data = result.selector.css("script#__NEXT_DATA__::text").get()
    data = dict(json.loads(data))
    
    total = data['props']['pageProps']['geo']['homeValuesListDetails']['total']
    pages = math.ceil(total / 106)
    try:
        data = data['props']['pageProps']['geo']['homeValuesListDetails']['results']
        print("Data", len(data))
        props = []
        for prop in data:
            property = {}
            property['streetAddress'] = prop['location']['address']['line']
            property['city'] = prop['location']['address']['city']
            property['state'] = prop['location']['address']['state_code']
            property['zipCode'] = prop['location']['address']['postal_code']
            property['permalink'] = prop['permalink']
            props.append(property)
        return pages, props
    except Exception as e:
        print(e)
        return 0, []
    
def get_realtor_property_details(listingId, scrapfly):
    listing = HomeListing.objects.get(id=listingId)
    url = f"https://www.realtor.com/realestateandhomes-detail/{listing.permalink}"
    result = scrapfly.scrape(ScrapeConfig(url, country="US", asp=False, proxy_pool="public_datacenter_pool"))
    result = scrapfly.scrape(ScrapeConfig(url, country="US", asp=False, proxy_pool="public_datacenter_pool"))
    data = result.selector.css("script#__NEXT_DATA__::text").get()
    data = dict(json.loads(data))
    data = data['props']['pageProps']['initialReduxState']['propertyDetails']
    try:
        listing.year_built = data['description']['year_built']
        listing.year_renovated = data['description']['year_renovated']
        listing.housingType = data['description']['type']
        listing.bedrooms = data['description']['beds']
        listing.bathrooms = data['description']['baths']
        listing.sqft = data['description']['sqft']
        listing.lot_sqft = data['description']['lot_sqft']
        listing.roofing = data['description']['roofing']
        listing.garage_type = data['description']['garage_type']
        listing.garage = data['description']['garage']
        listing.pool = data['description']['pool']
        listing.fireplace = data['description']['fireplace']
        listing.heating = data['description']['heating']
        listing.cooling = data['description']['cooling']
        listing.exterior = data['description']['exterior']
        if data['description']['text']:
            listing.description = data['description']['text']
        elif data['property_history']:
            listing.description = data['property_history'][0]['listing']['description']['text']
        listing.latitude = data['location']['address']['coordinate']['lat']
        listing.longitude = data['location']['address']['coordinate']['lon']
        for tag in listing["tags"]:
            currTag = HomeListingTags.objects.get_or_create(tag=tag)
            listing.tag.add(currTag[0])
        extras = []
        for extra in data['description']['details']:
            if extra["category"] == "Interior Features" or extra["category"] == "Heating and Cooling" :
                extras.extend(extra["text"])
        
        if data["advertisers"]:
            realtor, updated = Realtor.objects.update_or_create(
                company = data["advertisers"][0]["broker"]["name"],
                email = data["advertisers"][0]["email"],
                url = data["advertisers"][0]["href"],
                name = data["advertisers"][0]["name"],
                phone = data["advertisers"][0]["phones"][0]["number"]
            )
            listing.realtor = realtor
        listing.save()


    except Exception as e:
        print(e)
        print(data)
        print(f"ERROR: {listing.permalink}")
        pass

    
