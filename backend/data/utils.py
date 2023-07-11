from re import sub
from time import sleep
from accounts.models import Company, CustomUser
from config import settings
from .models import (
    Client,
    ZipCode,
    HomeListing,
    ClientUpdate,
    Task,
    HomeListingTags,
    SavedFilter,
)
from .serializers import ZapierClientSerializer, HomeListingSerializer

from celery import shared_task
from datetime import datetime, timedelta, date
import gc
import json
import logging
import requests
import traceback
from defusedxml.ElementTree import fromstring


from django.template.loader import get_template
from django.core.mail import EmailMessage, send_mail


def del_variables(vars):
    for var in vars:
        try:
            del var
        except NameError:
            pass
    gc.collect()


def find_client_count(subscription_product):
    if (
        subscription_product.amount == 150
        and subscription_product.interval == "month"
    ) or (
        subscription_product.amount == 1650
        and subscription_product.interval == "year"
    ):
        ceiling = 5000
    elif (
        subscription_product.amount == 250
        and subscription_product.interval == "month"
    ) or (
        subscription_product.amount == 2750
        and subscription_product.interval == "year"
    ):
        ceiling = 10000
    elif (
        subscription_product.amount == 400
        and subscription_product.interval == "month"
    ) or (
        subscription_product.amount == 4400
        and subscription_product.interval == "year"
    ):
        ceiling = 20000
    elif (
        subscription_product.amount == 1500
        and subscription_product.interval == "month"
    ) or (
        subscription_product.amount == 16500
        and subscription_product.interval == "year"
    ):
        ceiling = 150000
    elif (
        subscription_product.amount == 5000
        and subscription_product.interval == "month"
    ) or (
        subscription_product.amount == 55000
        and subscription_product.interval == "year"
    ):
        ceiling = 500000
    else:
        ceiling = 100000
    return ceiling


def find_clients_to_delete(client_count, subscription_type):
    ceiling = find_client_count(subscription_type)
    if client_count > ceiling:
        return client_count - ceiling
    else:
        return 0


def reactivate_clients(company_id):
    company = Company.objects.get(id=company_id)
    clients = Client.objects.filter(company=company)
    client_ceiling = find_client_count(company.product.product.name)
    if client_ceiling > clients.count():
        clients.update(active=True)
    else:
        to_reactive_count = (
            client_ceiling - clients.filter(active=True).count()
        )
        clients.filter(active=False).order_by("id")[
            :to_reactive_count
        ].update(active=True)


@shared_task
def delete_extra_clients(company_id, task_id=None):
    """
    Delete extra clients based on the company's subscription limit.

    :param company_id: ID of the company
    :param task_id: ID of the task (optional)
    """
    try:
        company = Company.objects.get(id=company_id)
        clients = Client.objects.filter(company=company, active=True)
        deleted_clients = find_clients_to_delete(
            clients.count(), company.product
        )

        if deleted_clients > 0:
            Client.objects.filter(
                id__in=list(
                    clients.values_list("id", flat=True)[:deleted_clients]
                )
            ).update(active=False)

            admins = CustomUser.objects.filter(
                company=company, status="admin"
            )
            mail_subject = "IMCM Clients Deleted"
            message_plain = (
                "Your company has exceeded the number of clients..."
            )
            message_html = get_template("clientsDeleted.html").render(
                {"deleted_clients": deleted_clients}
            )

            for admin in admins:
                send_mail(
                    subject=mail_subject,
                    message=message_plain,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[admin.email],
                    html_message=message_html,
                    fail_silently=False,
                )
    except Exception as e:
        logging.error(e)
        deleted_clients = 0

    if task_id:
        task = Task.objects.get(id=task_id)
        task.deleted_clients = deleted_clients
        task.completed = True
        task.save()


def parse_streets(street):
    """
    Parses street names into abbreviated forms.

    :param street: Street name
    :return: Abbreviated street name
    """
    conversions = {
        "Alley": "Aly",
        "Avenue": "Ave",
        "Boulevard": "Blvd",
        "Circle": "Cir",
        "Court": "Crt",
        "Cove": "Cv",
        "Canyon": "Cnyn",
        "Drive": "Dr",
        "Expressway": "Expy",
        "Highway": "Hwy",
        "Lane": "Ln",
        "Parkway": "Pkwy",
        "Place": "Pl",
        "Pike": "Pk",
        "Point": "Pt",
        "Road": "Rd",
        "Square": "Sq",
        "Street": "St",
        "Terrace": "Ter",
        "Trail": "Trl",
        "South": "S",
        "North": "N",
        "West": "W",
        "East": "E",
        "Northeast": "NE",
        "Northwest": "NW",
        "Southeast": "SE",
        "Southwest": "SW",
        "Ne": "NE",
        "Nw": "NW",
        "Sw": "SW",
        "Se": "SE",
    }
    for word in street.split():
        if word in conversions:
            street = street.replace(word, conversions[word])
    return street


