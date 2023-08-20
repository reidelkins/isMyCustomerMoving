from django.db.models import QuerySet
from django.db.models.expressions import F
from django.test import TestCase
from unittest.mock import patch, MagicMock, Mock, call
from datetime import date, datetime, timedelta

import requests
import pytest

from accounts.models import Company, CustomUser
from data.models import Client, HomeListing, SavedFilter, ZipCode
from data.syncClients import (
    complete_service_titan_sync,
    get_service_titan_locations,
    get_service_titan_equipment,
    update_clients_with_last_day_of_equipment_installation,
    get_service_titan_customers,
    get_service_titan_invoices,
    save_invoices,
    get_customer_since_data_from_invoices
)
from data.utils import (
    find_client_count,
    find_clients_to_delete,
    format_zip,
    reactivate_clients,
    delete_extra_clients,
    verify_address,
    save_service_area_list,
    send_zapier_recently_sold
)
from payments.models import ServiceTitanInvoice


@pytest.fixture
def mock_access_token():
    with patch("data.syncClients.get_service_titan_access_token") as mock:
        yield mock


@pytest.fixture
def mock_delay():
    with patch("data.syncClients.save_client_list.delay") as mock:
        yield mock


@pytest.fixture
def mock_get():
    with patch("requests.get") as mock:
        yield mock


@pytest.fixture
def mock_post():
    with patch("requests.post") as mock:
        yield mock


@pytest.fixture
def mock_update_clients_with_last_day_of_equipment_installation():
    with patch("data.syncClients.update_clients_with_last_day_of_equipment_installation.delay") as mock:
        yield mock


@pytest.fixture
def mock_get_service_titan_locations():
    with patch("data.syncClients.get_service_titan_locations") as mock:
        yield mock


@pytest.fixture
def mock_delete_extra_clients():
    with patch("data.syncClients.delete_extra_clients.delay") as mock:
        yield mock


@pytest.fixture
def mock_get_service_titan_equipment():
    with patch("data.syncClients.get_service_titan_equipment.delay") as mock:
        yield mock


@pytest.fixture
def mock_do_it_all():
    with patch("data.syncClients.do_it_all.delay") as mock:
        yield mock


@pytest.fixture
def mock_get_service_titan_customers():
    with patch("data.syncClients.get_service_titan_customers.delay") as mock:
        yield mock


@pytest.fixture
def mock_get_service_titan_invoices():
    with patch("data.syncClients.get_service_titan_invoices.delay") as mock:
        yield mock


@pytest.fixture
def mock_company():
    with patch("accounts.models.Company.objects.get") as mock:
        yield mock


@pytest.fixture
def mock_client():
    with patch("data.models.Client.objects.filter") as mock:
        yield mock


# @pytest.fixture
# def mock_client_for_save_invoices():
#     with patch("data.models.Client.objects.filter", return_value=mock_queryset) as mock:
#         client = Client.objects.filter(
#             serv_titan_id=client_id, company=company)
#         if client.count() > 0:
#             yield mock


@pytest.fixture
def mock_update_client_list():
    with patch("data.syncClients.update_client_list.delay") as mock:
        yield mock


@pytest.fixture
def mock_save_invoices():
    with patch("data.syncClients.save_invoices.delay") as mock:
        yield mock


@pytest.fixture
def mock_get_customer_since_data_from_invoices():
    with patch("data.syncClients.get_customer_since_data_from_invoices.delay") as mock:
        yield mock


@pytest.fixture
def mock_invoice():
    with patch("payments.models.ServiceTitanInvoice.objects") as mock:
        yield mock


@pytest.fixture
def mock_invoice_filter():
    with patch("payments.models.ServiceTitanInvoice.objects.filter") as mock:
        yield mock


@pytest.fixture
def mock_verify_address():
    with patch("data.utils.verify_address.delay") as mock:
        yield mock


@pytest.fixture
def mock_parse_streets():
    with patch("data.utils.parse_streets") as mock:
        yield mock


@pytest.fixture
def mock_filter_home_listings():
    with patch("data.utils.filter_home_listings") as mock:
        yield mock


