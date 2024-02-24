from datetime import date, datetime, timedelta
import logging
from time import sleep

from accounts.models import Company
from data.crm import CRM
from data.models import Client, ClientUpdate
from data.utils import (
    auto_update,
    delete_extra_clients,
    generic_crm_task,
    get_service_titan_access_token,
    save_client_list,
    verify_address,
)
from payments.models import CRMInvoice

from django.db.models import Q
from django.db.models.functions import Coalesce


import requests


class ServiceTitanCRM(CRM):
    def __init__(self, company_id):
        """
        Initialize the ServiceTitanCRM object with the company ID.
        Args:
        company_id (int): The ID of the company using the ServiceTitan CRM.
        tenant (str): The tenant ID for the ServiceTitan API.
        """
        super().__init__(company_id)
        self.tenant = Company.objects.get(id=company_id).tenant_id

    def get_access_token(self):
        """
        Retrieve the access token for ServiceTitan API.
        Overrides the method from the base CRM class.
        Returns:
        str: The access token for the ServiceTitan API.
        """
        return get_service_titan_access_token(self.company_id)

    def get_locations(self, option):
        """
        Retrieves location data from the ServiceTitan API.

        Args:
        option (str): Specific option for filtering data.

        Returns:
        list: A list of locations retrieved from the ServiceTitan API.
        """
        headers = self.get_access_token()
        clients = []
        moreClients = True
        page = 1
        results = []

        while moreClients:
            response = requests.get(
                f"https://api.servicetitan.io/crm/v2/tenant/{self.tenant}/locations?page={page}&pageSize=2500",  # noqa E501
                headers=headers,
                timeout=10,
            )
            page += 1
            clients = response.json()["data"]
            if not response.json()["hasMore"]:
                moreClients = False

            if option == "option3":
                for client in clients:
                    # Modify client names if option3 is selected
                    client["name"] = " "

            # Assuming a method to process these clients
            results.append(save_client_list.delay(clients, self.company_id))

        count = 0
        while any(not result.ready() for result in results) and count < 30:
            sleep(1)
            count += 1

        # Clean up variables to free up memory
        del headers, response, clients
        # return results

    def get_equipment(self):
        """
        Retrieves equipment data from the ServiceTitan API.

        Returns:
        list: A list of equipment retrieved from the ServiceTitan API.
        """
        try:
            headers = self.get_access_token()
            more_equipment = True
            page = 1
            # all_equipment = []

            while more_equipment:
                response = requests.get(
                    f"https://api.servicetitan.io/equipmentsystems/v2/tenant/{self.tenant}/installed-equipment?page={page}&pageSize=2500",  # noqa E501
                    headers=headers,
                    timeout=10,
                )
                page += 1
                equipment = response.json()["data"]
                generic_crm_task.delay(
                    'ServiceTitanCRM', self.company_id,
                    "_update_clients_with_last_day_of_equipment_installation",
                    equipment=equipment)

                # all_equipment.extend(equipment)

                if not response.json()["hasMore"]:
                    more_equipment = False

            del headers, response, equipment
            # return all_equipment

        except Exception as e:
            logging.error(f"Error in get_service_titan_equipment: {e}")
            return []

    def _update_clients_with_last_day_of_equipment_installation(self, equipment):
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
            serv_titan_id__in=client_ids, company_id=self.company_id)
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
        del client_dict, client_ids, clients

    def get_customers(self):
        """
        Retrieves customer data from the ServiceTitan API.

        Returns:
        list: A list of customers retrieved from the ServiceTitan API.
        """
        try:
            headers = self.get_access_token()
            clients = Client.objects.filter(
                Q(phone_number=None) | Q(email=None),
                company_id=self.company_id
            ).exclude(serv_titan_id=None)
            count = 0
            for client in clients:
                if count % 1500 == 0:  # Refresh token every 1500 requests
                    headers = self.get_access_token()
                count += 1
                try:
                    response = requests.get(
                        f"https://api.servicetitan.io/crm/v2/tenant/{self.tenant}/customers/{client.serv_titan_id}/contacts",  # noqa E501
                        headers=headers,
                        timeout=10,
                    )
                    if response.status_code == 200:
                        contact_info = response.json()["data"]
                        self._update_client_contact_info(client, contact_info)
                except Exception as e:
                    logging.error(
                        f"""Error in get_service_titan_customers for
                        client {client.serv_titan_id}: {e}""")

            del headers, response, clients

        except Exception as e:
            logging.error(f"Error in get_service_titan_customers: {e}")
            return []

    def _update_client_contact_info(self, client, contact_info):
        """
        Helper method to update contact information for a client.

        Args:
        client (Client): Client object to be updated.
        contact_info (list): List of contact information.

        Returns:
        None
        """
        try:
            found_phone = False
            for info in contact_info:
                if info["type"] == "MobilePhone" and not found_phone:
                    client.phone_number = info["value"]
                    found_phone = True
                elif info["type"] == "Email":
                    client.email = info["value"]
            client.save()

        except Exception as e:
            logging.error(
                f"Error in _update_client_contact_info for client {client.id}: {e}")

    def get_invoices(self):
        """
        Retrieves invoice data from the ServiceTitan API.

        Args:

        Returns:
        list: A list of invoices retrieved from the ServiceTitan API.
        """
        headers = self.get_access_token()
        more_invoices = True
        page = 1
        results = []
        while more_invoices:
            response = requests.get(
                f"https://api.servicetitan.io/accounting/v2/tenant/{self.tenant}/invoices?page={page}&pageSize=1000",  # noqa E501
                headers=headers,
                timeout=15,
            )
            page += 1
            invoices = response.json().get("data", [])

            results.append(generic_crm_task.delay(
                'ServiceTitanCRM', self.company_id,
                "save_invoices_to_db", invoices=invoices))
            more_invoices = response.json().get("hasMore", False)

        count = 0
        while any(not result.ready() for result in results) and count < 30:
            sleep(1)
            count += 1
        generic_crm_task.delay(
            'ServiceTitanCRM', self.company_id,
            "get_customer_since_data_from_invoices")
        return

    def save_invoices_to_db(self, invoices):
        """
        Saves a list of invoices to the database.

        Args:
        invoices (list): A list of invoice data.

        Returns:
        None
        """
        existing_invoice_ids = set(
            CRMInvoice.objects.values_list('invoice_id', flat=True))
        invoices_to_create = []

        for invoice in invoices:
            if str(invoice["id"]) not in existing_invoice_ids:
                client_id = invoice["customer"]
                if type(client_id) is dict:
                    client_id = client_id["id"]
                client = Client.objects.filter(
                    serv_titan_id=client_id, company_id=self.company_id)
                if client.exists():
                    client = client.first()

                    created_on = datetime.strptime(
                        invoice["createdOn"][:10], "%Y-%m-%d").date()

                    attributed = False
                    last_status_update_date = ClientUpdate.objects.filter(
                        client=client,
                        status__in=["House For Sale",
                                    "House Recently Sold (6)"]
                    ).values_list("date", flat=True).order_by("-date").first()

                    if last_status_update_date:
                        if (
                            (client.service_titan_customer_since is None or
                                client.service_titan_customer_since < date.today() - timedelta(days=180)) and  # noqa E501
                            client.status in ["House For Sale", "House Recently Sold (6)"] and  # noqa E501
                            created_on < last_status_update_date + timedelta(days=365) and  # noqa E501
                            created_on >= last_status_update_date
                        ):
                            attributed = True

                    invoices_to_create.append(
                        CRMInvoice(
                            invoice_id=invoice["id"],
                            amount=invoice["total"],
                            client=client,
                            created_on=created_on,
                            attributed=attributed
                        )
                    )
        CRMInvoice.objects.bulk_create(invoices_to_create)

    def get_customer_since_data_from_invoices(self):
        """
        Updates the customer data based on the
        earliest invoice date from ServiceTitan invoices.

        Returns:
        None
        """
        try:
            clients = Client.objects.filter(company_id=self.company_id)

            for client in clients:
                invoices = CRMInvoice.objects.filter(
                    client=client).order_by("created_on")

                if invoices.exists():
                    first_invoice = invoices.first()
                    client.service_titan_customer_since = first_invoice.created_on
                    lifetime_revenue = sum(
                        invoice.amount for invoice in invoices)
                    client.service_titan_lifetime_revenue = lifetime_revenue
                    client.save(update_fields=[
                                "service_titan_customer_since",
                                "service_titan_lifetime_revenue"])

        except Exception as e:
            logging.error(
                f"Error in get_customer_since_data_from_invoices: {e}")

    def complete_sync(self, option=None, task_id=None, automated=False):
        """
        Complete a sync with the ServiceTitan API.

        Args:
        option (str): Specific option for filtering data.

        Returns:
        None
        """
        company = Company.objects.get(id=self.company_id)
        if option is None:
            option = company.service_titan_customer_sync_option
        else:
            company.service_titan_customer_sync_option = option
            company.save()
        self.get_locations(option)
        delete_extra_clients.delay(self.company_id, task_id)
        generic_crm_task.delay(
            'ServiceTitanCRM', self.company_id, "get_equipment")

        if option == "option1":
            generic_crm_task.delay(
                'ServiceTitanCRM', self.company_id, "get_customers")

        generic_crm_task.delay(
            'ServiceTitanCRM', self.company_id, "get_invoices")

        clients_to_verify = list(Client.objects.filter(
            company=company, old_address=None
        ).values_list("id", flat=True))
        verify_address.delay(clients_to_verify)
        del company, clients_to_verify

        if not automated:
            auto_update.delay(company_id=self.company_id)
