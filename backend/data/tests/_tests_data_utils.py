from django.test import TestCase
from unittest.mock import patch, MagicMock
from accounts.models import Company, CustomUser
from data.models import Client
from data.utils import (
    find_client_count,
    find_clients_to_delete,
    reactivate_clients,
    delete_extra_clients,
)


class MyTestCase(TestCase):
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