def format_zip(zip_code):
    """
    Formats the zip code.

    :param zip_code: Zip code
    :return: Formatted zip code
    """
    try:
        if isinstance(zip_code, float):
            zip_code = int(zip_code)
        if isinstance(zip_code, str):
            zip_code = zip_code.replace(" ", "")
            zip_code = zip_code.split("-")[0]
        if 500 < int(zip_code) < 99951:
            zip_code = str(zip_code).zfill(5)
        return zip_code
    except ValueError:
        return False


@shared_task
def save_client_list(clients, company_id, task=None):
    """
    Saves a list of clients to the database.

    :param clients: List of clients
    :param company_id: ID of the company
    :param task: Task instance (optional)
    """
    bad_streets = [
        "none",
        "null",
        "na",
        "n/a",
        "tbd",
        ".",
        "unk",
        "unknown",
        "no address listed",
        "no address",
        "cmo",
    ]
    clients_to_add = []
    company = Company.objects.get(id=company_id)

    for i, client in enumerate(clients):
        try:
            is_service_titan = "active" in client

            if (
                is_service_titan and client["active"]
            ) or not is_service_titan:
                name = client["name"]
                if is_service_titan:
                    street = parse_streets(
                        client["address"]["street"].title()
                    )
                    zip_code = format_zip(client["address"]["zip"])
                    city = client["address"]["city"]
                    state = client["address"]["state"]
                else:
                    street = parse_streets(client["address"].title())
                    zip_code = format_zip(client["zip code"])
                    city = client["city"]
                    state = client["state"]

                if street.lower() in bad_streets or "tbd" in street.lower():
                    continue

                if int(zip_code) < 500 or int(zip_code) > 99951:
                    continue

                zip_code_obj = ZipCode.objects.get_or_create(
                    zip_code=str(zip_code)
                )[0]

                if is_service_titan:
                    clients_to_add.append(
                        Client(
                            address=street,
                            zip_code=zip_code_obj,
                            city=city,
                            state=state,
                            name=name,
                            company=company,
                            serv_titan_id=client["customerId"],
                        )
                    )
                else:
                    if i % 1000 == 0 and i != 0:
                        Client.objects.bulk_create(
                            clients_to_add, ignore_conflicts=True
                        )
                        clients_to_add = []

                    phone_number = (
                        sub("[^0-9]", "", client["phone number"])
                        if "phone number" in client
                        else ""
                    )
                    clients_to_add.append(
                        Client(
                            address=street,
                            zip_code=zip_code_obj,
                            city=city,
                            state=state,
                            name=name,
                            company=company,
                            phone_number=phone_number,
                        )
                    )
        except Exception as e:
            logging.error("create error")
            logging.error(e)

    Client.objects.bulk_create(clients_to_add, ignore_conflicts=True)

    # if task:
    #     delete_extra_clients.delay(company_id, task)
    #     do_it_all.delay(company_id)
    del clients_to_add, clients, company, company_id, bad_streets


@shared_task
def update_client_list(numbers):
    phone_numbers, clients = "", ""
    phone_numbers = {}
    for number in numbers:
        try:
            if number.get("phoneSettings") is not None:
                phone_numbers[number["customerId"]] = number[
                    "phoneSettings"
                ].get("phoneNumber")
        except Exception as e:
            logging.error(f"update error {e}")
            continue
    clients = Client.objects.filter(
        serv_titan_id__in=list(phone_numbers.keys())
    )
    for client in clients:
        client.phone_number = phone_numbers[client.serv_titan_id]
        client.save()
    del_variables([phone_numbers, clients, numbers])