class TestUtilFunctions(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="company_name",
            zapier_recently_sold="zapier.com"
        )
        zip = ZipCode.objects.create(zip_code="32952")
        self.client = Client.objects.create(
            name="Test Client1",
            address="260 Milford Point Rd",
            city="Merritt Island",
            state="FL",
            zip_code=zip,
            company=self.company,)
        self.home_listing = HomeListing.objects.create(
            zip_code=zip,
            address="260 Milford Point Rd",
            city="Merritt Island",
            state="FL",
            sqft=1000,
            lot_sqft=1000,
            bedrooms=3,
            bathrooms=2,
            housing_type="Single Family",
            year_built=2000,
            listed=date.today()-timedelta(days=6),
            status="House Recently Sold (6)",
            price=10000000
        )
        self.home_listing_2 = HomeListing.objects.create(
            listed=date.today()-timedelta(days=8),
            status="House Recently Sold (6)",
            zip_code=zip
        )

        self.saved_filter = SavedFilter.objects.create(
            name=" Test Saved Filter",
            company=self.company,
            filter_type="Recently Sold",
            saved_filters="{'price_min': 1000000}",
            for_zapier=True,
        )
        self.saved_filter_2 = SavedFilter.objects.create(
            name=" Test Saved Filter2",
            company=self.company,
            filter_type="Recently Sold",
            saved_filters="{'price_max': 1000000}",
            for_zapier=False,
        )

    @patch("accounts.models.Company.product")
    def test_find_client_count(self, mock_subscription):
        mock_subscription.amount = 150
        mock_subscription.interval = "month"
        self.assertEqual(find_client_count(mock_subscription), 5000)

        mock_subscription.amount = 1650
        mock_subscription.interval = "year"
        self.assertEqual(find_client_count(mock_subscription), 5000)

        mock_subscription.amount = 250
        mock_subscription.interval = "month"
        self.assertEqual(find_client_count(mock_subscription), 10000)

        mock_subscription.amount = 2750
        mock_subscription.interval = "year"
        self.assertEqual(find_client_count(mock_subscription), 10000)

        mock_subscription.amount = 400
        mock_subscription.interval = "month"
        self.assertEqual(find_client_count(mock_subscription), 20000)

        mock_subscription.amount = 4400
        mock_subscription.interval = "year"
        self.assertEqual(find_client_count(mock_subscription), 20000)

        mock_subscription.amount = 1500
        mock_subscription.interval = "month"
        self.assertEqual(find_client_count(mock_subscription), 150000)

        mock_subscription.amount = 16500
        mock_subscription.interval = "year"
        self.assertEqual(find_client_count(mock_subscription), 150000)

        mock_subscription.amount = 5000
        mock_subscription.interval = "month"
        self.assertEqual(find_client_count(mock_subscription), 500000)

        mock_subscription.amount = 55000
        mock_subscription.interval = "year"
        self.assertEqual(find_client_count(mock_subscription), 500000)

        mock_subscription.amount = 5001
        mock_subscription.interval = "year"
        self.assertEqual(find_client_count(mock_subscription), 100000)

    @patch("data.utils.find_client_count")
    def test_find_clients_to_delete(self, mock_find_client_count):
        mock_find_client_count.return_value = 100
        self.assertEqual(find_clients_to_delete(120, "test_product"), 20)

        mock_find_client_count.return_value = 100
        self.assertEqual(find_clients_to_delete(80, "test_product"), 0)

    # @patch("data.utils.Company.objects.get")
    # @patch("data.utils.Client.objects.filter")
    # @patch("data.utils.find_client_count")
    # def test_reactivate_clients(
    #     self, mock_find_client_count, mock_client_filter, mock_company_get
    # ):
    #     mock_find_client_count.return_value = 100
    #     mock_client_filter.return_value = MagicMock()
    #     mock_client_filter.return_value.count.return_value = 80
    #     mock_company_get.return_value = MagicMock()

    #     reactivate_clients(1)
    #     mock_client_filter.return_value.update.assert_called_once_with(
    #         active=True
    #     )

    #     mock_client_filter.return_value.count.return_value = 120
    #     mock_client_filter.return_value.update.assert_not_called()

    # @patch("data.utils.Company.objects.get")
    # @patch("data.utils.Client.objects.filter")
    # @patch("data.utils.find_clients_to_delete")
    # @patch("data.utils.send_mail")
    # @patch("data.utils.CustomUser.objects.filter")
    # @patch("data.utils.Task.objects.get")
    # def test_delete_extra_clients(
    #     self,
    #     mock_task_get,
    #     mock_user_filter,
    #     mock_send_mail,
    #     mock_find_clients_to_delete,
    #     mock_client_filter,
    #     mock_company_get,
    # ):
    #     mock_find_clients_to_delete.return_value = 10
    #     mock_client_filter.return_value = MagicMock()
    #     mock_client_filter.return_value.count.return_value = 120
    #     mock_client_filter.return_value.values_list.return_value = range(120)
    #     mock_user_filter.return_value = [MagicMock()]
    #     mock_company_get.return_value = MagicMock()
    #     mock_task_get.return_value = MagicMock()

    #     delete_extra_clients(1)
    #     mock_send_mail.assert_called_once()
    #     mock_task_get.return_value.save.assert_not_called()

    #     delete_extra_clients(1, 1)
    #     mock_task_get.return_value.save.assert_called_once()

    # @patch("Client.objects")
    @patch("requests.get")
    def test_verify_address(self, mock_get):
        response_text = """
        <AddressValidateResponse>
            <Address ID="1">
                <Address2>456 Elm St</Address2>
                <City>New York</City>
                <State>NY</State>
                <Zip5>10001</Zip5>
            </Address>
        </AddressValidateResponse>
        """
        mock_response = MagicMock()
        mock_response.text = response_text
        mock_get.return_value = mock_response

        # Call Function
        verify_address(self.client.id)

        # Verify Functionality
        mock_get.assert_called()

        # Check if the client's address was updated correctly
        self.client.refresh_from_db()
        self.assertEqual(self.client.address, "456 Elm St")
        self.assertEqual(self.client.city, "New York")
        self.assertEqual(self.client.state, "NY")
        self.assertEqual(self.client.zip_code.zip_code, "10001")
        self.assertTrue(self.client.usps_different)
        self.assertEqual(
            self.client.old_address,
            "260 Milford Point Rd, Merritt Island, FL 32952"
        )

    @patch("requests.get")
    def test_verify_address_invalid_client(self, mock_get):
        # Attempt to verify address for a non-existent client
        invalid_client_id = "non_existent_client_id"

        # Call Function
        verify_address(invalid_client_id)

        # Assertions
        mock_get.assert_not_called()

    @patch("data.utils.parse_streets")
    def test_verify_address_usps_error(self, mock_parse_streets):
        # Mock USPS API request exception
        with patch("requests.get", side_effect=requests.exceptions.RequestException("Error")):
            verify_address(self.client.id)

        # Assertions
        mock_parse_streets.assert_not_called()

    def test_verify_address_usps_validation_error(self):
        # Mock USPS API response with validation error
        response_text = """
        <AddressValidateResponse>
            <Address ID="1">
                <Error>Error occurred during validation</Error>
                <City>New York</City>
                <State>NY</State>
                <Zip5>10001</Zip5>
            </Address>
        </AddressValidateResponse>
        """
        response_mock = MagicMock()
        response_mock.text = response_text

        with patch("requests.get", return_value=response_mock):
            verify_address(self.client.id)

        # Check if the client's address remains unchanged
        self.client.refresh_from_db()
        self.assertEqual(self.client.address, "260 Milford Point Rd")
        self.assertEqual(self.client.city, "Merritt Island")
        self.assertEqual(self.client.state, "FL")
        self.assertEqual(self.client.zip_code.zip_code, "32952")
        self.assertFalse(self.client.usps_different)
        self.assertEqual(
            self.client.old_address,
            None
        )

    @patch("requests.post")
    @patch("data.utils.filter_home_listings")
    def test_send_zapier_recently_sold(self, mock_filter_home_listings, mock_post):
        mock_filter_home_listings.return_value = HomeListing.objects.filter(
            id=self.home_listing.id)
        send_zapier_recently_sold(self.company.id)

        # this shows that that a single saved filter was found
        mock_filter_home_listings.assert_called_once()

        # this shows the function was called once given the one filtered home listing
        mock_post.assert_called_once()

    def test_save_service_area_list(self):

        sample_service_area_list = [
            {
                'Zip_Code': '12345',
            },
            {
                'Zip_Code': '67890',
            },
            {
                'Zip_Code': '13579',
            }
        ]

        # Call the function
        save_service_area_list(sample_service_area_list, self.company.id)

        self.client.refresh_from_db()

        # Verify that the service area list was saved
        zip_code_queryset = ZipCode.objects.filter(
            zip_code__in=['12345', '67890', '13579'])

        # Convert the queryset of ZipCode objects into a set of primary keys
        expected_zip_codes = set(
            zip_code_queryset.values_list('pk', flat=True))

        # Convert the ManyToMany field into a set of primary keys
        actual_zip_codes = set(
            self.company.service_area_zip_codes.values_list('pk', flat=True))

        # Compare the sets of primary keys
        self.assertEqual(expected_zip_codes, actual_zip_codes)


