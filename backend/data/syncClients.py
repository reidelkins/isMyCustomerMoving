from celery import shared_task
import requests
import logging
from time import sleep

from datetime import datetime, timedelta, date
from django.conf import settings
from django.db import transaction
from django.db.models import Min
from django.db.models.functions import Coalesce

from accounts.models import Company, CustomUser
from .models import Client
from .utils import (
    save_client_list,
    update_client_list,
    do_it_all,
    delete_extra_clients,
    del_variables,
    get_service_titan_access_token,
)
from simple_salesforce import Salesforce


@shared_task
def get_fieldEdge_clients(company_id, task_id):
    Company.objects.get(id=company_id)


@shared_task
def get_hubspot_clients(company_id, task_id):
    Company.objects.get(id=company_id)


@shared_task
def get_salesforce_clients(company_id, task_id=None):
    company = Company.objects.get(id=company_id)

    sf = Salesforce(
        instance_url="https://ismycustomermoving-dev-ed.develop.my.salesforce.com",
        session_id=company.sf_access_token,
        consumer_key=settings.SALESFORCE_CONSUMER_KEY,
        consumer_secret=settings.SALESFORCE_CONSUMER_SECRET,
    )

    contacts = sf.query(
        "SELECT FirstName, LastName, Phone, MailingStreet FROM Contact"
    )
    clients = []
    count = 0
    for contact in contacts["records"]:
        x = contact["MailingStreet"]
        count += 1
        if x is not None:
            x = x.split("\n")
            if len(x) > 1:
                street = x[0]
                x = x[1].replace(",", "")
                x = x.split(" ")
                if len(x) == 3 and street is not None:
                    client = {
                        "name": f"{contact['FirstName']} {contact['LastName']}",
                        "phone number": contact["Phone"],
                        "address": street,
                        "city": x[0],
                        "state": x[1],
                        "zip code": x[2],
                    }
                    clients.append(client)

    save_client_list(clients, company_id)

    # bulk = SalesforceBulk(
    #     sessionId="""https://login.salesforce.com/
    #           id/00DDn00000DsoYnMAJ/005Dn000007Eo6XIAS""",
    #     host="https://ismycustomermoving-dev-ed.develop.my.salesforce.com",
    # )
    # job = bulk.create_query_job("Contact", contentType="JSON")
    # batch = bulk.query(job, "select Id,LastName from Contact")
    # bulk.close_job(job)
    # while not bulk.is_batch_done(batch):
    #     time.sleep(10)

    # for result in bulk.get_all_results_for_query_batch(batch):
    #     result = json.load(IteratorBytesIO(result))
    #     for row in result:
    #         print(row)  # dictionary rows


@shared_task
def get_service_titan_clients(
    company_id, task_id, option=None, automated=False
):
    company = Company.objects.get(id=company_id)
    if not option:
        option = company.service_titan_customer_sync_option
    else:
        company.service_titan_customer_sync_option = option
        company.save()
    tenant = company.tenant_id
    headers = get_service_titan_access_token(company_id)
    clients = []
    moreClients = True
    # get client data
    page = 1
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
            for client in clients:
                client["name"] = " "
        result = save_client_list.delay(clients, company_id)
        del_variables([clients, response])

    # wait up to 30 seconds for the last task to complete
    count = 0
    while result.status != "SUCCESS" and count < 30:
        sleep(1)
        count += 1

    delete_extra_clients.delay(company_id, task_id)

    get_servicetitan_equipment.delay(company_id)
    if not automated:
        do_it_all.delay(company_id)
    if option == "option1":
        frm = ""
        moreClients = True
        page = 0
        while moreClients:
            page += 1
            response = requests.get(
                url=(
                    f"https://api.servicetitan.io/crm/v2/tenant/"
                    f"{tenant}/export/customers/contacts?from={frm}"
                ),
                headers=headers,
                timeout=10,
            )
            # for number in response.json()['data']:
            #     numbers.append(number)
            numbers = response.json()["data"]
            if response.json()["hasMore"]:
                frm = response.json()["continueFrom"]
            else:
                moreClients = False
            update_client_list.delay(numbers)
            del_variables([numbers, response])
    del_variables([frm, moreClients, headers, company, tenant])
    update_clients_with_first_invoice_date.delay(company_id)


@shared_task
def update_clients_with_last_service_date(equipment, company_id):
    company = Company.objects.get(id=company_id)
    client_dict = {}
    for equip in equipment:
        if equip["installedOn"] is not None:
            try:
                client_dict[equip["customerId"]] = datetime.strptime(
                    equip["installedOn"], "%Y-%m-%dT%H:%M:%SZ"
                ).date()
            except Exception as e:
                logging.error(e)

    client_ids = client_dict.keys()
    clients = Client.objects.filter(
        serv_titan_id__in=client_ids, company=company
    ).select_related("company")

    for client in clients:
        client.equipment_installed_date = Coalesce(
            client_dict.get(client.serv_titan_id),
            client.equipment_installed_date,
        )
        client.save(update_fields=["equipment_installed_date"])
    return len(clients)


