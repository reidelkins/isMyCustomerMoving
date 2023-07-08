from django.db import IntegrityError
from django.test import TestCase
from datetime import datetime
from accounts.models import InviteToken, Enterprise, Company, CustomUser
from payments.models import Product


class TestInviteTokenModel(TestCase):
    def test_invitetoken_creation(self):
        """
        Test the creation of an InviteToken object.
        """
        company = Company.objects.create(name="Test Company")
        invite = InviteToken.objects.create(
            email="test@test.com", company=company
        )
        self.assertEqual(invite.email, "test@test.com")
        self.assertEqual(invite.company, company)

    def test_invitetoken_expiration(self):
        """
        Test the default value of expiration field.
        """
        invite = InviteToken.objects.create(email="test@test.com")
        # Calculate the timedelta between now and the expiration time.
        # We only compare days because the exact time could be different due to the execution time of the code.
        timedelta_to_expire = (
            invite.expiration.date() - datetime.utcnow().date()
        )

        self.assertEqual(timedelta_to_expire.days, 1)

    def test_invitetoken_unique(self):
        """
        Test that id field is unique.
        """
        invite1 = InviteToken.objects.create(email="test1@test.com")
        with self.assertRaises(Exception):
            invite2 = InviteToken.objects.create(
                id=invite1.id, email="test2@test.com"
            )

    def test_invitetoken_optional_fields(self):
        """
        Test that company field is optional.
        """
        invite = InviteToken.objects.create(email="test@test.com")
        self.assertIsNone(invite.company)


class TestEnterpriseModel(TestCase):
    def test_enterprise_creation(self):
        """
        Test the creation of an Enterprise object.
        """
        enterprise = Enterprise.objects.create(name="Test Enterprise")
        self.assertEqual(enterprise.name, "Test Enterprise")
        self.assertEqual(enterprise.__str__(), "Test Enterprise")

    def test_enterprise_unique(self):
        """
        Test that id field is unique.
        """
        enterprise1 = Enterprise.objects.create(name="Test Enterprise 1")
        with self.assertRaises(Exception):
            enterprise2 = Enterprise.objects.create(
                id=enterprise1.id, name="Test Enterprise 2"
            )


class TestCompanyModel(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            id="123", amount=150.0, interval="month", name="Product1"
        )

        self.enterprise = Enterprise.objects.create(name="Enterprise1")

    def test_company_creation(self):
        """
        Test the creation of a Company object.
        """
        company = Company.objects.create(
            name="Test Company",
            product=self.product,
            enterprise=self.enterprise,
        )
        self.assertEqual(company.name, "Test Company")
        self.assertEqual(company.product, self.product)
        self.assertEqual(company.enterprise, self.enterprise)

    def test_company_default_values(self):
        """
        Test the default values for the access_token field in a Company object.
        """
        company = Company.objects.create(
            name="Test Company",
            product=self.product,
            enterprise=self.enterprise,
        )
        self.assertIsNotNone(company.access_token)

    def test_company_str(self):
        """
        Test the string representation of a Company object.
        """
        company = Company.objects.create(
            name="Test Company",
            product=self.product,
            enterprise=self.enterprise,
        )
        self.assertEqual(str(company), "Test Company")

    def test_company_nullable_fields(self):
        """
        Test that nullable fields can indeed be set to null.
        """
        company = Company.objects.create(
            name="Test Company",
            product=self.product,
            enterprise=self.enterprise,
            phone=None,
            email=None,
        )
        self.assertIsNone(company.phone)
        self.assertIsNone(company.email)

    def test_company_unique_id(self):
        """
        Test that the Company id field is unique.
        """
        company1 = Company.objects.create(
            name="Test Company 1",
            product=self.product,
            enterprise=self.enterprise,
        )
        with self.assertRaises(Exception):
            company2 = Company.objects.create(
                id=company1.id,
                name="Test Company 2",
                product=self.product,
                enterprise=self.enterprise,
            )

    def test_company_foreign_keys(self):
        """
        Test foreign key constraints on deletion.
        """
        company = Company.objects.create(
            name="Test Company",
            product=self.product,
            enterprise=self.enterprise,
        )
        self.product.delete()
        self.assertEqual(
            Company.objects.filter(id=company.id).first().product, None
        )

    def test_company_related_name(self):
        """
        Test that the related name for enterprise works as expected.
        """
        company1 = Company.objects.create(
            name="Test Company 1",
            product=self.product,
            enterprise=self.enterprise,
        )
        company2 = Company.objects.create(
            name="Test Company 2",
            product=self.product,
            enterprise=self.enterprise,
        )
        self.assertEqual(
            list(self.enterprise.companies.all()), [company1, company2]
        )

    def test_company_access_token_generation(self):
        """
        Test access token generation on company creation.
        """
        company = Company.objects.create(
            name="Test Company",
            product=self.product,
            enterprise=self.enterprise,
        )
        self.assertIsNotNone(company.access_token)
        self.assertEqual(
            len(company.access_token), 32
        )  # assuming your access token is 32 characters long


