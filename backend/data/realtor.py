from accounts.models import Company
from config import settings
from .models import Client, HomeListing, ZipCode, HomeListingTags, Realtor
from .utils import delVariables, parseStreets

from bs4 import BeautifulSoup
from celery import shared_task
from datetime import datetime, timedelta
from django.core.exceptions import MultipleObjectsReturned

from django.db import transaction
import json
import logging
import math
from scrapfly import ScrapeApiResponse, ScrapeConfig, ScrapflyClient
from typing import List, Optional
from typing_extensions import TypedDict

zipScrapflies = []
for i in range(1, 21):
    scrapfly = ScrapflyClient(key=settings.SCRAPFLY_KEY, max_concurrency=1)
    zipScrapflies.append(scrapfly)

detailScrapflies = []
for i in range(1, 21):
    scrapfly = ScrapflyClient(key=settings.SCRAPFLY_KEY, max_concurrency=1)
    detailScrapflies.append(scrapfly)


@shared_task
def getAllZipcodes(company, zip=None):
    company_object, zipCode_objects, zipCodes, zips = "", "", "", ""
    try:
        company_object = Company.objects.get(id=company)
        zipCode_objects = Client.objects.filter(
            company=company_object, active=True
        ).values("zipCode")
        zipCodes = zipCode_objects.distinct()
        zipCodes = ZipCode.objects.filter(
            zipCode__in=zipCode_objects,
            lastUpdated__lt=(datetime.today()).strftime("%Y-%m-%d"),
        )
        zips = list(zipCodes.order_by("zipCode").values("zipCode"))
        zipCodes.update(lastUpdated=datetime.today().strftime("%Y-%m-%d"))
        # zips = [{'zipCode': '37919'}]
    except Exception as e:
        if zip:
            zips = [{"zipCode": str(zip)}]
        logging.error(e)
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
        find_data.delay(str(zips[i // 2]["zipCode"]), i, status, url, extra)
    delVariables([company_object, zipCode_objects, zipCodes, zips, company])


@shared_task
def find_data(zip, i, status, url, extra):
    (
        scrapfly,
        first_page,
        first_result,
        content,
        soup,
        first_data,
        results,
        total,
        count,
        new_results,
        parsed,
        page_url,
        total,
    ) = ("", "", "", "", "", "", "", "", "", "", "", "", "")
    scrapfly = zipScrapflies[i % 20]
    try:
        first_page = f"{url}/{zip}/{extra}"
        first_result = scrapfly.scrape(
            ScrapeConfig(
                first_page,
                country="US",
                asp=False,
                proxy_pool="public_datacenter_pool",
            )
        )
        if first_result.status_code >= 400:
            scrapfly = zipScrapflies[i + 5 % 20]
            first_result = scrapfly.scrape(
                ScrapeConfig(
                    first_page,
                    country="US",
                    asp=False,
                    proxy_pool="public_datacenter_pool",
                )
            )
        content = first_result.scrape_result["content"]
        soup = BeautifulSoup(content, features="html.parser")
        # resp = ScrapeResponse.objects.create(
        #     response=str(content), zip=zip, status=status, url=first_page
        # )
        if "pg-1" not in first_result.context["url"]:
            url = first_result.context["url"] + "/pg-1"
        else:
            url = first_result.context["url"]
        first_data = parse_search(first_result, status)
        if not first_data:
            return
        if status == "For Rent":
            results = first_data["properties"]
            total = int(soup.find("div", {"data-testid": "total-results"}).text)
            count = len(results)
            url += "/pg-1"
        else:
            results = first_data["results"]
            total = soup.find("span", {"class": "result-count"}).text
            total = int(total.split(" ")[0])
            count = first_data["count"]
        # create_home_listings(results, status, resp.id)
        create_home_listings(results, status)
        if count == 0 or total == 0:
            return
        if count < 20:  # I believe this can be 10
            total_pages = 1
        else:
            total_pages = math.ceil(total / count)
        for page in range(2, total_pages + 1):
            assert (
                "pg-1" in url
            )  # make sure we don't accidently scrape duplicate pages
            page_url = url.replace("pg-1", f"pg-{page}")
            new_results = scrapfly.scrape(
                ScrapeConfig(
                    url=page_url,
                    country="US",
                    asp=False,
                    proxy_pool="public_datacenter_pool",
                )
            )
            if first_result.status_code >= 400:
                scrapfly = zipScrapflies[i + 5 % 20]
                new_results = scrapfly.scrape(
                    ScrapeConfig(
                        url=page_url,
                        country="US",
                        asp=False,
                        proxy_pool="public_datacenter_pool",
                    )
                )
            content = new_results.scrape_result["content"]
            # resp = ScrapeResponse.objects.create(
            #     response=str(content),
            #     zip=zip,
            #     status=status,
            #     url=page_url
            # )
            parsed = parse_search(new_results, status)
            if status == "For Rent":
                results = parsed["properties"]
            else:
                results = parsed["results"]
            # create_home_listings(results, status, resp.id)
            create_home_listings(results, status)
    except Exception as e:
        logging.error(f"ERROR during getHomesForSale: {e} with zipCode {zip}")
        logging.error(f"URL: {url}")
    vars = [
        scrapfly,
        first_page,
        first_result,
        content,
        soup,
        first_data,
        results,
        total,
        count,
        url,
        extra,
        new_results,
        parsed,
        page_url,
        total,
    ]
    delVariables(vars)


def create_home_listings(results, status, resp=None):
    zip_object, created, listType, homeListing, currTag = "", "", "", "", ""
    two_years_ago = datetime.now() - timedelta(days=365 * 2)
    for listing in results:
        zip_object, created = ZipCode.objects.get_or_create(
            zipCode=listing["location"]["address"]["postal_code"]
        )
        try:
            if status == "House Recently Sold (6)":
                listType = listing["last_update_date"]
                if listType is not None:
                    try:
                        dateCompare = datetime.strptime(
                            listType, "%Y-%m-%dT%H:%M:%SZ"
                        )
                    except Exception as e:
                        logging.error(
                            f"ERROR during create_home_listings: {zip_object}"
                        )
                        logging.error(e)
                        dateCompare = datetime.strptime(listType, "%Y-%m-%d")
                    if dateCompare < two_years_ago:
                        continue
                else:
                    listType = listing["description"]["sold_date"]
                    if listType is not None:
                        try:
                            dateCompare = datetime.strptime(
                                listType, "%Y-%m-%dT%H:%M:%SZ"
                            )
                        except Exception as e:
                            logging.error(
                                f"ERROR during create_home_listings: {zip_object}"
                            )
                            logging.error(e)
                            dateCompare = datetime.strptime(
                                listType, "%Y-%m-%d"
                            )
                        if dateCompare < two_years_ago:
                            continue
            else:
                listType = listing["list_date"]
            if listType is None:
                listType = "2022-01-01"

            price = (
                listing["list_price"]
                if listing["list_price"]
                else listing["description"].get("sold_price", 0)
            )
            year_built = listing["description"].get("year_built", 0)

            # Assume the values are in the 'description' dictionary
            beds = listing["description"].get("beds", 0)
            baths = listing["description"].get("baths", 0)
            cooling = listing["description"].get("cooling", "")
            heating = listing["description"].get("heating", "")
            sqft = listing["description"].get("sqft", 0)

            # Check if the HomeListing already exists
            try:
                homeListing = HomeListing.objects.get(
                    zipCode=zip_object,
                    address=parseStreets(
                        (listing["location"]["address"]["line"]).title()
                    ),
                    city=listing["location"]["address"]["city"],
                    state=listing["location"]["address"]["state_code"],
                )
                # Update all the fields if it already exists
                homeListing.status = status
                homeListing.listed = listType[:10]
                homeListing.price = price
                homeListing.housingType = listing["description"]["type"]
                homeListing.year_built = year_built
                if listing["location"]["address"]["coordinate"] is not None:
                    homeListing.latitude = listing["location"]["address"][
                        "coordinate"
                    ].get("lat")
                    homeListing.longitude = listing["location"]["address"][
                        "coordinate"
                    ].get("lon")
                homeListing.permalink = listing["permalink"]
                homeListing.lot_sqft = listing["description"].get("lot_sqft", 0)
                homeListing.bedrooms = beds
                homeListing.bathrooms = baths
                homeListing.cooling = cooling
                homeListing.heating = heating
                homeListing.sqft = sqft
                homeListing.save()

            except HomeListing.DoesNotExist:
                # Create a new HomeListing if it doesn't exist
                if listing["location"]["address"]["coordinate"] is not None:
                    latitude = listing["location"]["address"]["coordinate"].get(
                        "lat"
                    )
                    longitude = listing["location"]["address"][
                        "coordinate"
                    ].get("lon")
                homeListing = HomeListing.objects.create(
                    zipCode=zip_object,
                    address=parseStreets(
                        (listing["location"]["address"]["line"]).title()
                    ),
                    status=status,
                    listed=listType[:10],
                    price=price,
                    housingType=listing["description"]["type"],
                    year_built=year_built,
                    state=listing["location"]["address"]["state_code"],
                    city=listing["location"]["address"]["city"],
                    latitude=latitude,
                    longitude=longitude,
                    permalink=listing["permalink"],
                    lot_sqft=listing["description"].get("lot_sqft", 0),
                    bedrooms=beds,
                    bathrooms=baths,
                    cooling=cooling,
                    heating=heating,
                    sqft=sqft,
                )
            # Uncomment this if you want a Scrapresponse
            # if resp:
            #     homeListing.ScrapeResponse = ScrapeResponse.objects.get(id=resp)
            #     homeListing.save()

            if listing["tags"]:
                for tag in listing["tags"]:
                    currTag, _ = HomeListingTags.objects.get_or_create(tag=tag)
                    homeListing.tag.add(currTag)

            if listing["branding"]:
                for brand in listing["branding"]:
                    realtor, _ = Realtor.objects.get_or_create(
                        name=brand["name"]
                    )
                    homeListing.realtor = realtor
                    homeListing.save()

        except Exception as e:
            logging.error(f"Listing: {listing['location']['address']}")
            logging.error(e)
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
        logging.error(
            f"""page {result.context['url']}
              is not a property listing page: Not Data"""
        )
        return

    data = dict(json.loads(data))
    try:
        if searchType == "For Rent":
            data = data["props"]["pageProps"]
        else:
            data = data["props"]["pageProps"]["searchResults"]["home_search"]
        return data
    except KeyError:
        logging.error(
            f"""page {result.context['url']} is not
              a property listing page: KeyError"""
        )
        return False


@shared_task
def get_realtor_property_records(address, city, state):
    street = address.split(" ", 1)[1].replace(" ", "-")
    city = city.replace(" ", "-")
    scrapfly = ScrapflyClient(key=settings.SCRAPFLY_KEY, max_concurrency=1)
    allProps = []
    pages, props = get_realtor_property_records_loop(
        city, state, street, 1, scrapfly
    )
    allProps.extend(props)
    for page in range(2, pages + 1):
        pages, props = get_realtor_property_records_loop(
            city, state, street, page, scrapfly
        )
        allProps.extend(props)
    with transaction.atomic():
        for property in allProps:
            try:
                zip_code = ZipCode.objects.get(
                    zipCode=property["zipCode"]
                )  # assuming you have zip_code as field in ZipCode model

                HomeListing.objects.update_or_create(
                    address=property["streetAddress"],
                    city=property["city"],
                    state=property["state"],
                    zipCode=zip_code,  # Use the ZipCode instance
                    # Provide the new values for 'permalink' field
                    defaults={"permalink": property["permalink"]},
                )
            except MultipleObjectsReturned as e:
                HomeListing.objects.filter(
                    address=property["streetAddress"],
                    city=property["city"],
                    state=property["state"],
                    zipCode=zip_code,  # Use the ZipCode instance
                ).update(permalink=property["permalink"])

                logging.error(
                    f"""ERROR: Multiple objects returned for
                    {property['streetAddress']}, {property['city']},
                      {property['state']}, {property['zipCode']} {e}"""
                )


def get_realtor_property_records_loop(city, state, street, page, scrapfly):
    url = f"""https://www.realtor.com/propertyrecord-search
    /{city}_{state}/{street}/pg-{page}"""
    result = scrapfly.scrape(
        ScrapeConfig(
            url, country="US", asp=False, proxy_pool="public_datacenter_pool"
        )
    )
    data = result.selector.css("script#__NEXT_DATA__::text").get()
    data = dict(json.loads(data))

    total = data["props"]["pageProps"]["geo"]["homeValuesListDetails"]["total"]
    pages = math.ceil(total / 106)
    try:
        data = data["props"]["pageProps"]["geo"]["homeValuesListDetails"][
            "results"
        ]
        props = []
        for prop in data:
            property = {}
            property["streetAddress"] = prop["location"]["address"]["line"]
            property["city"] = prop["location"]["address"]["city"]
            property["state"] = prop["location"]["address"]["state_code"]
            property["zipCode"] = prop["location"]["address"]["postal_code"]
            property["permalink"] = prop["permalink"]
            props.append(property)
        return pages, props
    except Exception as e:
        logging.error(e)
        return 0, []


def get_realtor_property_details(listingId, scrapfly):
    listing = HomeListing.objects.get(id=listingId)
    url = f"""https://www.realtor.com/
        realestateandhomes-detail/{listing.permalink}"""
    result = scrapfly.scrape(
        ScrapeConfig(
            url, country="US", asp=False, proxy_pool="public_datacenter_pool"
        )
    )
    data = result.selector.css("script#__NEXT_DATA__::text").get()
    data = dict(json.loads(data))
    data = data["props"]["pageProps"]["initialReduxState"]["propertyDetails"]
    try:
        # Check if fields exist before assigning
        description = data.get("description", {})
        if description:
            listing.year_built = description.get("year_built")
            listing.year_renovated = description.get("year_renovated")
            listing.housingType = description.get("type")
            listing.bedrooms = description.get("beds")
            listing.bathrooms = description.get("baths")
            listing.sqft = description.get("sqft")
            listing.lot_sqft = description.get("lot_sqft")
            listing.roofing = description.get("roofing")
            listing.garage_type = description.get("garage_type")
            listing.garage = description.get("garage")
            listing.pool = description.get("pool")
            listing.fireplace = description.get("fireplace")
            listing.heating = description.get("heating")
            listing.cooling = description.get("cooling")
            listing.exterior = description.get("exterior")

            listing.description = description.get("text")

            if not listing.description and data.get("property_history"):
                listing.description = data["property_history"][0]["listing"][
                    "description"
                ].get("text")
        if listing["location"]["address"]["coordinate"] is not None:
            listing.latitude = data["location"]["address"]["coordinate"].get(
                "lat"
            )
            listing.longitude = data["location"]["address"]["coordinate"].get(
                "lon"
            )

        if listing.get("tags"):
            for tag in listing["tags"]:
                currTag, _ = HomeListingTags.objects.get_or_create(tag=tag)
                if currTag not in listing.tag.all():
                    listing.tag.add(currTag)

        extras = []
        for extra in description.get("details", []):
            if extra.get("category") in [
                "Interior Features",
                "Heating and Cooling",
            ]:
                extras.extend(extra.get("text", []))

        if data.get("advertisers"):
            advertiser = data["advertisers"][0]
            realtor, _ = Realtor.objects.get_or_create(
                company=advertiser.get("broker", {}).get("name"),
                email=advertiser.get("email"),
                url=advertiser.get("href"),
                name=advertiser.get("name"),
                phone=advertiser.get("phones", [{}])[0].get("number"),
            )
            listing.realtor = realtor
        listing.save()

    except Exception as e:
        logging.error(e)
        logging.error(data)
        logging.error(f"ERROR: {listing.permalink}")