@shared_task
def update_status(zip_code, company_id, status):
    """
    Update the status of listings based on the provided zip code and status.

    :param zip_code: The zip code of the listings to be updated.
    :param company_id: The ID of the company.
    :param status: The status to be set for the listings.
    """
    try:
        company = Company.objects.get(id=company_id)
        zip_code_object = ZipCode.objects.get(zip_code=zip_code)
    except Exception as e:
        logging.error(
            f"ERROR during updateStatus: {e} with zip_code {zip_code}"
        )
        return

    listed_addresses = HomeListing.objects.filter(
        zip_code=zip_code_object, status=status
    ).values("address")

    clients_to_update = Client.objects.filter(
        company=company,
        address__in=listed_addresses,
        zip_code=zip_code_object,
        active=True,
        error_flag=False,
    )

    previous_listed = Client.objects.filter(
        company=company,
        zip_code=zip_code_object,
        status=status,
        active=True,
        error_flag=False,
    )

    newly_listed = clients_to_update.difference(previous_listed)

    for to_list in newly_listed:
        existing_updates = ClientUpdate.objects.filter(
            client=to_list,
            status__in=["House For Sale", "House Recently Sold (6)"],
        )
        update = True
        try:
            for listing in existing_updates:
                if (
                    listing.listed
                    > HomeListing.objects.get(
                        address=to_list.address, status=status
                    ).listed
                ):
                    update = False
        except Exception as e:
            logging.error(e)

        if update:
            home_listing = HomeListing.objects.get(
                address=to_list.address, status=status
            )
            to_list.status = status
            to_list.price = home_listing.price
            to_list.year_built = home_listing.year_built
            to_list.housing_type = home_listing.housing_type
            to_list.save()
            to_list.tag.add(*home_listing.tag.all())

            zapier_url = (
                company.zapier_for_sale
                if status == "House For Sale"
                else company.zapier_sold
            )
            if zapier_url:
                try:
                    serializer = ZapierClientSerializer(to_list)
                    requests.post(
                        zapier_url, data=serializer.data, timeout=10
                    )
                except Exception as e:
                    logging.error(e)

        try:
            listing = HomeListing.objects.filter(
                zip_code=zip_code_object,
                address=to_list.address,
                status=status,
            )
            ClientUpdate.objects.get_or_create(
                client=to_list, status=status, listed=listing[0].listed
            )
        except Exception as e:
            logging.error(f"Cant find listing to list {e}")
            logging.error("This should not be the case")

    clients_to_update = [
        client
        for client in clients_to_update.values_list(
            "serv_titan_id", flat=True
        )
        if client
    ]

    if clients_to_update:
        update_service_titan_client_tags.delay(
            clients_to_update, company.id, status
        )


@shared_task
def update_clients_statuses(company_id=None):
    """
    Update the statuses of clients in all companies or a specific company.

    :param company_id: The ID of the specific company.
    If None, update for all companies.
    """
    try:
        companies = (
            Company.objects.filter(id=company_id)
            if company_id
            else Company.objects.all()
        )

        for company in companies:
            if company.product.id != "price_1MhxfPAkLES5P4qQbu8O45xy":
                zip_codes = (
                    Client.objects.filter(company=company, active=True)
                    .values("zip_code")
                    .distinct()
                    .order_by("zip_code")
                )

                for zip_code in zip_codes:
                    update_status.delay(
                        zip_code["zip_code"], company.id, "House For Sale"
                    )
                    update_status.delay(
                        zip_code["zip_code"],
                        company.id,
                        "House Recently Sold (6)",
                    )

    except Exception as e:
        logging.error(
            f"""ERROR during update_clients_statuses: {e} with company {company}"""
        )
        logging.error(traceback.format_exc())


@shared_task
def send_daily_email(company_id=None):
    (
        companies,
        company,
        emails,
        subject,
        for_sale_customers,
        sold_customers,
        message,
        email,
        msg,
    ) = ("", "", "", "", "", "", "", "", "")
    if company_id:
        companies = Company.objects.filter(id=company_id)
    else:
        companies = Company.objects.all()
    for company in companies:
        try:
            if company.product.id != "price_1MhxfPAkLES5P4qQbu8O45xy":
                emails = list(
                    CustomUser.objects.filter(company=company).values_list(
                        "email"
                    )
                )
                subject = "Did Your Customers Move?"

                for_sale_customers = (
                    Client.objects.filter(
                        company=company, status="House For Sale", active=True
                    )
                    .exclude(contacted=True)
                    .count()
                )
                sold_customers = (
                    Client.objects.filter(
                        company=company,
                        status="House Recently Sold (6)",
                        active=True,
                    )
                    .exclude(contacted=True)
                    .count()
                )
                message = get_template("dailyEmail.html").render(
                    {"forSale": for_sale_customers, "sold": sold_customers}
                )

                if for_sale_customers > 0 or sold_customers > 0:
                    for email in emails:
                        email = email[0]
                        msg = EmailMessage(
                            subject,
                            message,
                            settings.EMAIL_HOST_USER,
                            [email],
                        )
                        msg.content_subtype = "html"
                        msg.send()
        except Exception as e:
            logging.error(
                f"ERROR during send_daily_email: {e} with company {company}"
            )
            logging.error(traceback.format_exc())
    # if not company_id:
    #     HomeListing.objects.all().delete()
    ZipCode.objects.filter(
        lastUpdated__lt=datetime.today() - timedelta(days=3)
    ).delete()
    del_variables(
        [
            companies,
            company,
            emails,
            subject,
            for_sale_customers,
            sold_customers,
            message,
            email,
            msg,
        ]
    )


