from django.test import TestCase
import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime


from accounts.models import Company
from data.models import Client, HomeListing, ZipCode
from data.realtor import (
    create_home_listings,
    get_all_zipcodes,
    get_realtor_property_details
)
from data.utils import (
    parse_streets
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

    # def test_find_data(self):
    #     assert 1 == 1

    @patch("data.models.HomeListing.objects.create")
    def test_create_home_listing_new_listing(self, mock_create_listing):
        results = [{
            "status": "For Sale",
            "list_date": "2023-06-01",
            "list_price": 200000,
            "year_built": 2023,
            "description": {
                "year_built": 2023,
                "beds": 3,
                "baths": 2,
                "cooling": "Central",
                "heating": "Forced air",
                "sqft": 1500,
                "type": "Single Family",
                "lot_sqft": 2500,
            },
            "location": {
                "address": {
                    "coordinate": {
                        "lat": 28.389,
                        "lon": -80.666
                    },
                    "line": "891 Test Street",
                    "city": "New York",
                    "state_code": "NY",
                    "postal_code": "22953"
                }
            },
            "permalink": "https://testurl.com",
        }]

        continue_listing = create_home_listings(results, "For Sale")
        assert continue_listing is True

        mock_create_listing.assert_called_once_with(
            zip_code=self.zip_code2,
            address=parse_streets("891 Test Street"),
            status="For Sale",
            listed="2023-06-01",
            price=200000,
            housing_type="Single Family",
            year_built=2023,
            state="NY",
            city="New York",
            latitude=28.389,
            longitude=-80.666,
            permalink="https://testurl.com",
            lot_sqft=2500,
            bedrooms=3,
            bathrooms=2,
            cooling="Central",
            heating="Forced air",
            sqft=1500,
        )

    @patch("data.models.HomeListing.objects.create")
    @patch("data.models.HomeListing.objects.get")
    def test_create_home_listing_update_listing(self, mock_get_listings, mock_create_listing):
        results = [{
            "status": "For Sale",
            "list_date": "2023-06-01",
            "list_price": 200000,
            "year_built": "2023",
            "description": {
                "year_built": "2023",
                "beds": 3,
                "baths": 2,
                "cooling": "Central",
                "heating": "Forced air",
                "sqft": 1500,
                "type": "Single Family",
                "lot_sqft": 2500,
            },
            "location": {
                "address": {
                    "coordinate": {
                        "lat": 28.389,
                        "lon": -80.666
                    },
                    "line": "1800 Great Street",
                    "city": "New York",
                    "state_code": "NY",
                    "postal_code": "22953"
                }
            },
            "permalink": "https://testurl.com",
        }]

        continue_listing = create_home_listings(results, "For Sale")
        assert continue_listing is True

        mock_get_listings.assert_called_once_with(
            zip_code=self.zip_code2,
            address=parse_streets("1800 Great Street"),
            city="New York",
            state="NY",
        )
        mock_create_listing.assert_not_called()

    @patch("data.realtor.update_listing_data")
    @patch("data.realtor.get_listing_data")
    @patch("data.realtor.create_detail_url")
    def test_get_realtor_property_details(self, mock_create_detail_url, mock_get_listing_data, mock_update_listing_data):

        mock_create_detail_url.return_value = "https://testurl.com"

        # call function
        get_realtor_property_details(self.listing.id, 1)

        assert mock_create_detail_url.call_count == 1
        assert mock_get_listing_data.call_count == 1
        assert mock_update_listing_data.call_count == 1
