from django.test import TestCase
import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime


from accounts.models import Company
from data.models import Client, ZipCode
from data.realtor import (
    get_all_zipcodes,
)


@pytest.fixture
def mock_find_data():
    with patch("data.realtor.find_data.delay") as mock:
        yield mock


@pytest.fixture
def mock_zapier_recently_sold():
    with patch("data.utils.send_zapier_recently_sold") as mock:
        yield mock


class TestRealtorFunctions(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="company_name")
        self.client = Client.objects.create(
            name="Test Client1",
            address="260 Milford Point Rd",
            city="Merritt Island",
            state="FL",
            zip_code=ZipCode.objects.create(zip_code="32952"),
            company=self.company)
        self.client2 = Client.objects.create(
            name="Test Client2",
            address="123 Main Street",
            city="New York",
            state="NY",
            zip_code=ZipCode.objects.create(zip_code="29523"),
            company=self.company)
        other_company = Company.objects.create(
            name="other_company_name")
        other_client = Client.objects.create(
            name="Test Client3",
            address="14914 Palmer Creek",
            city="San Antonio",
            state="FL",
            zip_code=ZipCode.objects.create(zip_code="12345"),
            company=other_company)

    @patch("data.utils.send_zapier_recently_sold")
    @patch("data.realtor.find_data.delay")
    def test_get_all_zipcodes(self, mock_find_data, mock_zapier_recently_sold):
        get_all_zipcodes(self.company.id)
        assert mock_find_data.call_count == 4

        mock_find_data.reset_mock()
        mock_zapier_recently_sold.reset_mock()

        get_all_zipcodes("", zip="12345")
        assert mock_find_data.call_count == 2
        if datetime.now().weekday() == 0:
            mock_zapier_recently_sold.assert_called_once_with(self.company.id)
        else:
            mock_zapier_recently_sold.assert_not_called()
