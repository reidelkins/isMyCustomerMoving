from apify_client import ApifyClient
from celery import shared_task
from datetime import datetime
import logging

from accounts.models import Company
from config.settings import APIFY_TOKEN
from data.models import Client, HomeListing, Realtor, ZipCode

from .utils import (
    del_variables,
    format_address_for_scraper,
    parse_streets,
    send_zapier_recently_sold
)

# Initialize the ApifyClient with your API token
client = ApifyClient(APIFY_TOKEN)


@shared_task
def get_listings(zip_code=None, status=None, addresses=None):

    location = [zip_code] if addresses is None else [addresses]
    search_type = "sell" if status == "House For Sale" else "sold"
    limit = 5 if addresses else 1000
    if addresses:
        memory = 256
    elif status == "House For Sale":
        memory = 2048
    else:
        memory = 4096

    # Prepare the Actor input
    run_input = {
        "location": location,
        "limit": limit,
        "sort": "newest",
        "search_type": search_type,
        "category": "category1",
        "includes:description": True,
        "includes:foreClosure": True,
        "includes:homeInsights": True,
        "includes:attributionInfo": True,
        "includes:resoFacts": True,

    }

    # Run the Actor and wait for it to finish
    run = client.actor(
        "jupri/zillow-scraper").call(
        run_input=run_input, memory_mbytes=memory, wait_secs=120)

    # Fetch and print Actor results from the run's dataset (if there are any)
    items = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        items.append(item)
    del_variables([run_input, run])
    if addresses:
        if items:
            edit_client_with_housing_data.delay(items)
    else:
        create_home_listings(items, zip_code)


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
            zip_codes = list(Client.objects.filter(
                company=company, active=True
            ).values_list('zip_code', flat=True).distinct())
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
            zip_code=zip, status="House For Sale")
        get_listings.delay(
            zip_code=zip, status="House Recently Sold (6)")

    # send listings to zapier
    days_to_run = [0]  # Only on Monday
    current_day = datetime.now().weekday()

    if current_day in days_to_run:
        send_zapier_recently_sold.delay(company)
    del_variables(
        [company_object, zip_code_objects, zip_codes, zips, company]
    )


@shared_task
def get_all_client_housing_details(company):
    company = Company.objects.get(id=company)
    client_ids = list(Client.objects.filter(
        company=company, active=True, year_built=0
    ).values_list('id', flat=True).distinct())
    # addresses = []
    for client_id in client_ids:
        address = format_address_for_scraper(client_id)
        get_listings.delay(addresses=address)
    #     addresses.append(format_address_for_scraper(client_id))
    #     if len(addresses) == 5:
    #         get_listings.delay(addresses=addresses)
    #         addresses = []
    # if len(addresses) > 0:
    #     get_listings.delay(addresses=addresses)
    del_variables(
        [company, client_ids]
    )


@shared_task
def edit_client_with_housing_data(addresses):
    for address in addresses:
        try:
            clients = Client.objects.filter(
                address=parse_streets(address["address"]["streetAddress"]),
                city=address["address"]["city"],
                state=address["address"]["state"],
                zip_code=ZipCode.objects.get(
                    zip_code=address["address"]["zipcode"]
                ),
            )
            if clients.exists():
                for client in clients:
                    client.housing_type = address.get("propertyType", "")
                    client.year_built = address.get("yearBuilt", 0)
                    client.bedrooms = address.get("bedrooms", 0)
                    client.bathrooms = int(address.get("bathrooms", 0))
                    client.sqft = address.get("livingArea", 0)
                    client.lot_sqft = address.get("lotSize", 0)
                    client.description = address.get("description", "")
                    client.save()
        except Exception as e:
            print(e)


@shared_task
def create_home_listings(listings, zip_code):
    realtor, home_listing = "", ""
    # try:
    home_listings = []
    for listing in listings:
        try:
            home_listing, _ = HomeListing.objects.get_or_create(
                address=parse_streets(listing["address"]["streetAddress"]),
                city=listing["address"]["city"],
                state=listing["address"]["state"],
                zip_code=ZipCode.objects.get(
                    zip_code=zip_code
                ),
            )
            if listing["homeStatus"] == "FOR_SALE":
                home_listing.status = "House For Sale"
            elif listing["homeStatus"] == "RECENTLY_SOLD":
                home_listing.status = "House Recently Sold (6)"
            # NOTE: I really don't care about anything over 6 months.
            # Our new source has data going back years
            # elif listing["homeStatus"] == "SOLD":
            #     home_listing.status = "House Recently Sold (12)"
            elif listing["homeStatus"] == "PENDING":
                home_listing.status = "Pending"
            else:
                home_listing.delete()
                continue

            timestamp_ms = listing["listingDateTimeOnZillow"] \
                if home_listing.status == "House For Sale" \
                else listing["lastSoldDate"]
            # Convert milliseconds to seconds
            timestamp_seconds = timestamp_ms / 1000
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
                home_listing.longitude = listing["location"].get(
                    "longitude", 0)

            realtor_info = listing["attributionInfo"]
            agent_name = realtor_info.get("agentName", "")
            if agent_name != "":
                realtor, _ = Realtor.objects_with_listing_count.get_or_create(
                    name=agent_name,
                    company=realtor_info.get("brokerName", ""),
                    agent_phone=realtor_info.get("agentPhoneNumber", ""),
                    brokerage_phone=realtor_info.get("brokerPhoneNumber", "")
                )
                home_listing.realtor = realtor

            # TODO: Get all the description fields and tags
            home_listings.append(home_listing)
        except Exception as e:
            print(e)
    HomeListing.objects.bulk_update(home_listings, [
        "status", "listed", "price", "housing_type", "year_built",
        "bedrooms", "bathrooms", "latitude", "longitude", "realtor"
    ])

    del_variables(
        [realtor, listing, home_listing, listings]
    )
