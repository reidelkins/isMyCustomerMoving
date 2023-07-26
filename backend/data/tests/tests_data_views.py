from django.test import TestCase
import pytest
from django.urls import reverse
from datetime import datetime, timedelta
from rest_framework.test import APIClient
from accounts.models import Company, CustomUser
from accounts.serializers import MyTokenObtainPairSerializer
from data.models import Client, ClientUpdate
from payments.models import ServiceTitanInvoice


@pytest.fixture
def api_client():
    return APIClient()


class CompanyDashboardView(TestCase):
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
        self.token = self.get_token()

        client = Client.objects.create(
            company=self.company, service_titan_customer_since=datetime.today()-timedelta(days=360))

        attributed_invoice = ServiceTitanInvoice.objects.create(
            client=client, amount=250.0, attributed=True, id="1"
        )
        unattributed_invoice = ServiceTitanInvoice.objects.create(
            client=client, amount=100.0, attributed=False, id="2"
        )

        for_sale_client_update = ClientUpdate.objects.create(
            client=client, status="House For Sale", date=datetime.today()-timedelta(days=30))
        recently_sold_client_update = ClientUpdate.objects.create(
            client=client, status="House For Sale (6)", date=datetime.today()-timedelta(days=60))

    def get_token(self):
        serializer = MyTokenObtainPairSerializer(
            data={"email": "testuser@example.com", "password": "testpassword"}
        )
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data["access_token"]

    def test_company_dashboard_view(self):
        # Make a request to the CompanyDashboardView API view.
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.get(reverse("company-dashboard"), **headers)

        # Validate the response status code.
        assert response.status_code == 200

        # Validate the response data.
        data = response.json()
        print(data)
        assert "totalRevenue" in data
        assert "monthsActive" in data
        assert "revenueByMonth" in data
        assert "forSaleByMonth" in data
        assert "recentlySoldByMonth" in data

        # Validate the format of the response data.
        assert isinstance(data["totalRevenue"], float) or isinstance(
            data["totalRevenue"], int)
        assert isinstance(data["monthsActive"], int)
        assert isinstance(data["revenueByMonth"], dict)
        assert isinstance(data["forSaleByMonth"], dict)
        assert isinstance(data["recentlySoldByMonth"], dict)

        first_day_of_current_month = datetime.now().replace(day=1)

        # Calculate the last day of the previous month
        last_day_of_last_month = first_day_of_current_month - \
            timedelta(days=1)

        # Calculate the first day of the previous month
        first_day_of_last_month = last_day_of_last_month.replace(day=1)

        # Get the name of the previous month as a string (full month name)
        previous_month_name = first_day_of_last_month.strftime("%B")
        assert data["monthsActive"] == 13
        assert data["forSaleByMonth"][previous_month_name] == 1

        first_day_of_current_month = first_day_of_last_month.replace(day=1)

        # Calculate the last day of the previous month
        last_day_of_last_month = first_day_of_current_month - \
            timedelta(days=1)

        # Calculate the first day of the previous month
        first_day_of_last_month = last_day_of_last_month.replace(day=1)

        # Get the name of the previous month as a string (full month name)
        previous_month_name = first_day_of_last_month.strftime("%B")
        assert data["recentlySoldByMonth"][previous_month_name] == 1

        assert data["totalRevenue"] == 250.0

        # Add more assertions based on the expected behavior of the CompanyDashboardView.
        # For example, check if the revenue and leads data for the test company are correct.
        # Use the setup_test_data fixture to retrieve the test data and perform the assertions.
