from celery import shared_task
import requests
import logging
from time import sleep

from datetime import datetime, date, timedelta
from django.db.models.functions import Coalesce
from django.db.models import Q
from django.db import transaction

from accounts.models import Company
from ..models import Client, ClientUpdate, ServiceTitanJob
from ..utils import (
    auto_update,
    save_client_list,
    delete_extra_clients,
    del_variables,
    get_service_titan_access_token,
    verify_address,
    parse_streets
)
from payments.models import CRMInvoice


@shared_task
def complete_service_titan_sync(company_id, task_id, option=None, automated=False):
    company = Company.objects.get(id=company_id)
    tenant = company.tenant_id
    if option is None:
        option = company.service_titan_customer_sync_option
    else:
        company.service_titan_customer_sync_option = option
        company.save()

    get_service_titan_locations(company_id, tenant, option)

    delete_extra_clients.delay(company_id, task_id)

    get_service_titan_equipment.delay(company_id, tenant)

    if option == "option1":
        get_service_titan_customers.delay(company_id, tenant)

    get_service_titan_invoices.delay(company_id, tenant)

    clients_to_verify = list(Client.objects.filter(
        company=company, old_address=None
    ).values_list("id", flat=True))
    verify_address.delay(clients_to_verify)
    del_variables([company, clients_to_verify])
    if not automated:
        auto_update.delay(company_id=company_id)


def get_service_titan_locations(company_id, tenant, option):
    # Retrieve the access token for ServiceTitan API
    headers = get_service_titan_access_token(company_id)
    clients = []
    moreClients = True
    page = 1

    # Fetch client data in paginated requests
    results = []
    while moreClients:
        response = requests.get(
            url=(
                f"https://api.servicetitan.io/crm/v2/tenant/"
                f"{tenant}/locations?page={page}&pageSize=2500"
            ),
            headers=headers,
            timeout=10,
        )
        page += 1
        clients = response.json()["data"]
        if not response.json()["hasMore"]:
            moreClients = False

        if option == "option3":
            # Modify client names if option3 is selected
            for client in clients:
                client["name"] = " "

        results.append(save_client_list.delay(clients, company_id))

    count = 0
    while any(not result.ready() for result in results) and count < 30:
        sleep(1)
        count += 1

    # Clean up variables to free up memory
    del_variables([clients, response, headers])


@shared_task
def update_sold_listed_date_on_location(
        headers, company_id, customer_id, status, listed_date):
    company = Company.objects.get(id=company_id)
    client = Client.objects.get(company=company, serv_titan_id=customer_id)
    response = requests.get(
        url=(
            f"https://api.servicetitan.io/crm/v2/tenant/"
            f"{company.tenant_id}/locations?customerId={customer_id}"
        ),
        headers=headers,
        timeout=10,
    )
    locations = response.json()["data"]
    for location in locations:
        if parse_streets(location["address"]["street"]) == client.address:
            location_id = location["id"]
            custom_fields = location["customFields"]
            new_custom_fields = []
            existed = False
            # Add all current custom fields to new_custom_fields,
            # if field to update exists, update it
            for field in custom_fields:
                if field["typeId"] == \
                    company.service_titan_sold_date_custom_field_id \
                        and status == "House Recently Sold (6)":
                    new_custom_fields.append(
                        {"value": listed_date, "typeId": field["typeId"]}
                    )
                    existed = True
                elif field["typeId"] == \
                    company.service_titan_listed_date_custom_field_id \
                        and status == "House For Sale":
                    new_custom_fields.append(
                        {"value": listed_date, "typeId": field["typeId"]}
                    )
                    existed = True
                else:
                    new_custom_fields.append(
                        {"value": field["value"], "typeId": field["typeId"]}
                    )
            # If field to update does not exist, add it to new_custom_fields
            if not existed:
                if status == "House Recently Sold (6)":
                    typeId = company.service_titan_sold_date_custom_field_id
                else:
                    typeId = company.service_titan_listed_date_custom_field_id
                new_custom_fields.append(
                    {"value": listed_date, "typeId": typeId}
                )
            response = requests.patch(
                url=(
                    f"https://api.servicetitan.io/crm/v2/tenant/"
                    f"{company.tenant_id}/locations/{location_id}"
                ),
                headers=headers,
                json={"customFields": new_custom_fields},
                timeout=10,
            )