class TestSyncClientFunctions(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="company_name", tenant_id=1, service_titan_customer_sync_option="option2")
        self.company_option1 = Company.objects.create(
            name="company_name2", tenant_id=1, service_titan_customer_sync_option="option1")
        self.client1 = Client.objects.create(
            name="Test Client1",
            address="123 Test Street",
            zip_code=ZipCode.objects.create(zip_code="12345"),
            company=self.company,
            serv_titan_id=240000001)
        self.client2 = Client.objects.create(
            name="Test Client2",
            address="123 Test Street",
            zip_code=ZipCode.objects.get(zip_code="12345"),
            company=self.company,
            serv_titan_id=240000002)
        self.invoice1 = ServiceTitanInvoice(
            client=self.client1,
            id="12345",
            created_on=date.today(),
            amount=100,
        )
        self.invoice2 = ServiceTitanInvoice(
            client=self.client1,
            id="123456",
            created_on=date.today() - timedelta(days=100),
            amount=1000.12,
        )

    @patch("data.syncClients.get_service_titan_access_token")
    @patch("data.syncClients.save_client_list.delay")
    @patch("requests.get")
    def test_get_service_titan_locations(self, mock_get, mock_delay, mock_access_token):
        mock_access_token.return_value = "dummy_access_token"

        # Mock the API response and its JSON data
        mock_response = Mock()
        fake_json = {
            "page": 2,
            "pageSize": 2,
            "hasMore": False,
            "totalCount": None,
            "data": [
                {
                    "taxZoneId": 18050,
                    "id": 240200029,
                    "customerId": 240000029,
                    "active": True,
                    "name": "Priscilla Dobbins",
                    "address": {
                        "street": "3110 Roxbury Court",
                        "unit": None,
                        "city": "Cleveland",
                        "state": "TN",
                        "zip": "37312",
                        "country": "USA",
                        "latitude": 35.2063812,
                        "longitude": -84.8890157
                    },
                    "customFields": [
                        {
                            "typeId": 7041,
                            "name": "     Client #",
                            "value": "10027-1"
                        }
                    ],
                    "createdOn": "0001-01-01T00:00:00Z",
                    "createdById": 0,
                    "modifiedOn": "2023-06-29T18:58:34.763Z",
                    "mergedToId": None,
                    "zoneId": 271438116,
                    "externalData": None
                },
                {
                    "taxZoneId": 18050,
                    "id": 240200030,
                    "customerId": 240000030,
                    "active": True,
                    "name": "David & Krista Brewster",
                    "address": {
                        "street": "150 Malone Road",
                        "unit": None,
                        "city": "Lenoir City",
                        "state": "TN",
                        "zip": "37771",
                        "country": "USA",
                        "latitude": 35.8162496,
                        "longitude": -84.3693237
                    },
                    "customFields": [
                        {
                            "typeId": 191000023,
                            "name": "  Salt Settings",
                            "value": "2.7"
                        },
                        {
                            "typeId": 173000905,
                            "name": " Float Cup",
                            "value": "7 3/4"
                        },
                        {
                            "typeId": 173000902,
                            "name": "  Brine Well Conversion",
                            "value": "False"
                        },
                        {
                            "typeId": 7041,
                            "name": "     Client #",
                            "value": "10028"
                        }
                    ],
                    "createdOn": "0001-01-01T00:00:00Z",
                    "createdById": 0,
                    "modifiedOn": "2023-05-10T06:46:58.6020699Z",
                    "mergedToId": None,
                    "zoneId": 271440915,
                    "externalData": None
                }
            ]
        }
        mock_response.json.return_value = fake_json
        mock_get.return_value = mock_response
        mock_delay.ready.return_value = True

        # Call the function
        get_service_titan_locations("company_id", "tenant", "option1")

        # Assertions
        mock_access_token.assert_called_once_with("company_id")
        mock_get.assert_called_once_with(
            url="https://api.servicetitan.io/crm/v2/tenant/tenant/locations?page=1&pageSize=2500",
            headers="dummy_access_token",
            timeout=10,
        )
        mock_delay.assert_called_once_with(
            fake_json["data"], "company_id"
        )

        # Reset the call count of mock_delay
        mock_delay.reset_mock()

        # Call the function
        get_service_titan_locations("company_id", "tenant", "option3")

        # Assertions
        assert mock_access_token.call_count == 2
        assert mock_get.call_count == 2
        for i in range(len(fake_json["data"])):
            fake_json["data"][i]["name"] = " "
        mock_delay.assert_called_once_with(
            fake_json["data"], "company_id"
        )

    @patch("data.syncClients.get_service_titan_access_token")
    @patch("data.syncClients.update_clients_with_last_day_of_equipment_installation.delay")
    @patch("requests.get")
    def test_get_service_titan_equipment(self, mock_get, mock_update_clients_with_last_day_of_equipment_installation, mock_access_token):
        mock_access_token.return_value = "dummy_access_token"

        # Mock the API response and its JSON data
        mock_response = Mock()
        fake_json = {
            "page": 1,
            "pageSize": 2,
            "hasMore": False,
            "totalCount": None,
            "data": [
                {
                    "id": 241300001,
                    "equipmentId": None,
                    "locationId": 240200001,
                    "customerId": 240000001,
                    "name": "K-5A-VP",
                    "installedOn": "2018-10-12T00:00:00Z",
                    "serialNumber": "3383025",
                    "memo": "Under Kitchen Sink-no cover, 3 Gal Air Tank, Leak Block Sensor & Leak Alarm",
                    "manufacturer": None,
                    "model": "K-5A-VP",
                    "cost": 0.0000000000000000000,
                    "manufacturerWarrantyStart": "2018-10-12T00:00:00Z",
                    "manufacturerWarrantyEnd": None,
                    "serviceProviderWarrantyStart": "2018-10-12T00:00:00Z",
                    "serviceProviderWarrantyEnd": "2019-10-11T00:00:00Z"
                },
                {
                    "id": 241300002,
                    "equipmentId": None,
                    "locationId": 240200002,
                    "customerId": 240000002,
                    "name": "K-5A",
                    "installedOn": "2018-10-11T00:00:00Z",
                    "serialNumber": "3383018",
                    "memo": "Basement Garage, 4 Gallon Air Tank on Wall with Booster Pump, No Alarm",
                    "manufacturer": None,
                    "model": "K-5A",
                    "cost": 0.0000000000000000000,
                    "manufacturerWarrantyStart": "2018-10-11T00:00:00Z",
                    "manufacturerWarrantyEnd": "2028-10-11T00:00:00Z",
                    "serviceProviderWarrantyStart": "2018-10-11T00:00:00Z",
                    "serviceProviderWarrantyEnd": "2019-10-11T00:00:00Z"
                }
            ]
        }
        mock_response.json.return_value = fake_json
        mock_get.return_value = mock_response

        # Call the function
        get_service_titan_equipment("company_id", "tenant")

        # Assertions
        mock_access_token.assert_called_once_with("company_id")
        mock_get.assert_called_once_with(
            url="https://api.servicetitan.io/equipmentsystems/v2/tenant/tenant/installed-equipment?page=1&pageSize=2500",
            headers="dummy_access_token",
            timeout=10
        )
        mock_update_clients_with_last_day_of_equipment_installation.assert_called_once_with(
            "company_id", fake_json["data"]
        )

    @patch("data.syncClients.get_service_titan_locations")
    @patch("data.syncClients.delete_extra_clients.delay")
    @patch("data.syncClients.get_service_titan_equipment.delay")
    @patch("data.syncClients.do_it_all.delay")
    @patch("data.syncClients.get_service_titan_customers.delay")
    @patch("data.syncClients.get_service_titan_invoices.delay")
    @patch("data.utils.verify_address.delay")
    def test_complete_service_titan_sync(self, mock_verify_address, mock_get_service_titan_invoices, mock_get_service_titan_customers, mock_do_it_all, mock_get_service_titan_equipment, mock_delete_extra_clients, mock_get_service_titan_locations):
        # Call the function
        complete_service_titan_sync(self.company.id, "task_id")

        # Assertions
        mock_get_service_titan_locations.assert_called_once_with(
            self.company.id, self.company.tenant_id, self.company.service_titan_customer_sync_option)
        mock_delete_extra_clients.assert_called_once_with(
            self.company.id, "task_id")
        mock_get_service_titan_equipment.assert_called_once_with(
            self.company.id, self.company.tenant_id)
        mock_do_it_all.assert_called_once_with(
            self.company.id)
        mock_get_service_titan_customers.assert_not_called()
        mock_get_service_titan_invoices.assert_called_once_with(
            self.company.id, self.company.tenant_id)
        assert mock_verify_address.call_count == 2

        # Call the function with automated = True and option1

        complete_service_titan_sync(
            self.company_option1.id, "task_id", automated=True)

        # Assertions
        assert mock_do_it_all.call_count == 1
        mock_get_service_titan_customers.assert_called_once_with(
            self.company_option1.id, self.company_option1.tenant_id)

    @patch("data.models.Client.objects.filter")
    @patch("accounts.models.Company.objects.get")
    def test_update_clients_with_last_day_of_equipment_installation(self, mock_company, mock_client):
        # Mock the Company and Client objects
        mock_company.return_value = Mock()

        mock_queryset = QuerySet(model=Client)
        mock_queryset.update = Mock()
        mock_client.return_value = mock_queryset

        # Define the equipment data
        equipment = [
            {
                "id": 241300001,
                "equipmentId": None,
                "locationId": 240200001,
                "customerId": 240000001,
                "name": "K-5A-VP",
                "installedOn": "2018-10-12T00:00:00Z",
                "serialNumber": "3383025",
                "memo": "Under Kitchen Sink-no cover, 3 Gal Air Tank, Leak Block Sensor & Leak Alarm",
                "manufacturer": None,
                "model": "K-5A-VP",
                "cost": 0.0000000000000000000,
                "manufacturerWarrantyStart": "2018-10-12T00:00:00Z",
                "manufacturerWarrantyEnd": None,
                "serviceProviderWarrantyStart": "2018-10-12T00:00:00Z",
                "serviceProviderWarrantyEnd": "2019-10-11T00:00:00Z"
            },
            {
                "id": 241300002,
                "equipmentId": None,
                "locationId": 240200002,
                "customerId": 240000002,
                "name": "K-5A",
                "installedOn": "2018-10-11T00:00:00Z",
                "serialNumber": "3383018",
                "memo": "Basement Garage, 4 Gallon Air Tank on Wall with Booster Pump, No Alarm",
                "manufacturer": None,
                "model": "K-5A",
                "cost": 0.0000000000000000000,
                "manufacturerWarrantyStart": "2018-10-11T00:00:00Z",
                "manufacturerWarrantyEnd": "2028-10-11T00:00:00Z",
                "serviceProviderWarrantyStart": "2018-10-11T00:00:00Z",
                "serviceProviderWarrantyEnd": "2019-10-11T00:00:00Z"
            }
        ]

        # Call the function
        update_clients_with_last_day_of_equipment_installation(
            "company_id", equipment)

        # Assertions
        mock_company.assert_called_once_with(id="company_id")

        # TODO: Assert that the fields are updated correctly

    @patch("data.syncClients.get_service_titan_access_token")
    @patch("data.syncClients.update_client_list.delay")
    @patch("requests.get")
    def test_get_service_titan_customers(self, mock_get, mock_update_client_list, mock_access_token):
        mock_access_token.return_value = "dummy_access_token"

        # Mock the API response and its JSON data
        mock_response = Mock()
        fake_json = {
            "hasMore": False,
            "continueFrom": "ARfeFsjsaNdIpNpYDgAAAAAXJw8U",
            "data": [
                {
                    "customerId": 240000012,
                    "active": True,
                    "modifiedOn": "2019-11-14T10:24:07.4726935Z",
                    "phoneSettings": {
                        "phoneNumber": "8659888198",
                        "doNotText": False
                    },
                    "id": 240400002,
                    "type": "Phone",
                    "value": "8659888198",
                    "memo": "Matt Hurst"
                },
                {
                    "customerId": 240000033,
                    "active": True,
                    "modifiedOn": "2019-11-14T10:24:07.4726935Z",
                    "phoneSettings": {
                        "phoneNumber": "8654081316",
                        "doNotText": False
                    },
                    "id": 240400003,
                    "type": "Phone",
                    "value": "8654081316",
                    "memo": "HomePhone"
                }
            ]
        }
        mock_response.json.return_value = fake_json
        mock_get.return_value = mock_response

        # Call the function
        get_service_titan_customers("company_id", "tenant")

        # Assertions
        mock_access_token.assert_called_once_with("company_id")
        mock_get.assert_called_once_with(
            url="https://api.servicetitan.io/crm/v2/tenant/tenant/export/customers/contacts?from=",
            headers="dummy_access_token",
            timeout=10
        )
        mock_update_client_list.assert_called_once_with(
            fake_json["data"])

    @patch("accounts.models.Company.objects.get")
    @patch("data.models.Client.objects.filter")
    @patch("payments.models.ServiceTitanInvoice.objects.filter")
    @patch("data.syncClients.get_service_titan_access_token")
    @patch("data.syncClients.get_customer_since_data_from_invoices.delay")
    @patch("data.syncClients.save_invoices.delay")
    @patch("requests.get")
    def test_get_service_titan_invoices(self, mock_get, mock_save_invoices, mock_get_customer_since_data_from_invoices, mock_access_token, mock_invoice_filter, mock_client, mock_company):
        mock_access_token.return_value = "dummy_access_token"
        mock_company.return_value = Mock()

        mock_queryset = QuerySet(model=Client)
        mock_queryset.update = Mock()
        mock_client.return_value = mock_queryset

        # Create a mock QuerySet and set its exists method return value
        mock_invoice_qs = mock_invoice_filter.return_value
        mock_invoice_qs.exists.return_value = False

        # Mock the API response and its JSON data
        mock_response = Mock()
        fake_json = {
            "page": 10,
            "pageSize": 5000,
            "hasMore": False,
            "totalCount": None,
            "data": [
                {
                    "id": 303350355,
                    "syncStatus": "Exported",
                    "summary": None,
                    "referenceNumber": "680999",
                    "invoiceDate": "2022-02-14T00:00:00Z",
                    "dueDate": "2022-02-14T00:00:00Z",
                    "subTotal": "0.00",
                    "salesTax": "0.00",
                    "salesTaxCode": {
                        "id": 18050,
                        "name": "Loudon County Sales Tax",
                        "taxRate": 0.0900000000
                    },
                    "total": "0.00",
                    "balance": "0.00",
                    "invoiceType": None,
                    "customer": {
                        "id": 289969909,
                        "name": "On Call Service (Service)"
                    },
                    "customerAddress": {
                        "street": "1767 Kevin Lane",
                        "unit": None,
                        "city": "Lenoir City",
                        "state": "TN",
                        "zip": "37772",
                        "country": "USA"
                    },
                    "location": {
                        "id": 289969912,
                        "name": "On Call Service (Service)"
                    },
                    "locationAddress": {
                        "street": "1767 Kevin Lane",
                        "unit": None,
                        "city": "Lenoir City",
                        "state": "TN",
                        "zip": "37772",
                        "country": "USA"
                    },
                    "businessUnit": {
                        "id": 1026,
                        "name": "Residential Service"
                    },
                    "termName": "Due Upon Receipt",
                    "createdBy": "mark haste",
                    "batch": {
                        "id": 303633281,
                        "number": "7475",
                        "name": "ON Call Service Bypass 02/15/2022"
                    },
                    "depositedOn": "2022-02-15T20:33:31.0005557Z",
                    "createdOn": "2022-02-11T12:42:44.3752813Z",
                    "modifiedOn": "2022-02-15T20:33:37.0187647Z",
                    "adjustmentToId": None,
                    "job": {
                        "id": 303350352,
                        "number": "680999",
                        "type": "On Call Service (Friday Night)"
                    },
                    "projectId": None,
                    "royalty": {
                        "status": "Pending",
                        "date": None,
                        "sentOn": None,
                        "memo": None
                    },
                    "employeeInfo": {
                        "id": 279460619,
                        "name": "mark haste",
                        "modifiedOn": "2023-07-07T19:54:00.4865896Z"
                    },
                    "commissionEligibilityDate": None,
                    "items": [
                        {
                            "id": 303350359,
                            "description": "On Call Service - 5pm - Midnight Friday",
                            "quantity": "1.0000000000000000000",
                            "cost": "0.0000000000",
                            "totalCost": "0.00",
                            "inventoryLocation": None,
                            "price": "0.00",
                            "type": "Service",
                            "skuName": "X-CALL (Friday Evening)",
                            "skuId": 288173174,
                            "total": "0.00",
                            "inventory": False,
                            "taxable": False,
                            "generalLedgerAccount": {
                                "id": 231145,
                                "name": "Employee Bonus",
                                "number": "6555",
                                "type": "Expense",
                                "detailType": "Expense"
                            },
                            "costOfSaleAccount": None,
                            "assetAccount": None,
                            "membershipTypeId": 0,
                            "itemGroup": None,
                            "displayName": "On Call Service (Friday Evening)",
                            "soldHours": 0.00000,
                            "modifiedOn": "2022-02-11T12:42:44.7889999Z",
                            "serviceDate": "2022-02-11T00:00:00Z",
                            "order": 1,
                            "businessUnit": {
                                "id": 1026,
                                "name": "Residential Service"
                            }
                        }
                    ],
                    "customFields": None
                },
                {
                    "id": 303350483,
                    "syncStatus": "Exported",
                    "summary": "No calls ",
                    "referenceNumber": "681000",
                    "invoiceDate": "2022-02-13T00:00:00Z",
                    "dueDate": "2022-02-13T00:00:00Z",
                    "subTotal": "0.00",
                    "salesTax": "0.00",
                    "salesTaxCode": {
                        "id": 18050,
                        "name": "Loudon County Sales Tax",
                        "taxRate": 0.0900000000
                    },
                    "total": "25.69",
                    "balance": "0.00",
                    "invoiceType": None,
                    "customer": {
                        "id": 286423152,
                        "name": "On Call Service (Phone Support)"
                    },
                    "customerAddress": {
                        "street": "1767 Kevin Lane",
                        "unit": None,
                        "city": "Lenoir City",
                        "state": "TN",
                        "zip": "37772",
                        "country": "USA"
                    },
                    "location": {
                        "id": 286423154,
                        "name": "On Call Service (Phone Support)"
                    },
                    "locationAddress": {
                        "street": "1767 Kevin Lane",
                        "unit": None,
                        "city": "Lenoir City",
                        "state": "TN",
                        "zip": "37772",
                        "country": "USA"
                    },
                    "businessUnit": {
                        "id": 1026,
                        "name": "Residential Service"
                    },
                    "termName": "Due Upon Receipt",
                    "createdBy": "mark haste",
                    "batch": {
                        "id": 303633281,
                        "number": "7475",
                        "name": "ON Call Service Bypass 02/15/2022"
                    },
                    "depositedOn": "2022-02-15T20:33:31.0005557Z",
                    "createdOn": "2023-04-21T12:43:52.9049113Z",
                    "modifiedOn": "2022-02-15T20:33:37.1005418Z",
                    "adjustmentToId": None,
                    "job": {
                        "id": 303350480,
                        "number": "681000",
                        "type": "On Call Service (Saturday)"
                    },
                    "projectId": None,
                    "royalty": {
                        "status": "Pending",
                        "date": None,
                        "sentOn": None,
                        "memo": None
                    },
                    "employeeInfo": {
                        "id": 279460619,
                        "name": "mark haste",
                        "modifiedOn": "2023-07-07T19:54:00.4865896Z"
                    },
                    "commissionEligibilityDate": None,
                    "items": [
                        {
                            "id": 303350487,
                            "description": "On Call Service - Saturday Technician",
                            "quantity": "1.0000000000000000000",
                            "cost": "0.0000000000",
                            "totalCost": "0.00",
                            "inventoryLocation": None,
                            "price": "0.00",
                            "type": "Service",
                            "skuName": "X-CALL (Saturday Technician)",
                            "skuId": 286424176,
                            "total": "0.00",
                            "inventory": False,
                            "taxable": False,
                            "generalLedgerAccount": {
                                "id": 231145,
                                "name": "Employee Bonus",
                                "number": "6555",
                                "type": "Expense",
                                "detailType": "Expense"
                            },
                            "costOfSaleAccount": None,
                            "assetAccount": None,
                            "membershipTypeId": 0,
                            "itemGroup": None,
                            "displayName": "On Call Saturday Service (Technician)",
                            "soldHours": 0.00000,
                            "modifiedOn": "2022-02-11T12:43:53.2447919Z",
                            "serviceDate": "2022-02-12T00:00:00Z",
                            "order": 1,
                            "businessUnit": {
                                "id": 1026,
                                "name": "Residential Service"
                            }
                        }
                    ],
                    "customFields": None
                },
                {
                    "id": 303350483,
                    "syncStatus": "Exported",
                    "summary": "No calls ",
                    "referenceNumber": "681000",
                    "invoiceDate": "2022-02-13T00:00:00Z",
                    "dueDate": "2022-02-13T00:00:00Z",
                    "subTotal": "0.00",
                    "salesTax": "0.00",
                    "salesTaxCode": {
                        "id": 18050,
                        "name": "Loudon County Sales Tax",
                        "taxRate": 0.0900000000
                    },
                    "total": "25.69",
                    "balance": "0.00",
                    "invoiceType": None,
                    "customerAddress": {
                        "street": "1767 Kevin Lane",
                        "unit": None,
                        "city": "Lenoir City",
                        "state": "TN",
                        "zip": "37772",
                        "country": "USA"
                    },
                    "location": {
                        "id": 286423154,
                        "name": "On Call Service (Phone Support)"
                    },
                    "locationAddress": {
                        "street": "1767 Kevin Lane",
                        "unit": None,
                        "city": "Lenoir City",
                        "state": "TN",
                        "zip": "37772",
                        "country": "USA"
                    },
                    "businessUnit": {
                        "id": 1026,
                        "name": "Residential Service"
                    },
                    "termName": "Due Upon Receipt",
                    "createdBy": "mark haste",
                    "batch": {
                        "id": 303633281,
                        "number": "7475",
                        "name": "ON Call Service Bypass 02/15/2022"
                    },
                    "depositedOn": "2022-02-15T20:33:31.0005557Z",
                    "createdOn": "2023-04-21T12:43:52.9049113Z",
                    "modifiedOn": "2022-02-15T20:33:37.1005418Z",
                    "adjustmentToId": None,
                    "job": {
                        "id": 303350480,
                        "number": "681000",
                        "type": "On Call Service (Saturday)"
                    },
                    "projectId": None,
                    "royalty": {
                        "status": "Pending",
                        "date": None,
                        "sentOn": None,
                        "memo": None
                    },
                    "employeeInfo": {
                        "id": 279460619,
                        "name": "mark haste",
                        "modifiedOn": "2023-07-07T19:54:00.4865896Z"
                    },
                    "commissionEligibilityDate": None,
                    "items": [
                        {
                            "id": 303350487,
                            "description": "On Call Service - Saturday Technician",
                            "quantity": "1.0000000000000000000",
                            "cost": "0.0000000000",
                            "totalCost": "0.00",
                            "inventoryLocation": None,
                            "price": "0.00",
                            "type": "Service",
                            "skuName": "X-CALL (Saturday Technician)",
                            "skuId": 286424176,
                            "total": "0.00",
                            "inventory": False,
                            "taxable": False,
                            "generalLedgerAccount": {
                                "id": 231145,
                                "name": "Employee Bonus",
                                "number": "6555",
                                "type": "Expense",
                                "detailType": "Expense"
                            },
                            "costOfSaleAccount": None,
                            "assetAccount": None,
                            "membershipTypeId": 0,
                            "itemGroup": None,
                            "displayName": "On Call Saturday Service (Technician)",
                            "soldHours": 0.00000,
                            "modifiedOn": "2022-02-11T12:43:53.2447919Z",
                            "serviceDate": "2022-02-12T00:00:00Z",
                            "order": 1,
                            "businessUnit": {
                                "id": 1026,
                                "name": "Residential Service"
                            }
                        }
                    ],
                    "customFields": None
                },
                {
                    "id": 303350483,
                    "syncStatus": "Exported",
                    "summary": "No calls ",
                    "referenceNumber": "681000",
                    "invoiceDate": "2022-02-13T00:00:00Z",
                    "dueDate": "2022-02-13T00:00:00Z",
                    "subTotal": "0.00",
                    "salesTax": "0.00",
                    "salesTaxCode": {
                        "id": 18050,
                        "name": "Loudon County Sales Tax",
                        "taxRate": 0.0900000000
                    },
                    "total": "25.69",
                    "balance": "0.00",
                    "invoiceType": None,
                    "customer": {
                        "id": 286423152,
                        "name": "On Call Service (Phone Support)"
                    },
                    "customerAddress": {
                        "street": "1767 Kevin Lane",
                        "unit": None,
                        "city": "Lenoir City",
                        "state": "TN",
                        "zip": "37772",
                        "country": "USA"
                    },
                    "location": {
                        "id": 286423154,
                        "name": "On Call Service (Phone Support)"
                    },
                    "locationAddress": {
                        "street": "1767 Kevin Lane",
                        "unit": None,
                        "city": "Lenoir City",
                        "state": "TN",
                        "zip": "37772",
                        "country": "USA"
                    },
                    "businessUnit": {
                        "id": 1026,
                        "name": "Residential Service"
                    },
                    "termName": "Due Upon Receipt",
                    "createdBy": "mark haste",
                    "batch": {
                        "id": 303633281,
                        "number": "7475",
                        "name": "ON Call Service Bypass 02/15/2022"
                    },
                    "depositedOn": "2022-02-15T20:33:31.0005557Z",
                    "createdOn": None,
                    "modifiedOn": "2022-02-15T20:33:37.1005418Z",
                    "adjustmentToId": None,
                    "job": {
                        "id": 303350480,
                        "number": "681000",
                        "type": "On Call Service (Saturday)"
                    },
                    "projectId": None,
                    "royalty": {
                        "status": "Pending",
                        "date": None,
                        "sentOn": None,
                        "memo": None
                    },
                    "employeeInfo": {
                        "id": 279460619,
                        "name": "mark haste",
                        "modifiedOn": "2023-07-07T19:54:00.4865896Z"
                    },
                    "commissionEligibilityDate": None,
                    "items": [
                        {
                            "id": 303350487,
                            "description": "On Call Service - Saturday Technician",
                            "quantity": "1.0000000000000000000",
                            "cost": "0.0000000000",
                            "totalCost": "0.00",
                            "inventoryLocation": None,
                            "price": "0.00",
                            "type": "Service",
                            "skuName": "X-CALL (Saturday Technician)",
                            "skuId": 286424176,
                            "total": "0.00",
                            "inventory": False,
                            "taxable": False,
                            "generalLedgerAccount": {
                                "id": 231145,
                                "name": "Employee Bonus",
                                "number": "6555",
                                "type": "Expense",
                                "detailType": "Expense"
                            },
                            "costOfSaleAccount": None,
                            "assetAccount": None,
                            "membershipTypeId": 0,
                            "itemGroup": None,
                            "displayName": "On Call Saturday Service (Technician)",
                            "soldHours": 0.00000,
                            "modifiedOn": "2022-02-11T12:43:53.2447919Z",
                            "serviceDate": "2022-02-12T00:00:00Z",
                            "order": 1,
                            "businessUnit": {
                                "id": 1026,
                                "name": "Residential Service"
                            }
                        }
                    ],
                    "customFields": None
                }
            ]
        }
        # only one invoice because one has an amount of 0, one has createdOn = None,
        # and one does not have customer in it
        mock_invoices = [
            {
                "id": 303350483,
                "customer": 286423152,
                "createdOn": "2023-04-21",
                "amount": '25.69',
            }
        ]
        mock_response.json.return_value = fake_json
        mock_get.return_value = mock_response

        # Call the function
        get_service_titan_invoices("company_id", "tenant")

        # Assertions
        mock_access_token.assert_called_once_with("company_id")
        mock_get.assert_called_once_with(
            url="https://api.servicetitan.io/accounting/v2/tenant/tenant/invoices?page=1&pageSize=2500",
            headers="dummy_access_token",
            timeout=15
        )
        mock_save_invoices.assert_called_once_with(
            "company_id", mock_invoices)

        mock_get_customer_since_data_from_invoices.assert_called_once_with(
            "company_id"
        )

        # Create a mock QuerySet and set its exists method return value
        mock_invoice_qs = mock_invoice_filter.return_value
        mock_invoice_qs.exists.return_value = True
        get_service_titan_invoices("company_id", "tenant")
        assert "createdOnOrAfter" in mock_get.call_args[1]["url"]

    @patch("data.models.Client.objects.filter")
    @patch("payments.models.ServiceTitanInvoice.objects")
    @patch("accounts.models.Company.objects.get")
    def test_save_invoices(self, mock_company, mock_invoice, mock_client):
        # Mock the Company and Client objects
        mock_company.return_value = Mock()
        mock_queryset = QuerySet(model=Client)
        mock_queryset.update = Mock()
        mock_client.return_value = mock_queryset

        # Mock the ServiceTitanInvoice.objects and its methods
        mock_invoice.exists.return_value = False

        # Define the invoice data
        invoices = [
            {
                "id": 303350483,
                "customer": 240000001,
                "createdOn": "2023-04-21",
                "amount": '25.69',
            },
            {
                "id": 384053303,
                "customer": 240000002,
                "createdOn": "2022-10-12",
                "amount": '12303.24',
            }
        ]
        # invoices_to_create = [
        #     ServiceTitanInvoice(
        #         id=303350483,
        #         amount='25.69',
        #         client=self.client1,
        #         created_on=datetime.strptime("2023-04-21", "%Y-%m-%d").date()
        #     ),
        #     ServiceTitanInvoice(
        #         id=384053303,
        #         amount='12303.24',
        #         client=self.client2,
        #         created_on=datetime.strptime("2022-10-12", "%Y-%m-%d").date()
        #     )
        # ]

        # Call the function
        save_invoices("company_id", invoices)

        # Assertions
        mock_company.assert_called_once_with(id="company_id")
        assert mock_client.call_count == 2
        # TODO: Need to figure out way to test this part
        # if not ServiceTitanInvoice.objects.filter(id=invoice["id"]).exists():
        # and actually add ServiceTitanInvoice to invoices_to_create
        mock_invoice.bulk_create.assert_called_once_with([])

    @patch("payments.models.ServiceTitanInvoice.objects")
    @patch("data.models.Client.objects.filter")
    @patch("accounts.models.Company.objects.get")
    def test_get_customer_since_data_from_invoices(self, mock_company, mock_client, mock_invoice):
        # Mock the Company and Client objects
        mock_company.return_value = Mock()
        mock_queryset = QuerySet(model=Client)

        mock_client.return_value = mock_queryset

        # Call the function
        get_customer_since_data_from_invoices("company_id=self.company.id")

        # Assertions
        mock_company.assert_called_once_with(id="company_id")
        mock_client.assert_called_once_with(company=self.company)
        assert mock_invoice.filter.call_count == 2

    @patch("payments.models.ServiceTitanInvoice.objects.filter")
    @patch("data.models.Client.objects.filter")
    @patch("accounts.models.Company.objects.get")
    def test_get_customer_since_data_from_invoices(self, mock_company, mock_client, mock_invoice_filter):
        # Mock the Company and Client objects
        mock_company.return_value = Mock()
        mock_client_queryset = QuerySet(model=Client)
        mock_client.return_value = mock_client_queryset
        mock_client_queryset.__iter__ = iter(
            [self.client1, self.client2])

        # Prepare invoice queryset and configure invoice amounts
        mock_invoice_queryset = QuerySet(model=ServiceTitanInvoice)
        mock_invoice_filter.return_value = mock_invoice_queryset
        # TODO: Figure out why this is not working
        mock_invoice_queryset.__iter__ = iter(
            [self.invoice1, self.invoice2])

        # Call the function
        get_customer_since_data_from_invoices("company_id")

        # Retrieve the updated client from the database
        updated_client = Client.objects.get(serv_titan_id=240000001)

        # Assertions
        mock_company.assert_called_once_with(id="company_id")
        mock_client.assert_called()
        mock_invoice_filter.assert_called_with(
            client=self.client2)
        assert mock_invoice_filter.call_count == 2
        # assert updated_client.service_titan_customer_since == self.invoice2.created_on
        # assert updated_client.service_titan_lifetime_revenue == (
        #     self.invoice1.amount + self.invoice2.amount
        # )
