from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from django.test import TestCase
from accounts.models import Company, CustomUser, Enterprise
from accounts.serializers import (BasicCompanySerializer, CompanySerializer, EnterpriseSerializer,
                                  MyTokenObtainPairSerializer, UserSerializer, UserSerializerWithToken, UserListSerializer)
from rest_framework import serializers


class TestCompanySerializer(TestCase):
    def test_basic_company_serializer_initialization(self):
        # Given
        company = Company.objects.create(
            name="Test Company", phone="1234567890", email="test@test.com")
        # When
        serializer = BasicCompanySerializer(company)
        # Then
        self.assertEqual(serializer.data, {
            "id": str(company.id),
            "name": "Test Company",
            "email": "test@test.com",
            "phone": "1234567890",
            "users_count": 0,
            "leads_count": 0,
            "clients_count": 0,
        })

    def test_company_serializer_initialization(self):
        # Given
        company = Company.objects.create(
            name="Test Company", phone="1234567890", email="test@test.com")
        # When
        serializer = CompanySerializer(company)
        # Then
        self.assertEqual(serializer.data["name"], "Test Company")
        self.assertEqual(serializer.data["phone"], "1234567890")
        self.assertEqual(serializer.data["email"], "test@test.com")

    def test_company_serializer_validation(self):
        # When
        serializer = CompanySerializer(
            data={"name": "Test Company", "phone": "1234567890", "email": "test2@test.com"})
        serializer.is_valid()
        print(serializer.errors)

        serializer.save()
        # Then
        self.assertEqual(Company.objects.all().count(), 1)

    def test_company_serializer_create(self):
        # Given
        serializer = CompanySerializer(
            data={"name": "Test Company", "phone": "1234567890", "email": "test@test.com"})
        # When
        serializer.is_valid()
        company = serializer.save()
        # Then
        self.assertEqual(company.name, "Test Company")
        self.assertEqual(company.phone, "1234567890")
        self.assertEqual(company.email, "test@test.com")

    def test_company_serializer_method_fields(self):
        # Given
        company = Company.objects.create(
            name="Test Company", phone="1234567890", email="test@test.com")
        CustomUser.objects.create(company=company)
        serializer = BasicCompanySerializer(company)
        # When
        users_count = serializer.get_users_count(company)
        # Then
        self.assertEqual(users_count, 1)


class EnterpriseSerializerTestCase(TestCase):
    def setUp(self):
        self.enterprise_data = {
            "name": "Test Enterprise",
        }
        self.enterprise = Enterprise.objects.create(**self.enterprise_data)
        self.company = Company.objects.create(
            name="Test Company",
            phone="1234567890",
            email="test@test.com",
            enterprise=self.enterprise,
        )

    def test_enterprise_serializer(self):
        """
        Test that EnterpriseSerializer correctly serializes data
        """
        serializer = EnterpriseSerializer(instance=self.enterprise)
        self.assertEqual(serializer.data["name"], "Test Enterprise")
        self.assertEqual(serializer.data["id"], str(self.enterprise.id))
        self.assertEqual(
            serializer.data["companies"][0]["name"], "Test Company")
        self.assertEqual(
            serializer.data["companies"][0]["id"], str(self.company.id))
        self.assertEqual(
            serializer.data["companies"][0]["phone"], "1234567890")
        self.assertEqual(
            serializer.data["companies"][0]["email"], "test@test.com")

    def test_enterprise_deserializer(self):
        """
        Test that EnterpriseSerializer correctly deserializes data
        """
        serializer = EnterpriseSerializer(data=self.enterprise_data)
        self.assertTrue(serializer.is_valid())
        enterprise = serializer.save()
        self.assertEqual(enterprise.name, self.enterprise_data["name"])
        # Note: We don't test deserialization of the 'companies' field,
        # as nested writes are not supported in the serializer as written.

    def test_enterprise_deserializer_invalid_data(self):
        """
        Test that EnterpriseSerializer correctly handles invalid data
        """
        invalid_data = self.enterprise_data.copy()
        invalid_data["name"] = ""  # Name field should not be empty
        serializer = EnterpriseSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)


