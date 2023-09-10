from django.test import TestCase
import pytest
from django.urls import reverse
from datetime import datetime, timedelta
from rest_framework.test import APIClient
from accounts.models import Company, CustomUser
from accounts.serializers import MyTokenObtainPairSerializer
from data.models import Client, ClientUpdate, HomeListing, Realtor, ZipCode
from payments.models import ServiceTitanInvoice


@pytest.fixture
def api_client():
    return APIClient()


def get_token():
    serializer = MyTokenObtainPairSerializer(
        data={"email": "testuser@example.com", "password": "testpassword"}
    )
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data["access_token"]


def get_month_names():
    first_day_of_current_month = datetime.now().replace(day=1)
    current_month_name = first_day_of_current_month.strftime("%B")

    # Calculate the last day of the previous month
    last_day_of_last_month = first_day_of_current_month - \
        timedelta(days=1)

    # Calculate the first day of the previous month
    first_day_of_last_month = last_day_of_last_month.replace(day=1)

    # Get the name of the previous month as a string (full month name)
    previous_month_name = first_day_of_last_month.strftime("%B")

    # Calculate the last day of the previous month
    last_day_of_two_months_ago = first_day_of_last_month - \
        timedelta(days=1)

    # Get the name of the previous month as a string (full month name)
    two_months_ago_name = last_day_of_two_months_ago.strftime("%B")

    return current_month_name, previous_month_name, two_months_ago_name


class CompanyDashboardView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(name="Test Company")
        company2 = Company.objects.create(name="Test Company 2")
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            company=self.company,
            is_verified=True,
            date_joined=datetime.today()-timedelta(days=365),
        )
        self.token = get_token()

        current_date = datetime.today()
        client = Client.objects.create(
            company=self.company, name="client1", service_titan_customer_since=current_date-timedelta(days=360), address="123 Main St")
        client2 = Client.objects.create(
            company=company2, name="client2", service_titan_customer_since=current_date-timedelta(days=360), address="456 Main St")
        # Get the first day of the current month
        first_day_of_current_month = current_date.replace(day=1)

        # Get the last day of the previous month by subtracting one day from the first day of the current month
        last_day_of_previous_month = first_day_of_current_month - \
            timedelta(days=1)

        # Get the first day of the previous month
        first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

        # Get the last day of the month two before this one
        last_day_of_two_months_prior = first_day_of_previous_month - \
            timedelta(days=1)

        Client.objects.create(
            company=self.company, name="client3", service_titan_customer_since=current_date, address="123 Main St")
        Client.objects.create(
            company=self.company, name="client4", service_titan_customer_since=last_day_of_two_months_prior, address="123 Main St")
        # TODO: Create clients with join dates of a couple months ago and then of less than a year ago
        # but in the previous year and test that the math works out correctly

        attributed_invoice1 = ServiceTitanInvoice.objects.create(
            client=client, amount=250.0, attributed=True, id="1", created_on=last_day_of_previous_month
        )
        attributed_invoice2 = ServiceTitanInvoice.objects.create(
            client=client, amount=100.0, attributed=True, id="2", created_on=last_day_of_two_months_prior
        )
        unattributed_invoice = ServiceTitanInvoice.objects.create(
            client=client, amount=150.0, attributed=False, id="3", created_on=last_day_of_two_months_prior
        )
        # Need these to make sure other company invoices are not being shown to current user
        diff_company_invoice = ServiceTitanInvoice.objects.create(
            client=client2, amount=100.0, attributed=True, id="4", created_on=last_day_of_previous_month
        )
        diff_company_invoice_2 = ServiceTitanInvoice.objects.create(
            client=client2, amount=100.0, attributed=True, id="5", created_on=last_day_of_two_months_prior
        )

        for_sale_client_update = ClientUpdate.objects.create(
            client=client, status="House For Sale", date=last_day_of_previous_month)
        recently_sold_client_update = ClientUpdate.objects.create(
            client=client, status="House Recently Sold (6)", date=last_day_of_two_months_prior)

    def test_company_dashboard_view(self):
        # Make a request to the CompanyDashboardView API view.
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.get(reverse("company-dashboard"), **headers)

        # Validate the response status code.
        assert response.status_code == 200

        # Validate the response data.
        data = response.json()

        assert "totalRevenue" in data
        assert "monthsActive" in data
        assert "revenueByMonth" in data
        assert "forSaleByMonth" in data
        assert "recentlySoldByMonth" in data
        assert "customerRetention" in data
        assert "clientsAcquired" in data
        assert "clientsAcquiredByMonth" in data

        # Validate the format of the response data.
        assert isinstance(data["totalRevenue"], float)
        assert isinstance(data["monthsActive"], int)
        assert isinstance(data["revenueByMonth"], dict)
        assert isinstance(data["forSaleByMonth"], dict)
        assert isinstance(data["recentlySoldByMonth"], dict)
        assert isinstance(data["customerRetention"], dict)
        assert isinstance(data["clientsAcquired"], int)
        assert isinstance(data["clientsAcquiredByMonth"], dict)

        current_month, previous_month, two_months_ago = get_month_names()

        assert data["totalRevenue"] == 350
        assert data["monthsActive"] == 13
        assert data["clientsAcquired"] == 2

        assert current_month in data["forSaleByMonth"]

        assert data["revenueByMonth"][previous_month] == 250.0
        assert data["forSaleByMonth"][previous_month] == 1
        assert data["recentlySoldByMonth"][previous_month] == 0
        assert data["clientsAcquiredByMonth"][previous_month] == 0

        assert data["revenueByMonth"][two_months_ago] == 100.0
        assert data["forSaleByMonth"][two_months_ago] == 0
        assert data["recentlySoldByMonth"][two_months_ago] == 1
        assert data["clientsAcquiredByMonth"][two_months_ago] == 1


