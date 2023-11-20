from datetime import datetime, timedelta
from django.test import TestCase
from data.models import (
    ZipCode,
    Client,
    ClientUpdate,
    HomeListing,
    # Realtor,
    SavedFilter,
    format_today,
)
from accounts.models import Company


STATUS = [
    ("House For Sale", "House For Sale"),
    ("House For Rent", "House For Rent"),
    ("House Recently Sold (6)", "House Recently Sold (6)"),
    ("Recently Sold (12)", "Recently Sold (12)"),
    ("Taken Off Market", "Taken Off Market"),
    ("No Change", "No Change"),
]


# Create your tests here.
class TestZipCodeModel(TestCase):
    def test_zipcode_creation(self):
        """
        Test the creation of a ZipCode object.
        """
        zipcode = ZipCode.objects.create(zip_code="12345")
        self.assertEqual(zipcode.zip_code, "12345")
        self.assertEqual(zipcode.__str__(), "12345")

    def test_zipcode_unique(self):
        """
        Test that zip_code field is unique.
        """
        zipcode1 = ZipCode.objects.create(zip_code="12345")
        with self.assertRaises(Exception):
            zipcode2 = ZipCode.objects.create(zip_code="12345")

    def test_zipcode_max_length(self):
        """
        Test the max_length attribute of zip_code field.
        """
        with self.assertRaises(Exception):
            zipcode = ZipCode.objects.create(zip_code="123456")

    def test_zipcode_last_updated(self):
        """
        Test that the last_updated field is set to the default value.
        """
        zipcode = ZipCode.objects.create(zip_code="12345")
        self.assertEqual(
            zipcode.last_updated,
            (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d"),
        )


class TestClientModel(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.zip_code = ZipCode.objects.create(zip_code="12345")

    def test_client_creation(self):
        """
        Test the creation of a Client object.
        """
        client = Client.objects.create(
            name="Test Client",
            address="123 Test Street",
            zip_code=self.zip_code,
            company=self.company,
            status="No Change",
            active=True,
            error_flag=False,
            usps_different=False,
        )
        self.assertEqual(client.name, "Test Client")
        self.assertEqual(client.address, "123 Test Street")
        self.assertEqual(client.zip_code, self.zip_code)
        self.assertEqual(client.company, self.company)
        self.assertEqual(client.status, "No Change")
        self.assertEqual(client.active, True)
        self.assertEqual(client.error_flag, False)
        self.assertEqual(client.usps_different, False)

    def test_client_str(self):
        """
        Test the __str__ method of the Client model.
        """
        client = Client.objects.create(
            name="Test Client",
            address="123 Test Street",
            zip_code=self.zip_code,
            company=self.company,
            status="No Change",
        )

        self.assertEqual(str(client), f"Test Client_{self.company}")

    def test_client_unique_together(self):
        """
        Test the unique_together meta option.
        """
        Client.objects.create(
            name="Test Client",
            address="123 Test Street",
            zip_code=self.zip_code,
            company=self.company,
            status="No Change",
        )
        with self.assertRaises(Exception):
            Client.objects.create(
                name="Test Client",
                address="123 Test Street",
                zip_code=self.zip_code,
                company=self.company,
                status="Off Market",
            )


class TestClientUpdateModel(TestCase):
    def setUp(self):
        """
        Setup test environment.
        """
        self.client_object = Client.objects.create(
            name="Test Client",
            address="123 Test Street",
            zip_code=ZipCode.objects.create(zip_code="12345"),
            company=Company.objects.create(name="Test Company"),
            status="No Change",
        )

    def test_client_update_creation(self):
        """
        Test the creation of a ClientUpdate object.
        """
        client_update = ClientUpdate.objects.create(
            client=self.client_object,
            status="House For Sale",
            listed="01-29-1997",
            note="Test Note",
            contacted=True,
            error_flag=False,
        )

        self.assertEqual(client_update.status, "House For Sale")
        self.assertEqual(client_update.listed, "01-29-1997")
        self.assertEqual(client_update.note, "Test Note")
        self.assertEqual(client_update.contacted, True)
        self.assertEqual(client_update.error_flag, False)

    def test_client_update_date_default(self):
        """
        Test that the date field is set to the default value.
        """
        client_update = ClientUpdate.objects.create(
            client=self.client_object,
            status="No Change",
            listed=datetime.today().strftime("%m-%d-%Y"),
            note="Test Note",
            contacted=True,
            error_flag=False,
        )

        self.assertEqual(client_update.date, format_today())


class HomeListingModelTests(TestCase):
    def setUp(self):
        self.zip_code = ZipCode.objects.create(zip_code="12345")
        # self.realtor = Realtor.objects_with_listing_count.create(
        #     name="John Doe",
        #     company="Doe Estate",
        #     agent_phone="1234567890",
        #     brokerage_phone="1234567890",
        # )

    def test_create_home_listing(self):
        home_listing = HomeListing.objects.create(
            zip_code=self.zip_code,
            address="123 Main St",
            status="Off Market",
            listed=" ",
            price=200000,
            housing_type=" ",
            year_built=2000,
            city="New York",
            state="NY",
            bedrooms=3,
            bathrooms=2,
            sqft=1200,
            lot_sqft=3000,
            latitude=40.712776,
            longitude=-74.005974,
            year_renovated=2010,
            # roofing=" ",
            # garage_type=" ",
            garage=1,
            # heating=" ",
            # cooling=" ",
            # exterior=" ",
            # pool=" ",
            # fireplace=" ",
            description="A beautiful home in New York",
            # realtor=self.realtor,
        )

        self.assertEqual(home_listing.address, "123 Main St")
        self.assertEqual(home_listing.status, "Off Market")
        self.assertEqual(home_listing.price, 200000)
        self.assertEqual(home_listing.housing_type, " ")
        self.assertEqual(home_listing.year_built, 2000)
        self.assertEqual(home_listing.city, "New York")
        self.assertEqual(home_listing.state, "NY")
        self.assertEqual(home_listing.bedrooms, 3)
        self.assertEqual(home_listing.bathrooms, 2)
        self.assertEqual(home_listing.sqft, 1200)
        self.assertEqual(home_listing.lot_sqft, 3000)
        self.assertEqual(home_listing.latitude, 40.712776)
        self.assertEqual(home_listing.longitude, -74.005974)
        self.assertEqual(home_listing.year_renovated, 2010)
        # self.assertEqual(home_listing.roofing, " ")
        # self.assertEqual(home_listing.garage_type, " ")
        self.assertEqual(home_listing.garage, 1)
        # self.assertEqual(home_listing.heating, " ")
        # self.assertEqual(home_listing.cooling, " ")
        # self.assertEqual(home_listing.exterior, " ")
        # self.assertEqual(home_listing.pool, " ")
        # self.assertEqual(home_listing.fireplace, " ")
        self.assertEqual(
            home_listing.description, "A beautiful home in New York"
        )
        # self.assertEqual(home_listing.realtor, self.realtor)

    def test_home_listing_str(self):
        home_listing = HomeListing.objects.create(
            zip_code=self.zip_code,
            address="123 Main St",
            status="Off Market",
            listed=" ",
            price=200000,
            housing_type=" ",
            year_built=2000,
            city="New York",
            state="NY",
            bedrooms=3,
            bathrooms=2,
            sqft=1200,
            lot_sqft=3000,
            latitude=40.712776,
            longitude=-74.005974,

            year_renovated=2010,
            # roofing=" ",
            # garage_type=" ",
            garage=1,
            # heating=" ",
            # cooling=" ",
            # exterior=" ",
            # pool=" ",
            # fireplace=" ",
            description="A beautiful home in New York",
            # realtor=self.realtor,
        )

        self.assertEqual(str(home_listing), "123 Main St_Off Market")

    def test_home_listing_unique_together(self):
        # unique_together = ("address", "status", "city", "state")
        HomeListing.objects.create(
            zip_code=self.zip_code,
            address="123 Main St",
            status="Off Market",
            listed=" ",
            price=200000,
            housing_type=" ",
            year_built=2000,
            city="New York",
            state="NY",
            bedrooms=3,
            bathrooms=2,
            sqft=1200,
            lot_sqft=3000,
            latitude=40.712776,
            longitude=-74.005974,

            year_renovated=2010,
            # roofing=" ",
            # garage_type=" ",
            garage=1,
            # heating=" ",
            # cooling=" ",
            # exterior=" ",
            # pool=" ",
            # fireplace=" ",
            description="A beautiful home in New York",
            # realtor=self.realtor,
        )

        with self.assertRaises(Exception):
            HomeListing.objects.create(
                zip_code=self.zip_code,
                address="123 Main St",
                status="Off Market",
                listed=" ",
                price=200000,
                housing_type=" ",
                year_built=2000,
                city="New York",
                state="NY",
                bedrooms=3,
                bathrooms=2,
                sqft=1200,
                lot_sqft=3000,
                latitude=40.712776,
                longitude=-74.005974,

                year_renovated=2010,
                # roofing=" ",
                # garage_type=" ",
                garage=1,
                # heating=" ",
                # cooling=" ",
                # exterior=" ",
                # pool=" ",
                # fireplace=" ",
                description="A beautiful home in New York",
                # realtor=self.realtor,
            )

    def test_home_listing_address_length(self):

        # max length is 150 chars
        address = "a" * 151
        with self.assertRaises(Exception):
            HomeListing.objects.create(
                zip_code=self.zip_code,
                address=address,
                status="Off Market",
                listed=" ",
                price=200000,
                housing_type=" ",
                year_built=2000,
                city="New York",
                state="NY",
                bedrooms=3,
                bathrooms=2,
                sqft=1200,
                lot_sqft=3000,
                latitude=40.712776,
                longitude=-74.005974,

                year_renovated=2010,
                # roofing=" ",
                # garage_type=" ",
                garage=1,
                # heating=" ",
                # cooling=" ",
                # exterior=" ",
                # pool=" ",
                # fireplace=" ",
                description="A beautiful home in New York",
                # realtor=self.realtor,
            )

    def test_home_listing_status_length(self):
        # 25 char limit
        status = "a" * 26
        with self.assertRaises(Exception):
            HomeListing.objects.create(
                zip_code=self.zip_code,
                address="123 Main St",
                status=status,
                listed=" ",
                price=200000,
                housing_type=" ",
                year_built=2000,
                city="New York",
                state="NY",
                bedrooms=3,
                bathrooms=2,
                sqft=1200,
                lot_sqft=3000,
                latitude=40.712776,
                longitude=-74.005974,

                year_renovated=2010,
                # roofing=" ",
                # garage_type=" ",
                garage=1,
                # heating=" ",
                # cooling=" ",
                # exterior=" ",
                # pool=" ",
                # fireplace=" ",
                description="A beautiful home in New York",
                # realtor=self.realtor,
            )

    def test_home_listing_listed_length(self):
        # max length 30 chars
        listed = "a" * 31
        with self.assertRaises(Exception):
            HomeListing.objects.create(
                zip_code=self.zip_code,
                address="123 Main St",
                status="Off Market",
                listed=listed,
                price=200000,
                housing_type=" ",
                year_built=2000,
                city="New York",
                state="NY",
                bedrooms=3,
                bathrooms=2,
                sqft=1200,
                lot_sqft=3000,
                latitude=40.712776,
                longitude=-74.005974,

                year_renovated=2010,
                # roofing=" ",
                # garage_type=" ",
                garage=1,
                # heating=" ",
                # cooling=" ",
                # exterior=" ",
                # pool=" ",
                # fireplace=" ",
                description="A beautiful home in New York",
                # realtor=self.realtor,
            )

    def test_home_listing_housing_type_length(self):
        # max length 100 chars
        housing_type = "a" * 101
        with self.assertRaises(Exception):
            HomeListing.objects.create(
                zip_code=self.zip_code,
                address="123 Main St",
                status="Off Market",
                listed=" ",
                price=200000,
                housing_type=housing_type,
                year_built=2000,
                city="New York",
                state="NY",
                bedrooms=3,
                bathrooms=2,
                sqft=1200,
                lot_sqft=3000,
                latitude=40.712776,
                longitude=-74.005974,

                year_renovated=2010,
                # roofing=" ",
                # garage_type=" ",
                garage=1,
                # heating=" ",
                # cooling=" ",
                # exterior=" ",
                # pool=" ",
                # fireplace=" ",
                description="A beautiful home in New York",
                # realtor=self.realtor,
            )


class SavedFilterModelTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")

    def test_create_saved_filter(self):
        saved_filter = SavedFilter.objects.create(
            name="Test SavedFilter",
            company=self.company,
            filter_type="Client",
            saved_filters="Test filters",
            service_titan_tag=123,
            for_zapier=False,
        )

        self.assertEqual(saved_filter.name, "Test SavedFilter")
        self.assertEqual(saved_filter.company, self.company)
        self.assertEqual(saved_filter.filter_type, "Client")
        self.assertEqual(saved_filter.saved_filters, "Test filters")
        self.assertEqual(saved_filter.service_titan_tag, 123)
        self.assertEqual(saved_filter.for_zapier, False)

    def test_unique_togetherness(self):
        saved_filter_1 = SavedFilter.objects.create(
            name="Test SavedFilter",
            company=self.company,
            filter_type="Client",
            saved_filters="Test filters",
            service_titan_tag=123,
            for_zapier=False,
        )

        with self.assertRaises(Exception):
            saved_filter_2 = SavedFilter.objects.create(
                name="Test SavedFilter",
                company=self.company,
                filter_type="Client",
                saved_filters="Different filters",
                service_titan_tag=456,
                for_zapier=True,
            )