# def get_service_titan_jobs(company_id, tenant, option):
#     # Retrieve the access token for ServiceTitan API
#     headers = get_service_titan_access_token(company_id)
#     clients = []
#     moreClients = True
#     page = 1

#     # Fetch client data in paginated requests
#     results = []
#     while moreClients:
#         response = requests.get(
#             url=(
#                 f"https://api.servicetitan.io/crm/v2/tenant/"
#                 f"{tenant}/locations?page={page}&pageSize=2500"
#             ),
#             headers=headers,
#             timeout=10,
#         )
#         page += 1
#         clients = response.json()["data"]
#         if not response.json()["hasMore"]:
#             moreClients = False

#         if option == "option3":
#             # Modify client names if option3 is selected
#             for client in clients:
#                 client["name"] = " "

#         results.append(save_client_list.delay(clients, company_id))

#     count = 0
#     while any(not result.ready() for result in results) and count < 30:
#         sleep(1)
#         count += 1

#     # Clean up variables to free up memory
#     del_variables([clients, response, headers])


@shared_task
def get_service_titan_equipment(company_id, tenant):
    headers = get_service_titan_access_token(company_id)
    more_equipment = True
    # get client data
    page = 1
    while more_equipment:

        response = requests.get(
            url=(
                f"https://api.servicetitan.io/equipmentsystems"
                f"/v2/tenant/{tenant}/installed-equipment"
                f"?page={page}&pageSize=2500"
            ),
            headers=headers,
            timeout=10,
        )
        page += 1
        equipment = response.json()["data"]
        if not response.json()["hasMore"]:
            more_equipment = False

        update_clients_with_last_day_of_equipment_installation.delay(
            company_id, equipment)
    del_variables([equipment, response, headers])


@shared_task
def update_clients_with_last_day_of_equipment_installation(company_id, equipment):
    # Retrieve the company based on the company_id
    company = Company.objects.get(id=company_id)
    client_dict = {}

    # Iterate through the equipment list
    for equip in equipment:
        if equip["installedOn"] is not None:
            try:
                # Parse the installation date from the equipment data
                client_dict[equip["customerId"]] = datetime.strptime(
                    equip["installedOn"][:10], "%Y-%m-%d"
                ).date()
            except Exception as e:
                logging.error(e)

    # Retrieve the client IDs from the client_dict
    client_ids = client_dict.keys()

    # Fetch clients associated with the given company and matching the client IDs
    clients = Client.objects.filter(
        serv_titan_id__in=client_ids, company=company)
    # clients.update(
    #     equipment_installed_date=F("client_dict__serv_titan_id") or F(
    #         "equipment_installed_date")
    # )
    # Update the equipment_installed_date for each client
    for client in clients:
        client.equipment_installed_date = Coalesce(
            client_dict.get(client.serv_titan_id),
            client.equipment_installed_date,
        )
        client.save(update_fields=["equipment_installed_date"])

    # Clean up variables to free up memory
    del_variables([company, equipment, client_dict, client_ids, clients])


@shared_task
def get_service_titan_customers(company_id, tenant):
    company = Company.objects.get(id=company_id)
    clients = Client.objects.filter(
        Q(phone_number=None) | Q(email=None),
        company=company,
    ).exclude(
        serv_titan_id=None
    )
    count = 0
    for client in clients:
        if count % 1500 == 0:
            headers = get_service_titan_access_token(company_id)
        count += 1
        try:
            response = requests.get(
                url=(
                    f"https://api.servicetitan.io/crm/v2/tenant/"
                    f"{tenant}/customers/{client.serv_titan_id}/contacts"
                ),
                headers=headers,
                timeout=10,
            )

            if response.status_code == 200:
                contact_info = response.json()["data"]
                found_phone = False
                for info in contact_info:
                    if info["type"] == "MobilePhone" and found_phone is False:
                        client.phone_number = info["value"]
                        found_phone = True
                    elif info["type"] == "Email":
                        client.email = info["value"]
                client.save()
        except Exception as e:
            logging.error(f"ERROR: {e}")
    del_variables([clients, response, headers])


