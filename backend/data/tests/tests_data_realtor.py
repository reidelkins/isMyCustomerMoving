from django.test import TestCase
import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime


from accounts.models import Company
from data.models import Client, HomeListing, ZipCode
from data.realtor import (
    get_all_zipcodes,
)


@pytest.fixture
def mock_find_data():
    with patch("data.realtor.find_data.delay") as mock:
        yield mock


@pytest.fixture
def mock_zapier_recently_sold():
    with patch("data.utils.send_zapier_recently_sold.delay") as mock:
        yield mock


@pytest.fixture
def mock_get_listings():
    with patch("data.models.HomeListing.objects.get") as mock:
        yield mock


@pytest.fixture
def mock_create_listing():
    with patch("data.models.HomeListing.objects.create") as mock:
        yield mock


@pytest.fixture
def mock_create_detail_url():
    with patch("data.realtor.create_detail_url") as mock:
        yield mock


@pytest.fixture
def mock_get_listing_data():
    with patch("data.realtor.get_listing_data") as mock:
        yield mock


@pytest.fixture
def mock_update_listing_data():
    with patch("data.realtor.update_listing_data") as mock:
        yield mock


class TestRealtorFunctions(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="company_name")
        self.zip_code1 = ZipCode.objects.create(zip_code="32953")
        self.zip_code2 = ZipCode.objects.create(zip_code="22953")
        self.zip_code3 = ZipCode.objects.create(zip_code="12345")
        self.client = Client.objects.create(
            name="Test Client1",
            address="260 Milford Point Rd",
            city="Merritt Island",
            state="FL",
            zip_code=self.zip_code1,
            company=self.company)
        self.client2 = Client.objects.create(
            name="Test Client2",
            address="123 Main Street",
            city="New York",
            state="NY",
            zip_code=self.zip_code2,
            company=self.company)
        other_company = Company.objects.create(
            name="other_company_name")
        other_client = Client.objects.create(
            name="Test Client3",
            address="14914 Palmer Creek",
            city="San Antonio",
            state="FL",
            zip_code=self.zip_code3,
            company=other_company)
        self.listing = HomeListing.objects.create(
            zip_code=self.zip_code1,
            address="260 Milford Point Rd",
            status="Recently Sold (6)",
            listed="2020-01-01",
            price=100000,
            year_built=2000,
            city="Merritt Island",
            state="FL",
            permalink="260-Milford-Point-Dr_Merritt-Island_FL_32952_M57137-33293"
        )
        HomeListing.objects.create(
            zip_code=self.zip_code2,
            address="123 Main Street",
            status="For Sale",
            listed="2023-11-01",
            price=200000,
            year_built=2023,
            city="New York",
            state="NY",
        )

    @patch("data.utils.send_zapier_recently_sold.delay")
    @patch("data.realtor.find_data.delay")
    def test_get_all_zipcodes(self, mock_find_data, mock_zapier_recently_sold):
        get_all_zipcodes(self.company.id)
        assert mock_find_data.call_count == 4
        if datetime.now().weekday() == 0:
            mock_zapier_recently_sold.assert_called()
        else:
            mock_zapier_recently_sold.assert_not_called()

        mock_find_data.reset_mock()

        get_all_zipcodes("", zip="12345")
        assert mock_find_data.call_count == 2
