import json
import logging
import math
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from celery import shared_task
from scrapfly import ScrapeConfig, ScrapflyClient

from config import settings
from accounts.models import Company
from .models import Client, HomeListing, ZipCode, HomeListingTags, Realtor
from .utils import del_variables, parse_streets, send_zapier_recently_sold

zip_scrapflies = [
    ScrapflyClient(key=settings.SCRAPFLY_KEY, max_concurrency=1)
    for _ in range(1, 21)
]

detail_scrapflies = [
    ScrapflyClient(key=settings.SCRAPFLY_KEY, max_concurrency=1)
    for _ in range(1, 21)
]


@shared_task
def get_all_zipcodes(company, zip=None):
    """
    This task retrieves all the zip codes associated with a given company.
    """
    # Initialization of variables
    company_object, zip_code_objects, zip_codes, zips = "", "", "", ""
    try:
        company_object = Company.objects.get(id=company)
        zip_code_objects = Client.objects.filter(
            company=company_object, active=True
        ).values("zip_code")
        zip_codes = zip_code_objects.distinct()
        zip_codes = ZipCode.objects.filter(
            zip_code__in=zip_code_objects,
            last_updated__lt=(datetime.today()).strftime("%Y-%m-%d"),
        )
        zips = list(zip_codes.order_by("zip_code").values("zip_code"))
        zip_codes.update(last_updated=datetime.today().strftime("%Y-%m-%d"))

    except Exception as e:
        if zip:
            zips = [{"zip_code": str(zip)}]
        else:
            logging.error(e)

    # Additional logic and task delays
    for i in range(len(zips) * 2):
        if i % 2 == 0:
            status = "House For Sale"
            url = "https://www.realtor.com/realestateandhomes-search"
            extra = "sby-6"
        elif i % 2 == 1:
            status = "House Recently Sold (6)"
            url = "https://www.realtor.com/realestateandhomes-search"
            extra = "show-recently-sold/"
        find_data.delay(
            str(zips[i // 2]["zip_code"]), i, status, url, extra)

    # send listings to zapier
    # days_to_run = [0]  # Only on Monday
    # current_day = datetime.now().weekday()

    # if current_day in days_to_run:
    #     send_zapier_recently_sold.delay(company)
    del_variables(
        [company_object, zip_code_objects, zip_codes, zips, company]
    )


@shared_task
def find_data(zip_code, i, status, url, extra):
    """
    This function uses Celery task to find data.

    Args:
        zip_code (str): zip code for search criteria
        i (int): index for determining scrapfly
        status (str): status of property (for sale, rent, etc.)
        url (str): URL for scraping
        extra (str): additional data for the request

    Returns:
        None
    """
    # Initialize variables
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
    ) = ("", "", "", "", "", "", "", "", "", "", "", "")

    scrapfly = zip_scrapflies[i % 20]

    try:
        # Fetch the first page and results
        first_page = f"{url}/{zip_code}/{extra}"

        first_result = get_scrapfly_scrape(scrapfly, first_page)

        if first_result.status_code >= 400:
            scrapfly = zip_scrapflies[(i + 5) % 20]
            first_result = get_scrapfly_scrape(scrapfly, first_page, asp=True)

        # Parse the first page
        content = first_result.scrape_result["content"]
        soup = BeautifulSoup(content, features="html.parser")

        # Add pagination to the url if it doesn't exist
        if "pg-1" not in first_result.context["url"]:
            url = first_result.context["url"] + "/pg-1"
        else:
            url = first_result.context["url"]

        first_data = parse_search(first_result, status)
        if not first_data:
            return
        count = len(first_data)

        total = 0
        val = soup.find("div", attrs={"data-testid": "total-results"})
        if val:
            total = int(val.text)
        else:
            val = soup.find("span", {"class": "result-count"})
            if val:
                total = int(val.text.split(" ")[0])

        continue_scraping = create_home_listings(first_data, status)
        # print(f"Result: {continue_scraping}, url: {url}")
        if count == 0 or total == 0:
            return

        # Determine the number of pages
        total_pages = 1 if count < 40 else math.ceil(total / count)
        # Iterate through all pages
        for page in range(2, total_pages + 1):
            if continue_scraping:
                if "pg-1" not in url:
                    raise ValueError(
                        "URL does not contain 'pg-1', "
                        "might risk scraping duplicate pages."
                    )
                page_url = url.replace("pg-1", f"pg-{page}")
                new_results = get_scrapfly_scrape(scrapfly, page_url)
                if new_results.status_code >= 400:
                    scrapfly = zip_scrapflies[(i + 5) % 20]
                    new_results = get_scrapfly_scrape(
                        scrapfly, page_url, asp=True)

                content = new_results.scrape_result["content"]
                parsed = parse_search(new_results, status)
                count = len(parsed)
                if not parsed or count == 0:
                    return

                continue_scraping = create_home_listings(parsed, status)
                # print(f"Result: {continue_scraping}, url: {page_url}")

    except Exception as e:
        logging.error(
            f"ERROR during getHomesForSale: {e} with zip_code {zip_code}"
        )
        logging.error(f"URL: {url}")

    del_variables(
        [
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
        ]
    )


def get_scrapfly_scrape(scrapfly, page, asp=False):
    """
    Helper function to avoid repeating Scrapfly API calls.

    Args:
        scrapfly (str): Scrapfly API key
        page (str): URL to scrape

    Returns:
        Scrapfly's ScrapeConfig object
    """
    return scrapfly.scrape(
        ScrapeConfig(
            url=page,
            country="US",
            asp=asp,
            proxy_pool="public_datacenter_pool",
        )
    )


def parse_search(result, search_type: str):
    data = result.selector.css("script#__NEXT_DATA__::text").get()
    if not data:
        logging.error(f"page {result.context['url']}: Not Data")
        return

    data = dict(json.loads(data))
    try:
        data = data["props"]["pageProps"]["searchResults"]["home_search"][
            "results"
        ]
        return data
    except KeyError:
        try:
            data = data["props"]["pageProps"]["properties"]
            return data
        except KeyError as e:
            logging.error(f"page {result.context['url']}: KeyError")
            logging.error(f"KeyError: {e}")
            return False


def create_home_listings(results, status):
    zip_object, created, list_type, home_listing, curr_tag = (
        "",
        "",
        "",
        "",
        "",
    )
    two_years_ago = datetime.now() - timedelta(days=365 * 2)
    for listing in results:
        zip_object, created = ZipCode.objects.get_or_create(
            zip_code=listing["location"]["address"]["postal_code"]
        )
        try:
            if status == "House Recently Sold (6)":
                if listing["description"]["sold_date"] is not None:
                    list_type = listing["description"]["sold_date"]
                elif listing["last_update_date"] is not None:
                    list_type = listing["last_update_date"]
                elif listing["list_date"] is not None:
                    list_type = listing["list_date"]
                else:
                    list_type = None
                    list_type = listing["description"]["sold_date"]
                    if list_type is not None:
                        try:
                            date_compare = datetime.strptime(
                                list_type, "%Y-%m-%dT%H:%M:%SZ"
                            )
                        except Exception as e:
                            logging.error(e)
                            date_compare = datetime.strptime(
                                list_type, "%Y-%m-%d"
                            )
                        if date_compare < two_years_ago:
                            continue
            else:
                list_type = listing["list_date"]
            if list_type is None:
                list_type = "2022-01-01"
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

            if listing.get("location", {}).get("address", {}).get("coordinate"):
                latitude = listing["location"]["address"]["coordinate"].get(
                    "lat"
                )
                longitude = listing["location"]["address"]["coordinate"].get(
                    "lon"
                )
            else:
                latitude = 0
                longitude = 0

            # Check if the HomeListing already exists
            try:
                if listing["location"]["address"]["line"] is None:
                    continue

                home_listing = HomeListing.objects.get(
                    # zip_code=zip_object,
                    # address=parse_streets(
                    #     (listing["location"]["address"]["line"]).title()
                    # ),
                    # city=listing["location"]["address"]["city"],
                    # state=listing["location"]["address"]["state_code"],
                    description=listing["property_id"]
                )

                # Have found a listing that we have already scraped
                if home_listing.status == status:
                    return False

                home_listing.description = listing["property_id"]

                # Update all the fields if it already exists
                home_listing.status = status
                home_listing.listed = list_type[:10]
                home_listing.price = price
                home_listing.housing_type = listing["description"]["type"]
                home_listing.year_built = year_built
                home_listing.latitude = latitude
                home_listing.longitude = longitude
                home_listing.lot_sqft = listing["description"].get(
                    "lot_sqft", 0
                )
                home_listing.bedrooms = beds
                home_listing.bathrooms = baths
                home_listing.cooling = cooling
                home_listing.heating = heating
                home_listing.sqft = sqft
                home_listing.save()
            except HomeListing.DoesNotExist:
                # Create a new HomeListing if it doesn't exist
                if listing["location"]["address"]["line"] is None:
                    continue

                home_listing = HomeListing.objects.create(
                    zip_code=zip_object,
                    address=parse_streets(
                        (listing["location"]["address"]["line"]).title()
                    ),
                    status=status,
                    listed=list_type[:10],
                    price=price,
                    housing_type=listing["description"]["type"],
                    year_built=year_built,
                    state=listing["location"]["address"]["state_code"],
                    city=listing["location"]["address"]["city"],
                    latitude=latitude,
                    longitude=longitude,
                    lot_sqft=listing["description"].get("lot_sqft", 0),
                    bedrooms=beds,
                    bathrooms=baths,
                    cooling=cooling,
                    heating=heating,
                    sqft=sqft,
                    description=listing["property_id"],
                )

            if "tags" in listing:
                if listing["tags"] is not None:
                    for tag in listing["tags"]:
                        curr_tag, _ = HomeListingTags.objects.get_or_create(
                            tag=tag
                        )
                        home_listing.tag.add(curr_tag)

            # if "branding" in listing:
            #     if listing["branding"] is not None:
            #         try:
            #             for brand in listing["branding"]:
            #                 if brand["name"] is not None:
            #                     realtor, _ = Realtor.objects.get_or_create(
            #                         name=brand["name"]
            #                     )
            #                     home_listing.realtor = realtor
            #                     home_listing.save()
            #         except Exception as e:
            #             logging.error(e)

        except Exception as e:
            logging.error(f"Listing: {listing['location']['address']}")
            logging.error(e)
    del_variables(
        [zip_object, created, list_type, home_listing, curr_tag, results]
    )
    return True


def create_url(city, state, street, page):
    """
    This function creates a URL for property record search.

    Args:
        city (str): city name
        state (str): state name
        street (str): street name
        page (int): page number

    Returns:
        str: URL
    """
    combined_url = (
        f"https://www.realtor.com/propertyrecord-search"
        f"/{city}_{state}/{street}/pg-{page}"
    )
    return combined_url


def get_property_details(property):
    """
    This function parses the property details.

    Args:
        property (dict): property data

    Returns:
        dict: parsed property details
    """
    return {
        "streetAddress": property["location"]["address"]["line"],
        "city": property["location"]["address"]["city"],
        "state": property["location"]["address"]["state_code"],
        "zip_code": property["location"]["address"]["postal_code"],
    }


def get_data_from_response(result):
    """
    This function gets the required data from the API response.

    Args:
        result (ScrapeResult): API response

    Returns:
        dict: parsed data
        int: total number of pages
    """
    data = result.selector.css("script#__NEXT_DATA__::text").get()
    data = dict(json.loads(data))
    total = data["props"]["pageProps"]["geo"]["homeValuesListDetails"][
        "total"
    ]
    pages = math.ceil(total / 106)
    results = data["props"]["pageProps"]["geo"]["homeValuesListDetails"][
        "results"
    ]
    return results, pages


# def update_home_listings(properties):
#     """
#     This function updates or creates home listings in the database.

#     Args:
#         properties (list): list of property details

#     Returns:
#         None
#     """
#     with transaction.atomic():
#         for property in properties:
#             try:
#                 zip_code = ZipCode.objects.get(zip_code=property["zip_code"])
#                 HomeListing.objects.update_or_create(
#                     address=property["streetAddress"],
#                     city=property["city"],
#                     state=property["state"],
#                     zip_code=zip_code,
#                 )
#             except MultipleObjectsReturned as e:
#                 HomeListing.objects.filter(
#                     address=property["streetAddress"],
#                     city=property["city"],
#                     state=property["state"],
#                     zip_code=zip_code,
#                 ).update(permalink=property["permalink"])
#                 error_string = (
#                     f"Multiple objects returned for "
#                     f"{property['streetAddress']}, {property['city']}, "
#                     f"{property['state']}, {property['zip_code']} {e}"
#                 )
#                 logging.error(error_string)


@shared_task
def get_realtor_property_records(address, city, state):
    street = address.split(" ", 1)[1].replace(" ", "-")
    city = city.replace(" ", "-")
    scrapfly = ScrapflyClient(key=settings.SCRAPFLY_KEY, max_concurrency=1)
    allProps = []
    url = create_url(city, state, street, 1)
    result = scrapfly.scrape(
        ScrapeConfig(
            url, country="US", asp=False, proxy_pool="public_datacenter_pool"
        )
    )
    data, pages = get_data_from_response(result)
    allProps.extend([get_property_details(p) for p in data])
    for page in range(2, pages + 1):
        url = create_url(city, state, street, page)
        result = scrapfly.scrape(
            ScrapeConfig(
                url,
                country="US",
                asp=False,
                proxy_pool="public_datacenter_pool",
            )
        )
        data, _ = get_data_from_response(result)
        allProps.extend([get_property_details(p) for p in data])


def create_detail_url(listing):
    """
    This function creates a URL for property detail.

    Args:
        listing (HomeListing): HomeListing object

    Returns:
        str: URL
    """
    url = (
        f"https://www.realtor.com/realestateandhomes-detail"
        f"/{listing.permalink}"
    )
    return url


def get_listing_data(result):
    """
    This function gets the required data from the API response.

    Args:
        result (ScrapeResult): API response

    Returns:
        dict: parsed data
    """
    data = result.selector.css("script#__NEXT_DATA__::text").get()
    data = dict(json.loads(data))
    return data["props"]["pageProps"]["initialReduxState"]["propertyDetails"]


def update_listing_data(listing, data):
    """
    This function updates the HomeListing object with the property details.

    Args:
        listing (HomeListing): HomeListing object
        data (dict): property details

    Returns:
        None
    """
    try:
        description = data.get("description", {})
        if description:
            for key in [
                "year_built",
                "year_renovated",
                "type",
                "beds",
                "baths",
                "sqft",
                "lot_sqft",
                "roofing",
                "garage_type",
                "garage",
                "pool",
                "fireplace",
                "heating",
                "cooling",
                "exterior",
                "text",
            ]:
                setattr(listing, key, description.get(key))

            if not listing.description and data.get("property_history"):
                listing.description = data["property_history"][0]["listing"][
                    "description"
                ].get("text")

        if data.get("location", {}).get("address", {}).get("coordinate"):
            listing.latitude = data["location"]["address"]["coordinate"].get(
                "lat"
            )
            listing.longitude = data["location"]["address"]["coordinate"].get(
                "lon"
            )

        if data.get("tags"):
            update_listing_tags(listing, data["tags"])

        for extra in description.get("details", []):
            if extra.get("category") == "Interior Features":
                listing.interiorFeaturesDescription = extra.get("text")
            elif extra.get("category") == "Heating and Cooling":
                listing.heatingCoolingDescription = extra.get("text")

        if data.get("advertisers"):
            update_advertiser(listing, data["advertisers"][0])

        listing.save()
    except Exception as e:
        logging.error(e)
        logging.error(f"ERROR: {listing.permalink}")


def update_listing_tags(listing, tags):
    """
    This function updates the HomeListing object's tags.

    Args:
        listing (HomeListing): HomeListing object
        tags (list): list of tags

    Returns:
        None
    """
    for tag in tags:
        currTag, _ = HomeListingTags.objects.get_or_create(tag=tag)
        if currTag not in listing.tag.all():
            listing.tag.add(currTag)


def update_advertiser(listing, advertiser):
    """
    This function updates the HomeListing object's advertiser.

    Args:
        listing (HomeListing): HomeListing object
        advertiser (dict): advertiser details

    Returns:
        None
    """
    realtor, _ = Realtor.objects.get_or_create(
        company=advertiser.get("broker", {}).get("name"),
        email=advertiser.get("email"),
        url=advertiser.get("href"),
        name=advertiser.get("name"),
        phone=advertiser.get("phones", [{}])[0].get("number"),
    )
    listing.realtor = realtor


def get_realtor_property_details(listingId, scrapfly):
    listing = HomeListing.objects.get(id=listingId)
    url = create_detail_url(listing)
    result = scrapfly.scrape(
        ScrapeConfig(
            url, country="US", asp=False, proxy_pool="public_datacenter_pool"
        )
    )
    data = get_listing_data(result)
    update_listing_data(listing, data)


# from apify_client import ApifyClient
# from celery import shared_task
# from datetime import datetime
# import logging

# from accounts.models import Company
# from config.settings import APIFY_TOKEN
# from data.models import Client, HomeListing, Realtor, ZipCode

# from .utils import (
#     del_variables,
#     format_address_for_scraper,
#     parse_streets,
#     send_zapier_recently_sold
# )

# # Initialize the ApifyClient with your API token
# client = ApifyClient(APIFY_TOKEN)


# @shared_task
# def get_listings(zip_code=None, status=None, addresses=None):

#     location = [zip_code] if addresses is None else addresses
#     search_type = "sell" if status == "House For Sale" else "sold"
#     limit = 5 if addresses else 1000
#     if addresses:
#         memory = 256
#     elif status == "House For Sale":
#         memory = 2048
#     else:
#         memory = 4096

#     # Prepare the Actor input
#     run_input = {
#         "location": location,
#         "limit": limit,
#         "sort": "newest",
#         "search_type": search_type,
#         "category": "category1",
#         "includes:description": True,
#         "includes:foreClosure": True,
#         "includes:homeInsights": True,
#         "includes:attributionInfo": True,
#         "includes:resoFacts": True,
#         "dev_proxy_config": {
#             "useApifyProxy": True,
#             "apifyProxyGroups": [
#                 "StaticUS3",
#                 "BUYPROXIES94952"
#             ]
#         },

#     }

#     # Run the Actor and wait for it to finish
#     run = client.actor(
#         "jupri/zillow-scraper").call(
#         run_input=run_input, memory_mbytes=memory, wait_secs=120)

#     # Fetch and print Actor results from the run's dataset (if there are any)
#     items = []
#     for item in client.dataset(run["defaultDatasetId"]).iterate_items():
#         items.append(item)
#     del_variables([run_input, run])
#     if addresses:
#         if items:
#             edit_client_with_housing_data.delay(items)
#     else:
#         create_home_listings(items, zip_code)


# @shared_task
# def get_all_zipcodes(company, zip=None):
#     """
#     This task retrieves all the zip codes associated with a given company.
#     """
#     # Initialization of variables
#     company_object, zip_code_objects, zip_codes, zips = "", "", "", ""
#     try:
#         company = Company.objects.get(id=company)
#         if company.service_area_zip_codes.count() > 0:
#             zip_codes = company.service_area_zip_codes.values_list(
#                 'zip_code', flat=True).distinct()
#         else:
#             zip_codes = list(Client.objects.filter(
#                 company=company, active=True
#             ).values_list('zip_code', flat=True).distinct())
#             zip_codes = ZipCode.objects.filter(
#                 zip_code__in=zip_codes
#             ).values_list('zip_code', flat=True).distinct()
#         zips = list(zip_codes.filter(
#             last_updated__lt=(datetime.today()).strftime("%Y-%m-%d"),
#         ))
#         zip_codes.update(last_updated=datetime.today().strftime("%Y-%m-%d"))

#     except Exception as e:
#         if zip:
#             zips = [str(zip)]
#         else:
#             logging.error(e)

#     # Additional logic and task delays
#     for zip in zips:
#         get_listings.delay(
#             zip_code=zip, status="House For Sale")
#         get_listings.delay(
#             zip_code=zip, status="House Recently Sold (6)")

#     # send listings to zapier
#     days_to_run = [0]  # Only on Monday
#     current_day = datetime.now().weekday()

#     if current_day in days_to_run:
#         send_zapier_recently_sold.delay(company)
#     del_variables(
#         [company_object, zip_code_objects, zip_codes, zips, company]
#     )


# @shared_task
# def get_all_client_housing_details(company):
#     company = Company.objects.get(id=company)
#     client_ids = list(Client.objects.filter(
#         company=company, active=True, year_built=0
#     ).values_list('id', flat=True).distinct())
#     addresses = []
#     for client_id in client_ids:
#         addresses.append(format_address_for_scraper(client_id))
#         if len(addresses) == 100:
#             get_listings.delay(addresses=addresses)
#             addresses = []
#     if len(addresses) > 0:
#         get_listings.delay(addresses=addresses)
#     del_variables(
#         [company, client_ids]
#     )


# @shared_task
# def edit_client_with_housing_data(addresses):
#     for address in addresses:
#         try:
#             clients = Client.objects.filter(
#                 address=parse_streets(address["address"]["streetAddress"]),
#                 city=address["address"]["city"],
#                 state=address["address"]["state"],
#                 zip_code=ZipCode.objects.get(
#                     zip_code=address["address"]["zipcode"]
#                 ),
#             )
#             if clients.exists():
#                 for client in clients:
#                     client.housing_type = address.get("propertyType", "")
#                     client.year_built = address.get("yearBuilt", 0)
#                     client.bedrooms = address.get("bedrooms", 0)
#                     client.bathrooms = int(address.get("bathrooms", 0))
#                     client.sqft = address.get("livingArea", 0)
#                     client.lot_sqft = address.get("lotSize", 0)
#                     client.description = address.get("description", "")
#                     client.save()
#         except Exception as e:
#             print(e)


# @shared_task
# def create_home_listings(listings, zip_code):
#     realtor, home_listing, listing = "", "", ""
#     # try:
#     home_listings = []
#     for listing in listings:
#         try:
#             home_listing, _ = HomeListing.objects.get_or_create(
#                 address=parse_streets(listing["address"]["streetAddress"]),
#                 city=listing["address"]["city"],
#                 state=listing["address"]["state"],
#                 zip_code=ZipCode.objects.get(
#                     zip_code=zip_code
#                 ),
#             )
#             if listing["homeStatus"] == "FOR_SALE":
#                 home_listing.status = "House For Sale"
#             elif listing["homeStatus"] == "RECENTLY_SOLD":
#                 home_listing.status = "House Recently Sold (6)"
#             # NOTE: I really don't care about anything over 6 months.
#             # Our new source has data going back years
#             # elif listing["homeStatus"] == "SOLD":
#             #     home_listing.status = "House Recently Sold (12)"
#             elif listing["homeStatus"] == "PENDING":
#                 home_listing.status = "Pending"
#             else:
#                 home_listing.delete()
#                 continue

#             timestamp_ms = listing["listingDateTimeOnZillow"] \
#                 if home_listing.status == "House For Sale" \
#                 else listing["lastSoldDate"]
#             # Convert milliseconds to seconds
#             timestamp_seconds = timestamp_ms / 1000
#             # Create a datetime object from the Unix timestamp
#             datetime_obj = datetime.utcfromtimestamp(timestamp_seconds)
#             # Format the datetime object as a string
#             formatted_date = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
#             home_listing.listed = formatted_date[:10]
#             if listing.get("price"):
#                 home_listing.price = listing["price"].get("value", 0)
#             home_listing.housing_type = listing.get("propertyType", "")
#             home_listing.year_built = listing.get("yearBuilt", 0)
#             home_listing.bedrooms = listing.get("bedrooms", 0)
#             home_listing.bathrooms = listing.get("bathrooms", 0)
#             # home_listing.sqft = listing["livingArea"]
#             # home_listing.lot_sqft = listing["lotSize"]
#             if listing.get("location"):
#                 home_listing.latitude = listing["location"].get("latitude", 0)
#                 home_listing.longitude = listing["location"].get(
#                     "longitude", 0)

#             realtor_info = listing["attributionInfo"]
#             agent_name = realtor_info.get("agentName", "")
#             if agent_name != "":
#                 realtor, _ = Realtor.objects_with_listing_count.get_or_create(
#                     name=agent_name,
#                     company=realtor_info.get("brokerName", ""),
#                     agent_phone=realtor_info.get("agentPhoneNumber", ""),
#                     brokerage_phone=realtor_info.get("brokerPhoneNumber", "")
#                 )
#                 home_listing.realtor = realtor

#             # TODO: Get all the description fields and tags
#             home_listings.append(home_listing)
#         except Exception as e:
#             print(e)
#     HomeListing.objects.bulk_update(home_listings, [
#         "status", "listed", "price", "housing_type", "year_built",
#         "bedrooms", "bathrooms", "latitude", "longitude", "realtor"
#     ])

#     del_variables(
#         [realtor, listing, home_listing, listings]
#     )