@shared_task
def get_service_titan_invoices(company_id, tenant):
    headers = get_service_titan_access_token(company_id)
    more_invoices = True
    page = 1
    results = []

    company = Company.objects.get(id=company_id)
    all_clients = Client.objects.filter(company=company)

    if CRMInvoice.objects.filter(client__in=all_clients).exists():
        rfc339 = (datetime.now()-timedelta(days=365)
                  ).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        rfc_url_param = f"&createdOnOrAfter={rfc339}"
    else:
        rfc_url_param = ""
    while more_invoices:
        invoices = []
        url = (
            f"https://api.servicetitan.io/accounting"
            f"/v2/tenant/{tenant}/invoices?page={page}"
            f"&pageSize=1000{rfc_url_param}"
        )
        response = requests.get(url=url, headers=headers, timeout=15)
        page += 1
        for invoice in response.json()["data"]:
            try:
                if invoice["createdOn"] is not None and "customer" in invoice:
                    if float(invoice["total"]) == 0:
                        continue
                    invoices.append(
                        {
                            "id": invoice["id"],
                            "customer": invoice["customer"]["id"],
                            "createdOn": invoice["createdOn"][:10],
                            "amount": invoice["total"],
                        }
                    )
            except Exception as e:
                logging.error(e)
        results.append(save_invoices.delay(
            company_id, invoices))
        if not response.json()["hasMore"]:
            more_invoices = False
    count = 0
    while any(not result.ready() for result in results) and count < 30:
        sleep(1)
        count += 1
    get_customer_since_data_from_invoices.delay(company_id)
    del_variables([headers, response, invoices, results])


@shared_task
def save_invoices(company_id, invoices):
    # TODO: This function takes 60-70 seconds to run. Need to optimize it.
    # Retrieve the company based on the company_id
    company = Company.objects.get(id=company_id)

    all_clients = Client.objects.filter(company=company)
    client_lookup = {client.serv_titan_id: client for client in all_clients}

    existing_invoice_ids = set(
        CRMInvoice.objects.values_list('invoice_id', flat=True))
    invoices_to_create = []
    # invoices_to_update = []
    count = 0
    for invoice in invoices:
        count += 1
        client_id = invoice["customer"]
        client = client_lookup.get(client_id)
        if client is None:
            continue
        if len(invoices_to_create) > 500:
            CRMInvoice.objects.bulk_create(invoices_to_create)
            invoices_to_create = []
        # Parse the createdOn date from the invoice data
        created_on = datetime.strptime(invoice["createdOn"], "%Y-%m-%d").date()
        if str(invoice["id"]) not in existing_invoice_ids:
            last_status_update_date = ClientUpdate.objects.filter(
                client=client,
                status__in=["House For Sale", "House Recently Sold (6)"]
            ).values_list("date", flat=True).order_by("-date").first()
            attributed = False
            if last_status_update_date:
                if (
                    (client.service_titan_customer_since is None or
                        client.service_titan_customer_since <
                     date.today() - timedelta(days=180)) and
                    client.status in [
                        "House For Sale",
                        "House Recently Sold (6)"] and
                    created_on < last_status_update_date + timedelta(days=365) and
                    created_on >= last_status_update_date
                ):
                    attributed = True
            invoices_to_create.append(
                CRMInvoice(
                    invoice_id=invoice["id"],
                    amount=invoice["amount"],
                    client=client,
                    created_on=created_on,
                    attributed=attributed,
                    existing_client=False,  # This is always False?
                )
            )
        # else:
        #     invoice_obj = CRMInvoice.objects.get(
        #         invoice_id=invoice["id"])
        #     if invoice['amount'] != invoice_obj.amount:
        #         invoice_obj.amount = invoice['amount']
        #         invoices_to_update.append(invoice_obj)

    # Bulk operations
    if invoices_to_create:
        CRMInvoice.objects.bulk_create(invoices_to_create)
    # if invoices_to_update:
    #     CRMInvoice.objects.bulk_update(invoices_to_update, ['amount'])

    # Clean up variables to free up memory
    del_variables([company, invoices_to_create])