@shared_task
def update_clients_with_first_invoice_date(company_id):
    company = Company.objects.get(id=company_id)
    tenant = company.tenant_id
    headers = get_service_titan_access_token(company_id)
    more_invoices = True
    page = 1

    while more_invoices:
        invoices = []
        url = (
            f"https://api.servicetitan.io/accounting"
            f"/v2/tenant/{tenant}/invoices?page={page}&pageSize=2500"
        )
        response = requests.get(url, headers=headers, timeout=10)
        page += 1
        for invoice in response.json()["data"]:
            invoices.append(
                {
                    "createdOn": invoice["createdOn"],
                    "id": invoice["customer"]["id"],
                }
            )
        process_invoices.delay(invoices, company_id)

        if not response.json()["hasMore"]:
            more_invoices = False


@shared_task
def process_invoices(invoices, company):
    company = Company.objects.get(id=company)
    client_dict = {}
    for invoice in invoices:
        # on the same line as the last statement, print another .
        if invoice["createdOn"] is not None:
            try:
                tmpClients = Client.objects.filter(
                    serv_titan_id=invoice["id"], company=company
                )
                year, month, day = map(
                    int, invoice["createdOn"][:10].split("-")
                )
                invoice_date = date(year, month, day)
                for tmpClient in tmpClients:
                    if tmpClient is not None:
                        if (
                            tmpClient.service_titan_customer_since is None
                            or tmpClient.service_titan_customer_since
                            > invoice_date
                            or tmpClient.service_titan_customer_since
                            == date(1, 1, 1)
                        ):
                            if invoice["id"] in client_dict:
                                if client_dict[invoice["id"]] > invoice_date:
                                    client_dict[invoice["id"]] = invoice_date
                            else:
                                client_dict[invoice["id"]] = invoice_date
            except Exception as e:
                logging.error(f"date error {e}")
    update_clients(
        client_dict, company
    )  # Update the clients' service_titanCustomerSince field


def update_clients(client_dict, company):
    client_ids = client_dict.keys()
    company = Company.objects.get(id=company.id)

    clients = Client.objects.filter(
        serv_titan_id__in=client_ids, company=company
    ).select_related("company")

    updated_clients = []
    for client in clients:
        client.service_titan_customer_since = client_dict.get(
            client.serv_titan_id, client.service_titan_customer_since
        )
        updated_clients.append(client)
    with transaction.atomic():
        Client.objects.bulk_update(
            updated_clients, ["service_titan_customer_since"]
        )


@shared_task
def get_servicetitan_equipment(company_id):
    company = Company.objects.get(id=company_id)
    tenant = company.tenant_id
    headers = get_service_titan_access_token(company_id)
    more_equipment = True
    # get client data
    page = 1
    while more_equipment:
        url = (
            f"https://api.servicetitan.io/equipmentsystems"
            f"/v2/tenant/{tenant}/installed-equipment"
            f"?page={page}&pageSize=2500"
        )
        response = requests.get(
            url,
            headers=headers,
            timeout=10,
        )
        # additional option &modifiedOnOrAfter=2000-1-1T00:00:14-05:00
        page += 1
        equipment = response.json()["data"]
        if not response.json()["hasMore"]:
            more_equipment = False

        update_clients_with_last_service_date.delay(equipment, company_id)
        del_variables([equipment, response])


@shared_task
def get_service_titan_invoices(company_id):
    company = Company.objects.get(id=company_id)
    earliest_date = CustomUser.objects.filter(company=company).aggregate(
        Min("date_joined")
    )
    rfc3339 = earliest_date["date_joined__min"].isoformat()
    rfc3339 = rfc3339[:-6]
    tenant = company.tenant_id
    headers = get_service_titan_access_token(company_id)
    more_invoices = True
    # get client data
    page = 1
    invoices = []
    while more_invoices:
        url = (
            f"https://api.servicetitan.io/accounting/"
            f"v2/tenant/{tenant}/invoices?page={page}"
            f"&pageSize=2500&invoicedOnOrAfter={rfc3339}"
        )

        response = requests.get(url, headers=headers, timeout=10)
        page += 1
        for invoice in response.json()["data"]:
            invoices.append(
                {"id": invoice["customer"]["id"], "total": invoice["total"]}
            )
        if not response.json()["hasMore"]:
            more_invoices = False
    update_clients_with_revenue.delay(invoices, company_id)
    del_variables([invoices, response])


@shared_task
def update_clients_with_revenue(invoices, company_id):
    company = Company.objects.get(id=company_id)
    client_dict = {}
    for invoice in invoices:
        if float(invoice["total"]) > 0:
            if invoice["id"] in client_dict:
                client_dict[invoice["id"]] += float(invoice["total"])
            else:
                client_dict[invoice["id"]] = float(invoice["total"])
    del invoices
    tmpDict = client_dict.copy()
    for client in tmpDict:
        tmpClient = (
            Client.objects.filter(serv_titan_id=client, company=company)
            .order_by("address")
            .first()
        )
        if tmpClient is not None:
            if (
                tmpClient.service_titan_customer_since is not None
                and tmpClient.service_titan_customer_since
                > date.today() - timedelta(days=180)
            ):
                client_dict.pop(client)
    del tmpDict
    client_ids = client_dict.keys()

    clients = Client.objects.filter(
        serv_titan_id__in=client_ids,
        company=company,
        status__in=["House For Sale", "House Recently Sold (6)"],
    )

    for client in clients:
        client.revenue = Coalesce(
            client_dict.get(client.serv_titan_id), client.revenue
        )

    Client.objects.bulk_update(clients, ["revenue"])