@shared_task
def auto_update(company_id=None, zip=None):
    from .realtor import get_all_zipcodes

    company = ""
    if company_id:
        try:
            company = Company.objects.get(id=company_id)
            get_all_zipcodes(company_id)

        except Exception as e:
            logging.error(f"Company does not exist {e}")
            return
        del_variables([company_id, company])
    elif zip:
        try:
            ZipCode.objects.get_or_create(zip_code=zip)
            get_all_zipcodes("", zip=zip)
        except Exception as e:
            logging.error(f"Zip does not exist {e}")
            return
    else:
        company, companies = "", ""
        companies = Company.objects.all()
        for company in companies:
            try:
                if company.product.id != "price_1MhxfPAkLES5P4qQbu8O45xy":
                    get_all_zipcodes(company.id)
                else:
                    logging.error("free tier")
            except Exception as e:
                logging.error(f"Auto Update Error: {e}")
                logging.error(
                    f"Auto Update: {company.product} {company.name}"
                )
        del_variables([company, companies])


def get_service_titan_access_token(company):
    company = Company.objects.get(id=company)
    if company.service_titan_app_version == 2:
        app_key = settings.ST_APP_KEY_2
    else:
        app_key = settings.ST_APP_KEY

    url = "https://auth.servicetitan.io/connect/token"

    payload = (
        f"grant_type=client_credentials&"
        f"client_id={company.client_id}&client_secret={company.client_secret}"
    )
    headers = {
        "ST-App-Key": app_key,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post(url, headers=headers, data=payload, timeout=5)
    response_data = response.json()
    access_token = response_data["access_token"]
    header = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "ST-App-Key": app_key,
    }

    return header


def process_client_tags(client_id):
    """
    Process tag removal for the given client.

    Parameters:
    client_id (str): ID of the client.
    """
    try:
        client = CustomUser.objects.get(id=client_id)
        headers = get_service_titan_access_token(client.company.id)
        company = client.company
        tag_ids = [
            str(company.service_titan_for_sale_tag_id),
            str(company.service_titan_recently_sold_tag_id),
            str(company.service_titan_for_sale_contacted_tag_id),
            str(company.service_titan_recently_sold_contacted_tag_id),
        ]
        tag_ids = [tag_id for tag_id in tag_ids if tag_id]

        for tag_id in tag_ids:
            payload = {
                "customerIds": [str(client.serv_titan_id)],
                "tagTypeIds": [tag_id],
            }
            handle_tag_deletion_request(payload, headers, client.company)

    except Exception as e:
        logging.error(e)


def determine_tag_type(company, status):
    """
    Determine the tag type based on the status.

    Parameters:
    company (object): Company object.
    status (str): Status of the property.

    Returns:
    list: List containing the tag type.
    """
    if status == "House For Sale":
        return [str(company.service_titan_for_sale_tag_id)]
    elif status == "House Recently Sold (6)":
        return [str(company.service_titan_recently_sold_tag_id)]


def handle_tag_deletion_request(
    payload, headers, company, client_subset=None
):
    """
    Send a tag deletion request to Service Titan API.

    Parameters:
    payload (dict): Payload for the request.
    headers (dict): Headers for the request.
    company (object): Company object.
    client_subset (list, optional): Subset of client IDs.

    Returns:
    response (object): Response from the Service Titan API.
    """
    base_url = "https://api.servicetitan.io/"
    response = requests.delete(
        f"{base_url}crm/v2/tenant/{str(company.tenant_id)}/tags",
        headers=headers,
        json=payload,
        timeout=10,
    )
    if response.status_code != 200:
        resp = response.json()
        error = (
            resp["title"]
            .replace("(", "")
            .replace(")", "")
            .replace(",", "")
            .replace(".", "")
            .split()
        )

        for word in error:
            if (
                word.isdigit()
                and client_subset
                and int(word) in client_subset
            ):
                client_subset.remove(int(word))

        if client_subset:
            payload = {
                "customerIds": client_subset,
                "tagTypeIds": payload["tagTypeIds"],
            }
            response = requests.delete(
                f"{base_url}crm/v2/tenant/{str(company.tenant_id)}/tags",
                headers=headers,
                json=payload,
                timeout=10,
            )

    return response