class ZapierClientView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(name="Test Company")
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            company=self.company,
            is_verified=True,
            date_joined=datetime.today()-timedelta(days=370),
        )
        self.token = get_token()

        client = Client.objects.create(
            company=self.company, service_titan_customer_since=datetime.today()-timedelta(days=360))

    def test_zapier_create_client_view(self):
        # Make a request to the ZapierClientView API view.
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        data = {
            "name": "Test Client",
            "address": "123 Test Street",
            "city": "Test City",
            "state": "Test State",
            "zip_code": "12345",
            "phone_number": "1234567890",
        }
        response = self.client.post(
            reverse("zapier-client-create"), data=data, **headers)

        # Validate the response status code.
        assert response.status_code == 200

        # Refresh database to see if object was created successfully
        self.company.refresh_from_db()

        assert Client.objects.filter(company=self.company).count() == 2
        assert Client.objects.filter(
            company=self.company, name="Test Client").exists() == True


class RealtorView(TestCase):
    def setUp(self):
        self.zip_code_1 = ZipCode.objects.create(zip_code="12345")
        self.zip_code_2 = ZipCode.objects.create(zip_code="67890")
        self.company = Company.objects.create(name="Test Company")
        self.company.service_area_zip_codes.add(self.zip_code_1)
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            company=self.company,
            is_verified=True,
            date_joined=datetime.today()-timedelta(days=370),
        )

        self.token = get_token()

        self.realtor_1 = Realtor.objects_with_listing_count.create(
            name="Realtor 1", company="Test Realty 1")
        self.realtor_2 = Realtor.objects_with_listing_count.create(
            name="Realtor 2", company="Test Realty 2")

        HomeListing.objects.create(
            zip_code=self.zip_code_1, address="123 Lane", status="House For Sale", realtor=self.realtor_1)
        HomeListing.objects.create(
            zip_code=self.zip_code_1, address="456 Lane", status="House For Sale", realtor=self.realtor_1)
        HomeListing.objects.create(
            zip_code=self.zip_code_2, address="654 Lane", status="House For Sale", realtor=self.realtor_1)
        HomeListing.objects.create(
            zip_code=self.zip_code_2, address="789 Street", status="House For Sale", realtor=self.realtor_2)

    def test_get_realtors_by_service_area(self):
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

        # Make a request to your view
        response = self.client.get(reverse("realtors"), **headers)

        # Check if the response status is 200 OK
        assert response.status_code == 200
        data = response.data['results']['data']

        # Check if the realtor with the most listings comes first, and that only listings in the service area are counted
        self.assertEqual(data[0]['name'], "Realtor 1")
        self.assertEqual(data[0]['listing_count'], 2)

        # Check if Realtor 2 is not present since it's not in the service zip code area
        realtor_names = [realtor['name'] for realtor in data]
        self.assertNotIn("Realtor 2", realtor_names)
