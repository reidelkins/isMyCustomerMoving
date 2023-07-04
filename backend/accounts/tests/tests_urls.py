from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import Company, CustomUser
from accounts.urls import *
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

        self.tokens = self.get_token()

    def get_token(self):
        serializer = MyTokenObtainPairSerializer(
            data={"email": "testuser@example.com", "password": "testpassword"}
        )
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def test_refresh_token(self):
        url = reverse("token-refresh")
        data = {"refresh": self.tokens["refresh_token"]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_otp_generate_url(self):
        url = reverse("otp-generate")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.post(url, **headers)
        self.assertEqual(response.status_code, 200)

    def test_otp_generate_url_not_authenticated(self):
        url = reverse("otp-generate")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_otp_generate_url_get(self):
        url = reverse("otp-generate")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_otp_generate_url_get(self):
        url = reverse("otp-generate")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.get(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_otp_generate_url_delete(self):
        url = reverse("otp-generate")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_otp_validate_url(self):
        url = reverse("otp-validate")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        data = {"otp": "123456"}
        response = self.client.post(url, data, **headers)
        self.assertEqual(response.status_code, 400)

    def test_otp_validate_url_not_authenticated(self):
        url = reverse("otp-validate")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_otp_validate_url_get(self):
        url = reverse("otp-validate")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_otp_validate_url_put(self):
        url = reverse("otp-validate")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.put(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_otp_validate_url_delete(self):
        url = reverse("otp-validate")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_otp_verify_url(self):
        url = reverse("otp-verify")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        data = {"otp": "123456"}
        response = self.client.post(url, data, **headers)
        self.assertEqual(response.status_code, 400)

    def test_otp_verify_url_not_authenticated(self):
        url = reverse("otp-verify")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_otp_verify_url_get(self):
        url = reverse("otp-verify")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_otp_verify_url_put(self):
        url = reverse("otp-verify")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.put(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_otp_verify_url_delete(self):
        url = reverse("otp-verify")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_otp_disable_url(self):
        url = reverse("otp-disable")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.post(url, **headers)
        self.assertEqual(response.status_code, 200)

    def test_otp_disable_url_not_authenticated(self):
        url = reverse("otp-disable")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_otp_disable_url_get(self):
        url = reverse("otp-disable")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_otp_disable_url_put(self):
        url = reverse("otp-disable")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.put(url, data={}, **headers)
        self.assertEqual(response.status_code, 405)

    def test_otp_disable_url_delete(self):
        url = reverse("otp-disable")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_manage_user_url(self):
        url = reverse("manage-user", kwargs={"id": self.company.id})
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        data = {"email": "testemail@gmail.com"}
        response = self.client.post(url, data, **headers)
        self.assertEqual(response.status_code, 400)

    def test_manage_user_url_not_authenticated(self):
        url = reverse("manage-user", kwargs={"id": self.company.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_manage_user_url_needs_kwarg(self):
        with self.assertRaises(Exception):
            reverse(
                "manage-user",
            )

    def test_manage_user_url_put(self):
        url = reverse("manage-user", kwargs={"id": self.company.id})
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        data = {
            "email": "newtestemail@gmail.com",
            "firstName": "testfirstname",
            "lastName": "testlastname",
        }
        response = self.client.put(url, data, **headers)
        self.assertEqual(response.status_code, 400)

    def test_manage_user_url_delete(self):
        url = reverse("manage-user", kwargs={"id": self.company.id})
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_manage_user_url_get(self):
        url = reverse("manage-user", kwargs={"id": self.company.id})
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_accept_invite_url(self):
        url = reverse("accept-invite", kwargs={"invitetoken": self.user.id})
        response = self.client.post(url, data={"email": self.user.email})
        self.assertEqual(response.status_code, 400)

    def test_accept_invite_url_needs_kwarg(self):
        with self.assertRaises(Exception):
            reverse(
                "accept-invite",
            )

    def test_accept_invite_url_put(self):
        url = reverse("accept-invite", kwargs={"invitetoken": self.user.id})
        response = self.client.put(url, data={})
        self.assertEqual(response.status_code, 405)

    def test_accept_invite_url_delete(self):
        url = reverse("accept-invite", kwargs={"invitetoken": self.user.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 405)

    def test_accept_invite_url_get(self):
        url = reverse("accept-invite", kwargs={"invitetoken": self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_password_reset_url(self):
        url = reverse("password_reset:reset-password-request")
        data = {"email": self.user.email}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)

    def test_user_list_url(self):
        url = reverse("user-list")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 200)

    def test_user_list_url_not_authenticated(self):
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_user_list_url_post(self):
        url = reverse("user-list")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.post(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_user_list_url_put(self):
        url = reverse("user-list")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.put(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_user_list_url_delete(self):
        url = reverse("user-list")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_register_url(self):
        url = reverse("register")
        data = {"email": "test@email.com"}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 400)

    def test_register_url_get(self):
        url = reverse("register")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_register_url_put(self):
        url = reverse("register")
        data = {"email": "test@email.com"}
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, 405)

    def test_register_url_delete(self):
        url = reverse("register")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 405)

    def test_login(self):
        url = reverse("login")
        data = {"email": self.user.email, "password": "testpassword"}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)

    # TODO
    # def test_google_login(self):
    #     url = reverse("google-login")
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)

    def test_enterprise_url(self):
        url = reverse("enterprise")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 400)

    def test_enterprise_url(self):
        url = reverse("enterprise")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_enterprise_url_put(self):
        url = reverse("enterprise")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 400)

    def test_enterprise_url_delete(self):
        url = reverse("enterprise")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 405)

    def test_enterprise_url_post(self):
        url = reverse("enterprise")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.tokens['access_token']}"
        }
        response = self.client.post(url, **headers)
        self.assertEqual(response.status_code, 405)
