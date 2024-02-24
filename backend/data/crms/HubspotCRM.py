from datetime import datetime, date, timedelta
from hubspot import HubSpot
from hubspot.crm.associations import BatchInputPublicObjectId
import logging

from accounts.models import Company
from data.models import Client, ClientUpdate
from data.crm import CRM
from data.utils import (
    auto_update,
    chunk_list,
    delete_extra_clients,
    save_client_list,
    verify_address,
)
from payments.models import CRMInvoice


class HubspotCRM(CRM):
    def __init__(self, company_id):
        """
        Initialize the HubspotCRM object with the company ID and HubSpot API key.
        Args:
        company_id (int): The ID of the company using the HubSpot CRM.
        hubspot_api_key (str): The API key for accessing HubSpot.
        """
        super().__init__(company_id)
        self.access_token = Company.objects.get(id=company_id).hubspot_api_key

    def get_access_token(self):
        api_client = HubSpot(access_token=self.access_token)
        return api_client

    def get_customers(self):
        api_client = self.get_access_token()
        clients = api_client.crm.contacts.get_all(
            properties=["id", "city", "state", "zip", "firstname",
                        "lastname", "email", "phone",
                        "address", "company", "hs_object_id"]
        )

        # Remove unnecessary values
        filtered_clients = []
        for client in clients:
            new_client = {}
            if client.properties["createdate"]:
                new_client["created"] = client.properties["createdate"]
            else:
                new_client["created"] = ""
            if client.properties["address"]:
                new_client["address"] = client.properties["address"]
            else:
                new_client["address"] = ""
            if client.properties["city"]:
                new_client["city"] = client.properties["city"]
            else:
                new_client["city"] = ""
            if client.properties["state"]:
                new_client["state"] = client.properties["state"]
            else:
                new_client["state"] = ""
            if client.properties["zip"]:
                new_client["zip code"] = client.properties["zip"]
            else:
                new_client["zip code"] = ""
            if client.properties["firstname"]:
                new_client["firstname"] = client.properties["firstname"]
            else:
                new_client["firstname"] = ""
            if client.properties["lastname"]:
                new_client["lastname"] = client.properties["lastname"]
            else:
                new_client["lastname"] = ""
            if client.properties["email"]:
                new_client["email"] = client.properties["email"]
            else:
                new_client["email"] = ""
            if client.properties["phone"]:
                new_client["phone"] = client.properties["phone"]
            else:
                new_client["phone"] = ""
            if client.properties["hs_object_id"]:
                new_client["hs_object_id"] = client.properties["hs_object_id"]
            else:
                new_client["hs_object_id"] = ""

            filtered_clients.append(new_client)

        # Chunk the clients list into batches of 1000
        client_batches = chunk_list(filtered_clients, 1000)

        # Schedule Celery tasks for each batch
        for batch in client_batches:
            save_client_list.delay(batch, self.company_id)

    def get_invoices(self):
        api_client = self.get_access_token()
        clients = api_client.crm.contacts.get_all()
        invoices_to_save = []
        for client in clients:
            batch_ids = BatchInputPublicObjectId([{'id': client.id}])
            associations = api_client.crm.associations.batch_api.read(
                from_object_type="contacts",
                to_object_type="deals",
                batch_input_public_object_id=batch_ids)
            for association in associations.results:
                deal = api_client.crm.deals.basic_api.get_by_id(
                    association.to[0].id)
                invoices_to_save.append([client.id, deal])
        print(invoices_to_save)
        invoice_batches = chunk_list(invoices_to_save, 1000)
        for batch in invoice_batches:
            self._save_invoices(batch)

    def _save_invoices(self, invoices):
        existing_invoice_ids = set(
            CRMInvoice.objects.values_list('invoice_id', flat=True))
        invoices_to_create = []
        print(f"NVOICES IDS: {invoices}")
        for invoice in invoices:
            print("1")
            if str(invoice[0]) not in existing_invoice_ids:
                print("2")
                client = Client.objects.filter(
                    hubspot_id=invoice[0],
                    company_id=self.company_id)
                if client.exists():
                    print("3")
                    client = client.first()

                    created_on = datetime.fromisoformat(
                        invoice[1].properties["createdate"].rstrip('Z')).date()

                    attributed = False
                    last_status_update_date = ClientUpdate.objects.filter(
                        client=client,
                        status__in=["House For Sale",
                                    "House Recently Sold (6)"]
                    ).values_list("date", flat=True).order_by("-date").first()

                    if last_status_update_date:
                        if (
                            (client.service_titan_customer_since is None or
                                client.service_titan_customer_since <
                             date.today() - timedelta(days=180)) and
                            client.status in
                                ["House For Sale", "House Recently Sold (6)"] and
                            created_on < last_status_update_date + timedelta(days=365) and created_on >= last_status_update_date  # noqa E501
                        ):
                            attributed = True
                    print("ADDING INVOICE")
                    invoices_to_create.append(
                        CRMInvoice(
                            invoice_id=invoice[1].properties["hs_object_id"],
                            amount=invoice[1].properties["amount"],
                            client=client,
                            created_on=created_on,
                            attributed=attributed
                        )
                    )
        CRMInvoice.objects.bulk_create(invoices_to_create)

    # def _get_invoice_associations(self, invoice_id):
    #     api_client = self.get_access_token()
    #     api_response =
        # api_client.crm.associations.v4.basic_api.get_crm_v4_objects_object_type_object_id_associations_to_object_type(
    #         object_type="deal", object_id=invoice_id,
        # to_object_type="contact", limit=5)
    #     print(api_response)

    #     return associations

    def get_lifetime_revenue_data_from_invoices(self):
        """
        Updates the customer data with the lifetime
        revenue based on the sum of closed deals

        Returns:
        None
        """
        try:
            clients = Client.objects.filter(company_id=self.company_id)

            for client in clients:
                invoices = CRMInvoice.objects.filter(
                    client=client).order_by("created_on")

                if invoices.exists():
                    client.customer_lifetime_value = sum(
                        invoice.amount for invoice in invoices)
                    client.save(update_fields=[
                        "customer_lifetime_value"])

        except Exception as e:
            logging.error(
                f"Error in get_customer_since_data_from_invoices: {e}")

    def complete_sync(self, task_id=None, automated=False):
        company = Company.objects.get(id=self.company_id)
        self.get_customers()
        delete_extra_clients.delay(self.company_id, task_id)
        print("GETTING INVOICES")
        self.get_invoices()
        clients_to_verify = list(Client.objects.filter(
            company=company, old_address=None
        ).values_list("id", flat=True))
        verify_address.delay(clients_to_verify)
        del company, clients_to_verify

        if not automated:
            auto_update.delay(company_id=self.company_id)