def handle_tag_addition_request(payload, headers, company, for_sale):
    """
    Send a tag addition request to Service Titan API.

    Parameters:
    payload (dict): Payload for the request.
    headers (dict): Headers for the request.
    company (object): Company object.
    for_sale (list): List of client IDs for sale.

    Returns:
    response (object): Response from the Service Titan API.
    """
    base_url = "https://api.servicetitan.io/"
    response = requests.put(
        f"{base_url}crm/v2/tenant/{str(company.tenant_id)}/tags",
        headers=headers,
        json=payload,
        timeout=10,
    )
    if response.status_code != 200:
        resp = response.json()
        error = (
            resp["title"]
            .replace("(", "")
            .replace(")", "")
            .replace(",", "")
            .replace(".", "")
            .split()
        )

        for word in error:
            if word.isdigit() and int(word) in for_sale:
                for_sale.remove(int(word))

        if for_sale:
            payload = {
                "customerIds": for_sale,
                "tagTypeIds": payload["tagTypeIds"],
            }
            response = requests.put(
                f"{base_url}crm/v2/tenant/{str(company.tenant_id)}/tags",
                headers=headers,
                json=payload,
                timeout=10,
            )

    return response


def cleanup_variables(variable_list):
    """
    Clean up variables by deleting them.

    Parameters:
    variable_list (list): List of variables to delete.
    """
    for var in variable_list:
        del var


@shared_task
def update_service_titan_client_tags(for_sale, company, status):
    """
    Update Service Titan client tags.

    Parameters:
    for_sale (list): List of IDs of clients for sale.
    company (str): ID of the company.
    status (str): Status of the property.
    """
    try:
        company = Company.objects.get(id=company)
        tag_ids = [
            company.service_titan_for_sale_tag_id,
            company.service_titan_recently_sold_tag_id,
        ]
        tag_ids = [str(tag_id) for tag_id in tag_ids if tag_id]
        headers = get_service_titan_access_token(company.id)
        if for_sale and tag_ids:
            tag_type = determine_tag_type(company, status)

            if status == "House Recently Sold (6)":
                for_sale_to_remove = for_sale
                payload = {
                    "customerIds": for_sale_to_remove,
                    "tagTypeIds": [
                        str(company.service_titan_for_sale_tag_id)
                    ],
                }
                response = handle_tag_deletion_request(
                    payload, headers, company, for_sale_to_remove
                )

                if response and response.status_code != 200:
                    logging.error(response.json())

            payload = {"customerIds": for_sale, "tagTypeIds": tag_type}
            response = handle_tag_addition_request(
                payload, headers, company, for_sale
            )

            if response and response.status_code != 200:
                logging.error(response.json())

    except Exception as e:
        logging.error("Updating Service Titan clients failed")
        logging.error(f"ERROR: {e}")
        logging.error(traceback.format_exc())

    cleanup_variables(
        [
            headers,
            response,
            payload,
            company,
            status,
            tag_type,
            for_sale,
        ]
    )


@shared_task
def add_service_titan_contacted_tag(client, tagId):
    client = Client.objects.get(id=client)
    headers = get_service_titan_access_token(client.company.id)
    payload = {
        "customerIds": [str(client.serv_titan_id)],
        "tagTypeIds": [str(tagId)],
    }
    requests.put(
        url=(
            f"https://api.servicetitan.io/crm/v2/tenant/"
            f"{str(client.company.tenant_id)}/tags"
        ),
        headers=headers,
        json=payload,
        timeout=10,
    )