class TestCustomUserModel(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.enterprise = Enterprise.objects.create(name="Test Enterprise")

    def test_create_user(self):
        """
        Test the creation of a User object.
        """
        user = CustomUser.objects.create_user(
            email="testuser@test.com",
            password="password",
            first_name="Test",
            last_name="User",
        )
        self.assertEqual(user.email, "testuser@test.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_superuser, False)

    def test_create_superuser(self):
        """
        Test the creation of a Superuser object.
        """
        user = CustomUser.objects.create_superuser(
            email="testadmin@test.com",
            password="password",
            first_name="Test",
            last_name="Admin",
        )
        self.assertEqual(user.email, "testadmin@test.com")
        self.assertEqual(user.is_staff, True)
        self.assertEqual(user.is_superuser, True)

    def test_user_str(self):
        """
        Test the string representation of a User object.
        """
        user = CustomUser.objects.create_user(
            email="testuser@test.com",
            password="password",
            first_name="Test",
            last_name="User",
        )
        self.assertEqual(str(user), "testuser@test.com")

    def test_user_unique_email(self):
        """
        Test that the email field is unique.
        """
        user1 = CustomUser.objects.create_user(
            email="testuser@test.com",
            password="password",
            first_name="Test",
            last_name="User",
        )
        with self.assertRaises(Exception):
            user2 = CustomUser.objects.create_user(
                email="testuser@test.com",
                password="password",
                first_name="Test",
                last_name="User",
            )

    def test_user_related_name(self):
        """
        Test that the related name for enterprise works as expected.
        """
        user1 = CustomUser.objects.create_user(
            email="user1@test.com",
            password="password",
            first_name="User",
            last_name="One",
            enterprise=self.enterprise,
        )
        user2 = CustomUser.objects.create_user(
            email="user2@test.com",
            password="password",
            first_name="User",
            last_name="Two",
            enterprise=self.enterprise,
        )
        self.assertEqual(list(self.enterprise.users.all()), [user1, user2])

    def test_user_save_method(self):
        """
        Test the behavior of the save method.
        """
        user = CustomUser.objects.create_user(
            email="testuser@test.com",
            password="password",
            first_name="Test",
            last_name="User",
            company=self.company,
        )
        self.assertEqual(user.enterprise, self.company.enterprise)

    def test_user_no_username(self):
        """
        Test that the User model does not have a username field.
        """
        user = CustomUser.objects.create_user(
            email="testuser@test.com",
            password="password",
            first_name="Test",
            last_name="User",
        )
        self.assertEqual(user.username, None)

    def test_email_required(self):
        """
        Test that all required fields are indeed required.
        """
        with self.assertRaises(ValueError):
            user = CustomUser.objects.create_user(
                email=None,
                password="password",
                first_name="Test",
                last_name="User",
            )

    def test_first_name_required(self):
        with self.assertRaises(IntegrityError):
            user = CustomUser.objects.create_user(
                email="testuser@test.com",
                password="password",
                first_name=None,
                last_name="User",
            )

    def test_last_name_required(self):
        with self.assertRaises(IntegrityError):
            user = CustomUser.objects.create_user(
                email="testuser@test.com",
                password="password",
                first_name="Test",
                last_name=None,
            )

    def test_is_verified_default(self):
        """
        Test that is_verified defaults to False upon user creation.
        """
        user = CustomUser.objects.create_user(
            email="testuser@test.com",
            password="password",
            first_name="Test",
            last_name="User",
        )
        self.assertEqual(user.is_verified, False)

    def test_otp_fields_default(self):
        """
        Test that otp_enabled and otp_verified default to False upon user creation.
        """
        user = CustomUser.objects.create_user(
            email="testuser@test.com",
            password="password",
            first_name="Test",
            last_name="User",
        )
        self.assertEqual(user.otp_enabled, False)
        self.assertEqual(user.otp_verified, False)

    def test_save_no_company(self):
        """
        Test the behavior of the save method when company is None.
        """
        user = CustomUser.objects.create_user(
            email="testuser@test.com",
            password="password",
            first_name="Test",
            last_name="User",
        )
        self.assertIsNone(user.enterprise)

    def test_cascade_delete_behavior(self):
        """
        Test that user gets deleted when the associated company or enterprise is deleted.
        """
        user = CustomUser.objects.create_user(
            email="testuser@test.com",
            password="password",
            first_name="Test",
            last_name="User",
            company=self.company,
            enterprise=self.enterprise,
        )
        self.company.delete()
        self.assertFalse(
            CustomUser.objects.filter(email="testuser@test.com").exists()
        )
        user = CustomUser.objects.create_user(
            email="testuser2@test.com",
            password="password",
            first_name="Test",
            last_name="User",
            enterprise=self.enterprise,
        )
        self.enterprise.delete()
        self.assertFalse(
            CustomUser.objects.filter(email="testuser2@test.com").exists()
        )

    # def test_user_deletion_with_tokens(self):
    #     """
    #     Test the deletion of a user and their associated tokens.
    #     """
    #     user = CustomUser.objects.create_user(
    #         email="testuser@test.com",
    #         password="password",
    #         first_name="Test",
    #         last_name="User",
    #     )
    #     refresh = RefreshToken.for_user(user)
    #     outstanding_token = OutstandingToken.objects.create(
    #         user=user, token=refresh.token
    #     )
    #     user.delete_with_tokens()
    #     self.assertEqual(
    #         OutstandingToken.objects.filter(user=user).exists(), False
    #     )
