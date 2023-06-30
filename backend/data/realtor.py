import json
import logging
import math
from datetime import datetime
from bs4 import BeautifulSoup
from celery import shared_task
from django.core.exceptions import MultipleObjectsReturned
from django.db import transaction
from scrapfly import ScrapeConfig, ScrapflyClient

from config import settings
from accounts.models import Company
from .models import Client, HomeListing, ZipCode, HomeListingTags, Realtor
from .utils import del_variables

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
        logging.error(e)

    # Additional logic and task delays
    for i in range(len(zips) * 2):
        extra = ""
        if i % 2 == 0:
            status = "House For Sale"
            url = "https://www.realtor.com/realestateandhomes-search"
        elif i % 2 == 1:
            status = "House Recently Sold (6)"
            url = "https://www.realtor.com/realestateandhomes-search"
            extra = "show-recently-sold/"
        find_data.delay(str(zips[i // 2]["zip_code"]), i, status, url, extra)
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
            first_result = get_scrapfly_scrape(scrapfly, first_page)

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

        # Process data based on status
        if status == "For Rent":
            results = first_data["properties"]
            total = int(
                soup.find("div", {"data-testid": "total-results"}).text
            )
            count = len(results)
            url += "/pg-1"
        else:
            results = first_data["results"]
            total = int(
                soup.find("span", {"class": "result-count"}).text.split(" ")[
                    0
                ]
            )
            count = first_data["count"]

        create_home_listings(results, status)
        if count == 0 or total == 0:
            return

        # Determine the number of pages
        total_pages = 1 if count < 20 else math.ceil(total / count)

        # Iterate through all pages
        for page in range(2, total_pages + 1):
            if "pg-1" not in url:
                raise ValueError(
                    "URL does not contain 'pg-1', "
                    "might risk scraping duplicate pages."
                )
            page_url = url.replace("pg-1", f"pg-{page}")
            new_results = get_scrapfly_scrape(scrapfly, page_url)
            if new_results.status_code >= 400:
                scrapfly = zip_scrapflies[(i + 5) % 20]
                new_results = get_scrapfly_scrape(scrapfly, page_url)

            content = new_results.scrape_result["content"]
            parsed = parse_search(new_results, status)
            if status == "For Rent":
                results = parsed["properties"]
            else:
                results = parsed["results"]
            create_home_listings(results, status)

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


def get_scrapfly_scrape(scrapfly, page):
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
            asp=False,
            proxy_pool="public_datacenter_pool",
        )
    )


def parse_search(result, status):
    """
    This function parses the page's content and returns the parsed data.

    Args:
        result (ScrapeResult): the page's content
        status (str): status of property (for sale, rent, etc.)

    Returns:
        dict: parsed data
    """
    content = result.scrape_result["content"]
    soup = BeautifulSoup(content, features="html.parser")
    if status == "For Rent":
        return parse_properties(soup, result)
    else:
        return parse_for_sale(soup, result)


def parse_property(property_card, result):
    """
    This function parses an individual property card.

    Args:
        property_card (bs4.element.Tag):
        a BeautifulSoup element representing a property card
        result (ScrapeResult): the page's content

    Returns:
        dict: property details
    """
    property_details = {
        "address": property_card.find("div", class_="property-address").text,
        "price": property_card.find("div", class_="property-price").text,
        # More fields here...
        # TODO
    }

    return property_details


def parse_listing(listing, result):
    """
    This function parses an individual listing.

    Args:
        listing (bs4.element.Tag): a BeautifulSoup element representing a listing
        result (ScrapeResult): the page's content

    Returns:
        dict: listing details
    """
    listing_details = {
        "address": listing.find("div", class_="listing-address").text,
        "price": listing.find("div", class_="listing-price").text,
        # More fields here...
        # TODO
    }

    return listing_details


def parse_properties(soup, result):
    """
    This function parses properties and their details.

    Args:
        soup (BeautifulSoup): parsed HTML content
        result (ScrapeResult): the page's content

    Returns:
        dict: properties and their details
    """
    properties = soup.find_all("div", {"data-testid": "property-card"})
    return {"properties": [parse_property(p, result) for p in properties]}


def parse_for_sale(soup, result):
    """
    This function parses the details for properties for sale.

    Args:
        soup (BeautifulSoup): parsed HTML content
        result (ScrapeResult): the page's content

    Returns:
        dict: details of properties for sale
    """
    listings = soup.find_all("li", {"class": "component_property-card"})
    return {
        "results": [parse_listing(listing, result) for listing in listings],
        "count": len(listings),
    }


def create_home_listings(results, status):
    """
    This function creates home listings and adds them to the database.

    Args:
        results (list): parsed data from the page's content
        status (str): status of property (for sale, rent, etc.)

    Returns:
        None
    """
    for result in results:
        try:
            HomeListing.objects.create(**result)
        except Exception as e:
            logging.error(f"Failed to create listing: {e}. Result: {result}")


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
        "permalink": property["permalink"],
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


def update_home_listings(properties):
    """
    This function updates or creates home listings in the database.

    Args:
        properties (list): list of property details

    Returns:
        None
    """
    with transaction.atomic():
        for property in properties:
            try:
                zip_code = ZipCode.objects.get(zip_code=property["zip_code"])
                HomeListing.objects.update_or_create(
                    address=property["streetAddress"],
                    city=property["city"],
                    state=property["state"],
                    zip_code=zip_code,
                    defaults={"permalink": property["permalink"]},
                )
            except MultipleObjectsReturned as e:
                HomeListing.objects.filter(
                    address=property["streetAddress"],
                    city=property["city"],
                    state=property["state"],
                    zip_code=zip_code,
                ).update(permalink=property["permalink"])
                error_string = (
                    f"Multiple objects returned for "
                    f"{property['streetAddress']}, {property['city']}, "
                    f"{property['state']}, {property['zip_code']} {e}"
                )
                logging.error(error_string)


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
    update_home_listings(allProps)


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

        extras = []
        for extra in description.get("details", []):
            if extra.get("category") in [
                "Interior Features",
                "Heating and Cooling",
            ]:
                extras.extend(extra.get("text", []))

        if data.get("advertisers"):
            update_advertiser(listing, data["advertisers"][0])

        listing.save()
    except Exception as e:
        logging.error(e)
        logging.error(data)
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