@shared_task
def get_customer_since_data_from_invoices(company_id):
    company = Company.objects.get(id=company_id)
    clients = Client.objects.filter(
        company=company
    )
    for client in clients:
        invoices = CRMInvoice.objects.filter(
            client=client
        ).order_by("created_on")

        if len(invoices) > 0:
            client.service_titan_customer_since = invoices[0].created_on
            lifetime_revenue = 0
            for invoice in invoices:
                lifetime_revenue += invoice.amount
            client.service_titan_lifetime_revenue = lifetime_revenue
            client.save(update_fields=[
                        "service_titan_customer_since",
                        "service_titan_lifetime_revenue"
                        ])
    del_variables([clients, company, invoices])


def get_service_titan_job_types(headers, tenant):
    url = (
        f"https://api.servicetitan.io/jpm/v2"
        f"/tenant/{tenant}/job-types?pageSize=1000"
    )
    response = requests.get(url=url, headers=headers, timeout=10)
    data = response.json()["data"]
    job_types = {}
    for job_type in data:
        job_types[job_type["id"]] = job_type["name"]
    del_variables([headers, response, data])
    return job_types


@shared_task
def get_service_titan_jobs(company_id, tenant):
    headers = get_service_titan_access_token(company_id)
    job_types = get_service_titan_job_types(headers, tenant)
    more_jobs = True
    page = 1

    while more_jobs:
        jobs = []
        url = (
            f"https://api.servicetitan.io/jpm/v2/tenant/"
            f"{tenant}/job-types?pageSize=1000&page={page}"
        )
        response = requests.get(url=url, headers=headers, timeout=10)
        page += 1
        jobs = response.json()["data"]
        if not response.json()["hasMore"]:
            more_jobs = False
        jobs_to_create = []
        jobs_to_update = []

        for job in jobs:
            job_data = {
                "id": job["id"],
                "name": job_types[job["jobTypeId"]],
                "client": Client.objects.get(serv_titan_id=job["customerId"])
            }

            if ServiceTitanJob.objects.filter(id=job_data["id"]).exists():
                jobs_to_update.append(job_data)
            else:
                jobs_to_create.append(ServiceTitanJob(**job_data))

        # Bulk update
        with transaction.atomic():
            for job_data in jobs_to_update:
                ServiceTitanJob.objects.filter(
                    id=job_data["id"]).update(**job_data)

        # Bulk create
        ServiceTitanJob.objects.bulk_create(jobs_to_create)

    del_variables([headers, response, jobs, job_types,
                  jobs_to_create, jobs_to_update])


# TODO: Figure out where/when to use this
# @shared_task
# def update_clients_with_revenue(invoices, company_id):
#     company = Company.objects.get(id=company_id)
#     client_dict = {}
#     for invoice in invoices:
#         if float(invoice["total"]) > 0:
#             if invoice["id"] in client_dict:
#                 client_dict[invoice["id"]] += float(invoice["total"])
#             else:
#                 client_dict[invoice["id"]] = float(invoice["total"])
#     del invoices
#     tmpDict = client_dict.copy()
#     for client in tmpDict:
#         tmpClient = (
#             Client.objects.filter(serv_titan_id=client, company=company)
#             .order_by("address")
#             .first()
#         )
#         if tmpClient is not None:
#             if (
#                 tmpClient.service_titan_customer_since is not None
#                 and tmpClient.service_titan_customer_since
#                 > date.today() - timedelta(days=180)
#             ):
#                 client_dict.pop(client)
#     del tmpDict
#     client_ids = client_dict.keys()

#     clients = Client.objects.filter(
#         serv_titan_id__in=client_ids,
#         company=company,
#         status__in=["House For Sale", "House Recently Sold (6)"],
#     )

#     for client in clients:
#         client.revenue = Coalesce(
#             client_dict.get(client.serv_titan_id), client.revenue
#         )

#     Client.objects.bulk_update(clients, ["revenue"])


# from data.serviceTitan import *
# company = Company.objects.get(name="Test Company")
# get_service_titan_customers(company.id, company.tenant_id)
