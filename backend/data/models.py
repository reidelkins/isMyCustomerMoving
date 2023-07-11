from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import uuid

# Define status choices
STATUS = [
    ("House For Sale", "House For Sale"),
    ("House For Rent", "House For Rent"),
    ("House Recently Sold (6)", "House Recently Sold (6)"),
    ("Recently Sold (12)", "Recently Sold (12)"),
    ("Taken Off Market", "Taken Off Market"),
    ("No Change", "No Change"),
]

SAVED_FILTER_TYPE = [
    ("Recently Sold", "Recently Sold"),
    ("For Sale", "For Sale"),
    ("Client", "Client"),
]


# Function to return yesterday's date
def zip_time():
    return (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")


# ZipCode model
class ZipCode(models.Model):
    zip_code = models.CharField(max_length=5, primary_key=True, unique=True)
    last_updated = models.DateField(default=zip_time)

    def __str__(self):
        return self.zip_code


# Client model
class Client(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    zip_code = models.ForeignKey(
        ZipCode,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="client_zip_code",
    )
    company = models.ForeignKey(
        "accounts.Company",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="client_company",
    )
    status = models.CharField(
        max_length=25, choices=STATUS, default="No Change"
    )
    city = models.CharField(max_length=40, blank=True, null=True)
    state = models.CharField(max_length=31, blank=True, null=True)
    contacted = models.BooleanField(default=False)
    note = models.TextField(default="", blank=True, null=True)
    serv_titan_id = models.IntegerField(blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    price = models.IntegerField(default=0, blank=True, null=True)
    housing_type = models.CharField(
        max_length=100, default=" ", blank=True, null=True
    )
    year_built = models.IntegerField(default=0, blank=True, null=True)
    tag = models.ManyToManyField(
        "HomeListingTags", blank=True, related_name="client_tags"
    )
    equipment_installed_date = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=True)
    error_flag = models.BooleanField(default=False)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    revenue = models.IntegerField(default=0, blank=True, null=True)
    service_titan_customer_since = models.DateField(blank=True, null=True)
    usps_address = models.CharField(max_length=100, blank=True, null=True)
    usps_different = models.BooleanField(default=False)
    bedrooms = models.IntegerField(default=0, blank=True, null=True)
    bathrooms = models.IntegerField(default=0, blank=True, null=True)
    sqft = models.IntegerField(default=0, blank=True, null=True)
    lot_sqft = models.IntegerField(default=0, blank=True, null=True)

    new_address = models.CharField(max_length=100, blank=True, null=True)
    new_city = models.CharField(max_length=40, blank=True, null=True)
    new_state = models.CharField(max_length=31, blank=True, null=True)
    new_zip_code = models.ForeignKey(
        ZipCode,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="client_new_zip_code",
    )

    class Meta:
        unique_together = ("company", "name", "address")

    def __str__(self):
        return f"{self.name}_{self.company}"


# Function to return today's date
def format_today():
    return datetime.today().strftime("%Y-%m-%d")


# ClientUpdate model
class ClientUpdate(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="client_updates_client"
    )
    date = models.DateField(default=format_today)
    status = models.CharField(
        max_length=25,
        choices=STATUS,
        default="No Change",
        blank=True,
        null=True,
    )
    listed = models.CharField(max_length=30, blank=True, null=True)
    note = models.TextField(default="", blank=True, null=True)
    contacted = models.BooleanField(blank=True, null=True, default=False)
    error_flag = models.BooleanField(blank=True, null=True, default=False)


# ScrapeResponse model
class ScrapeResponse(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    date = models.DateField(default=format_today)
    response = models.TextField(default="")
    zip = models.IntegerField(blank=True, null=True)
    status = models.CharField(
        max_length=25,
        choices=STATUS,
        default="No Change",
        blank=True,
        null=True,
    )
    url = models.CharField(max_length=100, blank=True, null=True)


# Realtor model
class Realtor(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    url = models.CharField(max_length=100)


# HomeListing model
class HomeListing(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    zip_code = models.ForeignKey(
        ZipCode,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="home_listing_zip_code",
    )
    address = models.CharField(max_length=100)
    status = models.CharField(
        max_length=25, choices=STATUS, default="Off Market"
    )
    listed = models.CharField(max_length=30, default=" ")
    price = models.IntegerField(default=0, blank=True, null=True)
    housing_type = models.CharField(
        max_length=100, default=" ", blank=True, null=True
    )
    year_built = models.IntegerField(default=0, blank=True, null=True)
    tag = models.ManyToManyField(
        "HomeListingTags", blank=True, related_name="home_listing_tag"
    )
    city = models.CharField(max_length=40, blank=True, null=True)
    state = models.CharField(max_length=31, blank=True, null=True)
    bedrooms = models.IntegerField(default=0, blank=True, null=True)
    bathrooms = models.IntegerField(default=0, blank=True, null=True)
    sqft = models.IntegerField(default=0, blank=True, null=True)
    lot_sqft = models.IntegerField(default=0, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    permalink = models.CharField(max_length=100, blank=True, null=True)
    year_renovated = models.IntegerField(default=0, blank=True, null=True)
    roofing = models.CharField(
        max_length=100, default=" ", blank=True, null=True
    )
    garage_type = models.CharField(
        max_length=100, default=" ", blank=True, null=True
    )
    garage = models.IntegerField(default=0, blank=True, null=True)
    heating = models.CharField(
        max_length=100, default=" ", blank=True, null=True
    )
    cooling = models.CharField(
        max_length=100, default=" ", blank=True, null=True
    )
    heatingCoolingDescription = models.TextField(
        default=" ", blank=True, null=True)
    interiorFeaturesDescription = models.TextField(
        default=" ", blank=True, null=True)
    exterior = models.CharField(
        max_length=100, default=" ", blank=True, null=True
    )
    pool = models.CharField(
        max_length=100, default=" ", blank=True, null=True
    )
    fireplace = models.CharField(
        max_length=100, default=" ", blank=True, null=True
    )
    description = models.TextField(default=" ", blank=True, null=True)
    realtor = models.ForeignKey(
        Realtor,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="home_listing_realtor",
    )

    class Meta:
        unique_together = ("address", "status", "city", "state")

    def __str__(self):
        return f"{self.address}_{self.status}"


# HomeListingTags model
class HomeListingTags(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    tag = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.tag


# Task model
class Task(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    completed = models.BooleanField(default=False)
    deleted_clients = models.IntegerField(default=0)


# Referral model
class Referral(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    enterprise = models.ForeignKey(
        "accounts.Enterprise", on_delete=models.CASCADE, blank=True, null=True
    )
    referred_from = models.ForeignKey(
        "accounts.Company",
        on_delete=models.SET_NULL,
        related_name="referred_from",
        blank=True,
        null=True,
    )
    referred_to = models.ForeignKey(
        "accounts.Company",
        on_delete=models.SET_NULL,
        related_name="referred_to",
        blank=True,
        null=True,
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="referral_client",
        blank=True,
        null=True,
    )
    contacted = models.BooleanField(default=False)

    # on save, make sure both the referred_from and referred_to
    #  are not the same and they are part of the franchise
    def save(self, *args, **kwargs):
        if self.referred_from == self.referred_to:
            raise ValidationError(
                "Referred From and Referred To cannot be the same"
            )
        if (
            self.referred_from.enterprise != self.enterprise
            or self.referred_to.enterprise != self.enterprise
        ):
            raise ValidationError(
                "Both Referred From and Referred To must be part of the enterprise"
            )
        if self.client.company.enterprise != self.enterprise:
            raise ValidationError("Client must be part of the enterprise")
        if self.client.company != self.referred_from:
            raise ValidationError(
                "Client must have the same company as Referred From"
            )

        super(Referral, self).save(*args, **kwargs)


# SavedFilter model
class SavedFilter(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    name = models.CharField(max_length=100)
    company = models.ForeignKey(
        "accounts.Company", on_delete=models.CASCADE, blank=True, null=True
    )
    filter_type = models.CharField(
        max_length=25, choices=SAVED_FILTER_TYPE, default="Client"
    )
    saved_filters = models.CharField(max_length=1000, blank=True, null=True)
    service_titan_tag = models.IntegerField(blank=True, null=True)
    for_zapier = models.BooleanField(default=False)

    class Meta:
        unique_together = ("name", "company", "filter_type")