@shared_task
def remove_all_service_titan_tags(company=None, client=None):
    """
    Remove all Service Titan tags for the provided company or client.

    Parameters:
    company (str, optional): ID of the company.
    client (str, optional): ID of the client.
    """
    if company:
        try:
            company = Company.objects.get(id=company)
            tag_ids = [
                company.service_titan_for_sale_tag_id,
                company.service_titan_recently_sold_tag_id,
            ]
            tag_ids = [str(tag_id) for tag_id in tag_ids if tag_id]

            if tag_ids:
                headers = get_service_titan_access_token(company.id)
                time_limit = datetime.now()

                for tag_id in tag_ids:
                    # get a list of all the serv_titan_ids
                    # for the clients with one from this company
                    clients = list(
                        Client.objects.filter(company=company)
                        .exclude(serv_titan_id=None)
                        .values_list("serv_titan_id", flat=True)
                    )
                    num_iterations = (len(clients) // 250) + 1

                    for i in range(num_iterations):
                        if time_limit < datetime.now() - timedelta(
                            minutes=15
                        ):
                            headers = get_service_titan_access_token(
                                company.id
                            )
                            time_limit = datetime.now()

                        client_subset = clients[
                            i * 250 : (i + 1) * 250  # noqa: E203
                        ]
                        payload = {
                            "customerIds": client_subset,
                            "tagTypeIds": [tag_id],
                        }
                        response = handle_tag_deletion_request(
                            payload, headers, company, client_subset
                        )

                        if response and response.status_code != 200:
                            logging.error(response.json())

                Client.objects.filter(company=company).update(
                    status="No Change"
                )

        except Exception as e:
            logging.error("Updating Service Titan clients failed")
            logging.error(f"ERROR: {e}")
            logging.error(traceback.format_exc())

    if client:
        process_client_tags(client)


def update_service_titan_tasks(clients, company, status):
    headers, data, response = "", "", ""
    if clients and (
        company.service_titan_for_sale_tag_id
        or company.service_titan_recently_sold_tag_id
    ):
        try:
            headers = get_service_titan_access_token(company.id)
            response = requests.get(
                url=(
                    f"https://api.servicetitan.io/taskmanagement/"
                    f"v2/tenant/{str(company.tenant_id)}/data"
                ),
                headers=headers,
                timeout=10,
            )
            with open("tasks.json", "w") as f:
                json.dump(response.json(), f)
            # if response.status_code != 200:
            #     resp = response.json()
            #     error = resp["errors"][""][0]
            #     error = (
            #         error.replace("(", "")
            #         .replace(")", "")
            #         .replace(",", " ")
            #         .replace(".", "")
            #         .split()
            #     )
            #     for word in error:
            #         if word.isdigit():
            #             Client.objects.filter(serv_titan_id=word).delete()
            #             forSale.remove(word)
            #     payload = {
            #         "customerIds": forSale,
            #         "taskTypeId": str(company.service_titanTaskID),
            #     }
            #     response = requests.put(
            #         f"https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tasks",
            #         headers=headers,
            #         json=payload,
            #     )
        except Exception as e:
            logging.error("updating service titan tasks failed")
            logging.error(f"ERROR: {e}")
            logging.error(traceback.format_exc())
    del_variables([headers, data, response, company, status])


# send email to every customuser with the html
# file that has the same name as the template
def send_update_email(templateName):
    try:
        users = list(
            CustomUser.objects.filter(is_verified=True).values_list(
                "email", flat=True
            )
        )
        mail_subject = "Is My Customer Moving Product Updates"
        messagePlain = """Thank you for signing up for Is My Customer Moving.
          We have some updates for you. Please visit
          https://app.ismycustomermoving.com/ to see them."""
        message = get_template(f"{templateName}.html").render()
        for user in users:
            send_mail(
                subject=mail_subject,
                message=messagePlain,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user],
                html_message=message,
                fail_silently=False,
            )
    except Exception as e:
        logging.error("sending update email failed")
        logging.error(f"ERROR: {e}")
        logging.error(traceback.format_exc())


@shared_task(rate_limit="1/s")
def do_it_all(company):
    try:
        company = Company.objects.get(id=company)
        result = auto_update.delay(
            company_id=company.id
        )  # Schedule auto_update task
        sleep(3600)  # TODO Calculate ETA for update_clients_statuses task
        result = update_clients_statuses(
            company.id
        )  # Schedule update_clients_statuses task
        sleep(360)
        result.then(send_daily_email.apply_async, args=[company.id])
    except Exception as e:
        logging.error("doItAll failed")
        logging.error(f"ERROR: {e}")
        logging.error(traceback.format_exc())