class UserSerializerTest(TestCase):
    def setUp(self):
        self.enterprise = Enterprise.objects.create(name="TestEnterprise")
        self.company = Company.objects.create(
            name="TestCompany", enterprise=self.enterprise)
        self.user = CustomUser.objects.create_user(
            email="testuser@test.com",
            password="password",
            first_name="Test",
            last_name="User",
            company=self.company,
            is_verified=True,
        )
        self.user_data = {
            "id": str(self.user.id),
            "email": "testuser@test.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "password",

        }

    def test_token_obtain_pair_serializer(self):
        """
        Test that MyTokenObtainPairSerializer correctly generates token pairs
        """
        serializer = MyTokenObtainPairSerializer(data={
            "email": "testuser@test.com",
            "password": "password"
        })
        self.assertTrue(serializer.is_valid())
        tokens = serializer.validated_data
        self.assertIn("access_token", tokens)
        self.assertIn("refresh_token", tokens)

    def test_user_serializer(self):
        """
        Test that UserSerializer correctly serializes data
        """
        serializer = UserSerializer(instance=self.user)
        expected_data = {**self.user_data, "company": None}
        expected_data["company"] = CompanySerializer(self.company).data
        self.assertEqual(serializer.data["id"], expected_data["id"])
        self.assertEqual(serializer.data["email"], expected_data["email"])
        self.assertEqual(
            serializer.data["first_name"], expected_data["first_name"])
        self.assertEqual(
            serializer.data["last_name"], expected_data["last_name"])
        self.assertEqual(
            serializer.data["company"], expected_data["company"])

    def test_user_list_serializer(self):
        """
        Test that UserListSerializer correctly serializes data
        """
        serializer = UserListSerializer(instance=self.user)
        expected_data = {
            "id": str(self.user.id),
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@test.com",
            "status": "active",
            "is_enterprise_owner": False,
        }
        self.assertEqual(serializer.data, expected_data)

    def test_token_obtain_pair_serializer_incorrect_password(self):
        """
        Test that MyTokenObtainPairSerializer raises a ValidationError for incorrect password
        """
        serializer = MyTokenObtainPairSerializer(data={
            "email": self.user_data["email"],
            "password": "wrongpassword"
        })
        try:
            serializer.is_valid(raise_exception=True)
            self.fail("Expected AuthenticationFailed exception not raised")
        except AuthenticationFailed as e:
            self.assertEqual(
                str(e), "No active account found with the given credentials"
            )

    def test_token_obtain_pair_serializer_unverified_user(self):
        """
        Test that MyTokenObtainPairSerializer raises a ValidationError for unverified user
        """
        self.user.is_verified = False
        self.user.save()
        serializer = MyTokenObtainPairSerializer(data={
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        })
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_user_serializer_with_token_different_tokens(self):
        """
        Test that UserSerializerWithToken generates different tokens for different users
        """
        user2 = CustomUser.objects.create_user(
            email="testuser2@test.com",
            password="password2",
            first_name="Test2",
            last_name="User2",
            company=self.company,
            is_verified=True,
        )
        serializer1 = UserSerializerWithToken(instance=self.user)
        serializer2 = UserSerializerWithToken(instance=user2)
        self.assertNotEqual(
            serializer1.data["access_token"], serializer2.data["access_token"])
        self.assertNotEqual(
            serializer1.data["refresh_token"], serializer2.data["refresh_token"])

    def test_user_serializer_get_finished_st_integration(self):
        """
        Test that get_finished_st_integration method works correctly
        """
        serializer = UserSerializer(instance=self.user)
        self.assertFalse(serializer.get_finished_st_integration(self.user))
        self.user.company.tenant_id = "12345"
        self.user.company.client_id = "some_client_id"
        self.user.company.client_secret = "some_client_secret"
        self.user.company.save()
        self.assertTrue(serializer.get_finished_st_integration(self.user))

    def test_user_list_serializer_multiple_users(self):
        """
        Test that UserListSerializer correctly serializes multiple user instances
        """
        user2 = CustomUser.objects.create_user(
            email="testuser2@test.com",
            password="password2",
            first_name="Test2",
            last_name="User2",
            company=self.company,
            is_verified=True,
        )
        queryset = get_user_model().objects.all()
        serializer = UserListSerializer(queryset, many=True)
        self.assertEqual(len(serializer.data), queryset.count())
        for user, data, in zip(queryset, serializer.data):
            self.assertEqual(data["id"], str(user.id))
            self.assertEqual(data["first_name"], user.first_name)
            self.assertEqual(data["last_name"], user.last_name)
            self.assertEqual(data["email"], user.email)
            self.assertEqual(data["status"], user.status)
            self.assertEqual(data["is_enterprise_owner"],
                             user.is_enterprise_owner)
