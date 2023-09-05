from apify_client import ApifyClient
from celery import shared_task
from datetime import datetime
import logging

from accounts.models import Company
from config.settings import APIFY_TOKEN
from data.models import Client, HomeListing, Realtor, ZipCode

from .utils import del_variables, parse_streets, send_zapier_recently_sold

# Initialize the ApifyClient with your API token
client = ApifyClient(APIFY_TOKEN)


@shared_task
def get_listings(zip_code, status):

    search_type = "sell" if status == "House For Sale" else "sold"
    # Prepare the Actor input
    run_input = {
        "location": [zip_code],
        "limit": 1000,
        "sort": "newest",
        "search_type": search_type,
        "category": "category1",
        "page": 1,
        "includes:description": True,
        "includes:foreClosure": True,
        "includes:homeInsights": True,
        "includes:attributionInfo": True,
        "includes:resoFacts": True,

    }

    # Run the Actor and wait for it to finish
    run = client.actor(
        "jupri/zillow-scraper").call(
        run_input=run_input, memory_mbytes=1024, wait_secs=120)

    # Fetch and print Actor results from the run's dataset (if there are any)
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        create_home_listings.delay(item, zip_code)


@shared_task
def get_all_zipcodes(company, zip=None):
    """
    This task retrieves all the zip codes associated with a given company.
    """
    # Initialization of variables
    company_object, zip_code_objects, zip_codes, zips = "", "", "", ""
    try:
        company = Company.objects.get(id=company)
        if company.service_area_zip_codes.count() > 0:
            zip_codes = company.service_area_zip_codes.values_list(
                'zip_code', flat=True).distinct()
        else:
            zip_codes = Client.objects.filter(
                company=company, active=True
            ).values_list('zip_code', flat=True).distinct()
            zip_codes = ZipCode.objects.filter(
                zip_code__in=zip_codes
            ).values_list('zip_code', flat=True).distinct()
        zips = list(zip_codes.filter(
            last_updated__lt=(datetime.today()).strftime("%Y-%m-%d"),
        ))
        zip_codes.update(last_updated=datetime.today().strftime("%Y-%m-%d"))

    except Exception as e:
        if zip:
            zips = [str(zip)]
        else:
            logging.error(e)

    # Additional logic and task delays
    for zip in zips:
        get_listings.delay(
            zip, "House For Sale")
        get_listings.delay(
            zip, "House Recently Sold (6)")

    # send listings to zapier
    days_to_run = [0]  # Only on Monday
    current_day = datetime.now().weekday()

    if current_day in days_to_run:
        send_zapier_recently_sold.delay(company)
    del_variables(
        [company_object, zip_code_objects, zip_codes, zips, company]
    )


@shared_task
def create_home_listings(listing, zip_code):
    realtor, home_listing = "", ""
    # try:
    home_listing, _ = HomeListing.objects.get_or_create(
        address=parse_streets(listing["address"]["streetAddress"]),
        city=listing["address"]["city"],
        state=listing["address"]["state"],
        zip_code=ZipCode.objects.get(
            zip_code=zip_code
        ),
    )
    status = "House For Sale" if listing[
        "homeStatus"] == "FOR_SALE" else "House Recently Sold (6)"
    if listing["homeStatus"] == "FOR_SALE":
        home_listing.status = "House For Sale"
    elif listing["homeStatus"] == "RECENTLY_SOLD":
        home_listing.status = "House Recently Sold (6)"
    elif listing["homeStatus"] == "SOLD":
        home_listing.status = "House Recently Sold (12)"
    elif listing["homeStatus"] == "PENDING":
        home_listing.status = "Pending"
    else:
        home_listing.delete()
        return

    home_listing.status = status

    timestamp_ms = listing["listingDateTimeOnZillow"] \
        if status == "House For Sale" else listing["lastSoldDate"]
    timestamp_seconds = timestamp_ms / 1000  # Convert milliseconds to seconds
    # Create a datetime object from the Unix timestamp
    datetime_obj = datetime.utcfromtimestamp(timestamp_seconds)
    # Format the datetime object as a string
    formatted_date = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    home_listing.listed = formatted_date[:10]
    if listing.get("price"):
        home_listing.price = listing["price"].get("value", 0)
    home_listing.housing_type = listing.get("propertyType", "")
    home_listing.year_built = listing.get("yearBuilt", 0)
    home_listing.bedrooms = listing.get("bedrooms", 0)
    home_listing.bathrooms = listing.get("bathrooms", 0)
    # home_listing.sqft = listing["livingArea"]
    # home_listing.lot_sqft = listing["lotSize"]
    if listing.get("location"):
        home_listing.latitude = listing["location"].get("latitude", 0)
        home_listing.longitude = listing["location"].get("longitude", 0)

    realtor_info = listing["attributionInfo"]
    realtor, _ = Realtor.objects_with_listing_count.get_or_create(
        name=realtor_info.get("agentName", ""),
        company=realtor_info.get("brokerName", ""),
        agent_phone=realtor_info.get("agentPhoneNumber", ""),
        brokerage_phone=realtor_info.get("brokerPhoneNumber", "")
    )
    home_listing.realtor = realtor

    # TODO: Get all the description fields and tags
    home_listing.save()
    # except Exception as e:
    #     print(e)
    #     pass

    del_variables(
        [realtor, listing, home_listing]
    )