def filter_home_listings(query_params, queryset, company_id, filter_type):
    """
    Filter all home listings based on the provided query parameters.

    Parameters:
    query_params (dict): Parameters to filter the queryset.
    queryset (QuerySet): QuerySet to be filtered.
    company_id (str): ID of the company.

    Returns:
    queryset: Filtered QuerySet.
    """
    company = Company.objects.get(id=company_id)

    if "saved_filter" in query_params:
        query_params = SavedFilter.objects.get(
            name=query_params["saved_filter"],
            company=company,
            filter_type=filter_type,
        ).saved_filters
        query_params = json.loads(query_params)
        query_params = {k: v for k, v in query_params.items() if v != ""}
        if "tags" in query_params:
            query_params["tags"] = "".join(query_params["tags"])

    for param in query_params:
        if param == "min_price":
            queryset = queryset.filter(price__gte=query_params[param])
        elif param == "max_price":
            queryset = queryset.filter(price__lte=query_params[param])
        elif param == "min_year":
            queryset = queryset.filter(year_built__gte=query_params[param])
        elif param == "max_year":
            queryset = queryset.filter(year_built__lte=query_params[param])
        elif param == "min_beds":
            queryset = queryset.filter(bedrooms__gte=query_params[param])
        elif param == "max_beds":
            queryset = queryset.filter(bedrooms__lte=query_params[param])
        elif param == "min_baths":
            queryset = queryset.filter(bathrooms__gte=query_params[param])
        elif param == "max_baths":
            queryset = queryset.filter(bathrooms__lte=query_params[param])
        elif param == "min_sqft":
            queryset = queryset.filter(sqft__gte=query_params[param])
        elif param == "max_sqft":
            queryset = queryset.filter(sqft__lte=query_params[param])
        elif param == "min_lot_sqft":
            queryset = queryset.filter(lot_sqft__gte=query_params[param])
        elif param == "max_lot_sqft":
            queryset = queryset.filter(lot_sqft__lte=query_params[param])
        elif param in ["min_days_ago", "max_days_ago"]:
            filter_key = (
                "listed__lte" if param == "min_days_ago" else "listed__gte"
            )
            queryset = queryset.filter(
                **{
                    filter_key: (
                        datetime.today()
                        - timedelta(days=int(query_params[param]))
                    ).strftime("%Y-%m-%d")
                }
            )

        elif param == "tags":
            try:
                tags = query_params[param].split(",")
                if tags[0]:
                    matching_tags = HomeListingTags.objects.filter(
                        tag__in=tags
                    )
                    queryset = queryset.filter(tag__in=matching_tags)
            except Exception as e:
                logging.error(e)
        elif param in ["state", "city"]:
            filter_key = f"{param}__iexact"
            queryset = queryset.filter(**{filter_key: query_params[param]})
        elif param == "zip_code":
            zip_code = ZipCode.objects.filter(zip_code=query_params[param])
            if zip_code.exists():
                queryset = queryset.filter(zip_code=zip_code.first())
    return queryset


def filter_clients(query_params, queryset, company_id):
    """
    Filter clients based on the provided query parameters.

    Parameters:
    query_params (dict): Parameters to filter the queryset.
    queryset (QuerySet): QuerySet to be filtered.

    Returns:
    queryset: Filtered QuerySet.
    """
    company = Company.objects.get(id=company_id)
    if "saved_filter" in query_params:
        query_params = SavedFilter.objects.get(
            name=query_params["saved_filter"],
            company=company,
            filter_type="Client",
        ).saved_filters
        query_params = json.loads(query_params)
        query_params = {k: v for k, v in query_params.items() if v != ""}
        if "tags" in query_params:
            query_params["tags"] = "".join(query_params["tags"])

    for param in query_params:
        if param == "min_price":
            queryset = queryset.filter(price__gte=query_params[param])
        elif param == "max_price":
            queryset = queryset.filter(price__lte=query_params[param])
        elif param == "min_year":
            queryset = queryset.filter(year_built__gte=query_params[param])
        elif param == "max_year":
            queryset = queryset.filter(year_built__lte=query_params[param])
        elif param == "min_beds":
            queryset = queryset.filter(bedrooms__gte=query_params[param])
        elif param == "max_beds":
            queryset = queryset.filter(bedrooms__lte=query_params[param])
        elif param == "min_baths":
            queryset = queryset.filter(bathrooms__gte=query_params[param])
        elif param == "max_baths":
            queryset = queryset.filter(bathrooms__lte=query_params[param])
        elif param == "min_sqft":
            queryset = queryset.filter(sqft__gte=query_params[param])
        elif param == "max_sqft":
            queryset = queryset.filter(sqft__lte=query_params[param])
        elif param == "min_lot_sqft":
            queryset = queryset.filter(lot_sqft__gte=query_params[param])
        elif param == "max_lot_sqft":
            queryset = queryset.filter(lot_sqft__lte=query_params[param])
        elif param == "equip_install_date_min":
            queryset = queryset.filter(
                equipment_installed_date__gte=query_params[param]
            )
        elif param == "equip_install_date_max":
            queryset = queryset.filter(
                equipment_installed_date__lte=query_params[param]
            )
        elif param in ["state", "city"]:
            filter_key = f"{param}__iexact"
            queryset = queryset.filter(**{filter_key: query_params[param]})
        elif param == "zip_code":
            zip_code = ZipCode.objects.filter(zip_code=query_params[param])
            if zip_code.exists():
                queryset = queryset.filter(zip_code=zip_code.first())
        elif param == "tags":
            tags = query_params[param].split(",")
            matching_tags = HomeListingTags.objects.filter(tag__in=tags)
            queryset = queryset.filter(tag__in=matching_tags)
        elif param == "status":
            statuses = []
            if "For Sale" in query_params[param]:
                statuses.append("House For Sale")
            if "Recently Sold" in query_params[param]:
                statuses.append("House Recently Sold (6)")
            if "Off Market" in query_params[param]:
                statuses.append("No Change")
            queryset = queryset.filter(status__in=statuses)
        elif param in ["customer_since_min", "customer_since_max"]:
            filter_key = (
                "service_titan_customer_since__gte"
                if param.endswith("min")
                else "service_titan_customer_since__lte"
            )
            date_value = (
                date(int(query_params[param]), 1, 1)
                if param.endswith("min")
                else date(int(query_params[param]), 12, 31)
            )
            queryset = queryset.filter(**{filter_key: date_value})

    return queryset


