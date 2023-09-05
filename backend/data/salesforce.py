from accounts.models import Company
from data.utils import save_client_list
from django.conf import settings

from celery import shared_task
from simple_salesforce import Salesforce


@shared_task
def get_salesforce_clients(company_id, task_id=None):
    company = Company.objects.get(id=company_id)
    url = "https://ismycustomermoving-dev-ed.develop.my.salesforce.com"
    sf = Salesforce(
        instance_url=url,
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
