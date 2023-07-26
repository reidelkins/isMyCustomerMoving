from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import Company, CustomUser
from data.models import ZipCode, Client as Customer, Task
from accounts.serializers import MyTokenObtainPairSerializer


class UrlsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.company = Company.objects.create(name="company_name")
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            company=self.company,
            is_verified=True,
        )
        self.customer = Customer.objects.create(
            company=self.company,
            name="test customer",
            address="123 test street",
            city="test city",
            state="test state",
            zip_code=ZipCode.objects.create(zip_code="12345"),
        )
        self.task = Task.objects.create()

        self.token = self.get_token()

    def get_token(self):
        serializer = MyTokenObtainPairSerializer(
            data={"email": "testuser@example.com", "password": "testpassword"}
        )
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data["access_token"]

    def test_recently_sold_url_get(self):
        url = reverse("recently-sold")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 200)

    def test_recently_sold_not_authenticated(self):
        url = reverse("recently-sold")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_recently_sold_url_post(self):
        url = reverse("recently-sold")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.post(url, data={}, **headers)
        self.assertEqual(response.status_code, 400)

    def test_recently_sold_url_delete(self):
        url = reverse(
            "delete-recently-sold-filter",
            kwargs={"filter": "test-filter-name"},
        )
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 400)

    def test_recently_sold_url_delete_needs_kwarg(self):
        with self.assertRaises(Exception):
            reverse(
                "delete-recently-sold-filter",
            )

    def test_recently_sold_url_put(self):
        url = reverse("recently-sold")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        response = self.client.put(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_download_recently_sold_url(self):
        url = reverse("all-recently-sold")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 200)

    def test_download_recently_sold_not_authenticated(self):
        url = reverse("all-recently-sold")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_download_recently_sold_url_put(self):
        url = reverse("all-recently-sold")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.put(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_download_recently_sold_url_post(self):
        url = reverse("all-recently-sold")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.post(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_download_recently_sold_url_delete(self):
        url = reverse("all-recently-sold")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_for_sale_url_get(self):
        url = reverse("for-sale")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 200)

    def test_for_sale_not_authenticated(self):
        url = reverse("for-sale")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_for_sale_url_post(self):
        url = reverse("for-sale")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.post(url, data={}, **headers)
        self.assertEqual(response.status_code, 400)

    def test_for_sale_url_delete(self):
        url = reverse(
            "delete-for-sale-filter",
            kwargs={"filter": "test-filter-name"},
        )
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 400)

    def test_for_sale_url_delete_needs_kwarg(self):
        with self.assertRaises(Exception):
            reverse(
                "delete-for-sale-filter",
            )

    def test_for_sale_url_put(self):
        url = reverse("for-sale")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        response = self.client.put(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_download_for_sale_url(self):
        url = reverse("all-for-sale")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 200)

    def test_download_for_sale_not_authenticated(self):
        url = reverse("all-for-sale")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_download_for_sale_url_put(self):
        url = reverse("all-for-sale")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.put(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_download_for_sale_url_post(self):
        url = reverse("all-for-sale")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.post(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_download_for_sale_url_delete(self):
        url = reverse("all-for-sale")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 405)

    # TODO
    # def test_update_status_url_get(self):
    #     url = reverse("update-status")
    #     headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
    #     response = self.client.get(url, **headers)
    #     self.assertEqual(response.status_code, 200)

    def test_update_status_url_not_authenticated(self):
        url = reverse("update-status")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_update_status_url_url_put(self):
        url = reverse("update-status")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.put(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_update_status_url_url_post(self):
        url = reverse("update-status")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.post(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_update_status_url_url_delete(self):
        url = reverse("update-status")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_update_client_url_put(self):
        url = reverse("update-client")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.put(url, data={}, **headers)
        self.assertEqual(response.status_code, 400)

    def test_update_client_url_not_authenticated(self):
        url = reverse("update-client")
        response = self.client.put(url, data={})
        self.assertEqual(response.status_code, 403)

    def test_update_client_url_url_get(self):
        url = reverse("update-client")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_update_client_url_url_post(self):
        url = reverse("update-client")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.post(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_update_client_url_url_delete(self):
        url = reverse("update-client")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_upload_file_url_get(self):
        url = reverse("upload-file-check", kwargs={"task": self.task.id})
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 201)

    def test_upload_file_url_not_authenticated(self):
        url = reverse("upload-file-check", kwargs={"task": self.task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_upload_file_url_get_needs_kwarg(self):
        with self.assertRaises(Exception):
            reverse("upload-file-check")

    # TODO
    # def test_upload_file_url_url_put(self):
    #     url = reverse("upload-file")
    #     headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
    #     response = self.client.put(url, **headers)
    #     self.assertEqual(response.status_code, 201)

    def test_upload_file_url_url_post(self):
        url = reverse("upload-file")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.post(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_upload_file_url_url_delete(self):
        url = reverse("upload-file")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_download_clients_url_get(self):
        url = reverse("all-client-list")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 200)

    def test_download_clients_url_not_authenticated(self):
        url = reverse("all-client-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_download_clients_url_put(self):
        url = reverse("all-client-list")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.put(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_download_clients_url_post(self):
        url = reverse("all-client-list")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.post(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_download_clients_url_delete(self):
        url = reverse("all-client-list")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_client_list_url_get(self):
        url = reverse("client-list")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 200)

    def test_client_list_url_not_authenticated(self):
        url = reverse("client-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_client_list_url_post(self):
        url = reverse("client-list")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.post(url, data={}, **headers)
        self.assertEqual(response.status_code, 400)

    def test_client_list_url_put(self):
        url = reverse("client-list")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.put(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_client_list_url_delete(self):
        url = reverse("client-list")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_salesforce_url_get(self):
        url = reverse("salesforce")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 200)

    def test_salesforce_url_not_authenticated(self):
        url = reverse("salesforce")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    # TODO
    # def test_salesforce_url_put(self):
    #     url = reverse("salesforce")
    #     headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
    #     response = self.client.put(url, **headers)
    #     self.assertEqual(response.status_code, 200)

    def test_salesforce_url_post(self):
        url = reverse("salesforce")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.post(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_salesforce_url_delete(self):
        url = reverse("salesforce")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_servicetitan_url_get(self):
        url = reverse("servicetitan-with-task", kwargs={"task": self.task.id})
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 201)

    def test_servicetitan_url_delete_needs_kwarg(self):
        with self.assertRaises(Exception):
            reverse(
                "servicetitan-with-task",
            )

    def test_servicetitan_url_not_authenticated(self):
        url = reverse("servicetitan")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    # TODO
    # def test_servicetitan_url_put(self):
    #     url = reverse("servicetitan")
    #     headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
    #     response = self.client.put(url, **headers)
    #     self.assertEqual(response.status_code, 201)

    def test_servicetitan_url_post(self):
        url = reverse("servicetitan")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.post(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_servicetitan_url_delete(self):
        url = reverse("servicetitan")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_company_dashboard_get(self):
        url = reverse("company-dashboard")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 200)

    def test_company_dashboard_not_authenticated(self):
        url = reverse("company-dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_company_dashboard_put(self):
        url = reverse("company-dashboard")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.put(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_company_dashboard_post(self):
        url = reverse("company-dashboard")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.post(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_company_dashboard_delete(self):
        url = reverse("company-dashboard")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 405)