@shared_task
def remove_error_flag():
    old_enough_updates = ClientUpdate.objects.filter(
        error_flag=True, date__lt=datetime.today() - timedelta(days=180)
    )
    for update in old_enough_updates:
        client = update.client
        client.error_flag = False
        client.save()


@shared_task
def verify_address(client_id):
    """
    Verify the client's address using USPS API.

    Parameters:
    client_id (str): The ID of the client.

    Returns:
    None
    """
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        logging.error(f"Client with id {client_id} does not exist.")
        return

    zip_code = client.zip_code.zip_code
    base_url = "http://production.shippingapis.com/ShippingAPI.dll"
    user_id = settings.USPS_USER_ID
    api = "Verify"

    xml_request = f"""
    <AddressValidateRequest USERID="{user_id}">
        <Address ID="1">
            <Address1></Address1>
            <Address2>{client.address}</Address2>
            <City>{client.city}</City>
            <State>{client.state}</State>
            <Zip5>{zip_code}</Zip5>
            <Zip4/>
        </Address>
    </AddressValidateRequest>
    """

    params = {"API": api, "XML": xml_request}

    try:
        response = requests.get(base_url, params=params, timeout=10)
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return

    response_xml = response.text
    parsed_response = fromstring(response_xml)
    address_element = parsed_response.find("Address")
    error = address_element.find("Error")

    if error:
        usps_address = "Error"
    else:
        address2 = address_element.find("Address2").text.title()
        city = address_element.find("City").text.title()
        state = address_element.find("State").text
        zip5 = address_element.find("Zip5").text
        if (
            address2 != client.address
            or state != client.state
            or zip5 != zip_code
        ):
            client.usps_different = True
        usps_address = f"{address2}, {city}, {state} {zip5}"

    client.usps_address = usps_address
    client.save()


@shared_task
def send_zapier_recently_sold(company_id):
    """
    Send information about recently sold homes to Zapier for a given company.

    Parameters:
    company_id (str): The ID of the company.

    Returns:
    None
    """
    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        logging.error(f"Company with id {company_id} does not exist.")
        return

    if not company.zapier_recently_sold:
        return

    zip_code_objects = Client.objects.filter(company=company).values(
        "zip_code"
    )
    recently_listed_date = (datetime.today() - timedelta(days=7)).strftime(
        "%Y-%m-%d"
    )
    home_listings = HomeListing.objects.filter(
        zip_code__in=zip_code_objects, listed__gt=recently_listed_date
    ).order_by("listed")

    saved_filters = SavedFilter.objects.filter(
        company=company, filter_type="Recently Sold", for_zapier=True
    )

    for saved_filter in saved_filters:
        query_params = {
            k: v
            for k, v in json.loads(saved_filter.saved_filters).items()
            if v != ""
        }
        filtered_home_listings = filter_home_listings(
            query_params, home_listings, company_id, "Recently Sold"
        )

        if filtered_home_listings:
            try:
                serialized_data = HomeListingSerializer(
                    filtered_home_listings, many=True
                ).data
                for (
                    data
                ) in (
                    serialized_data
                ):  # Add saved_filter.name to each item in the list
                    data["filter_name"] = saved_filter.name

                requests.post(
                    company.zapier_recently_sold,
                    data=serialized_data,
                    timeout=10,
                )
            except Exception as e:
                logging.error(e)
