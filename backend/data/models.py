from django.db import models
from django.core.exceptions import ValidationError
import uuid
from datetime import datetime, timedelta

from django.forms import JSONField


# from accounts.models import Company
STATUS = [
    ('House For Sale','House For Sale'),
    ('House For Rent','House For Rent'),
    ('House Recently Sold (6)','House Recently Sold (6)'),
    ('Recently Sold (12)','Recently Sold (12)'),
    ('Taken Off Market', 'Taken Off Market'),
    ('No Change', 'No Change')
]

def zipTime():
    return (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

class ZipCode(models.Model):
    zipCode = models.CharField(max_length=5, primary_key=True, unique=True)
    lastUpdated = models.DateField(default=zipTime)

    def __str__(self):
        return self.zipCode

class Client(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    zipCode = models.ForeignKey(ZipCode, on_delete=models.SET_NULL, blank=True, null=True,  related_name='client_zipCode')
    company = models.ForeignKey("accounts.Company", blank=True, null=True, on_delete=models.SET_NULL, related_name='client_company')
    status = models.CharField(max_length=25, choices=STATUS, default='No Change')
    city = models.CharField(max_length=40, blank=True, null=True)
    state = models.CharField(max_length=31, blank=True, null=True)
    contacted = models.BooleanField(default=False)
    note = models.TextField(default="", blank=True, null=True)
    servTitanID = models.IntegerField(blank=True, null=True)
    phoneNumber = models.CharField(max_length=100, blank=True, null=True)
    price = models.IntegerField(default=0, blank=True, null=True)
    housingType = models.CharField(max_length=100, default=" ", blank=True, null=True)
    year_built = models.IntegerField(default=0, blank=True, null=True)
    tag = models.ManyToManyField("HomeListingTags", blank=True, related_name='client_tags')
    equipmentInstalledDate = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=True)
    error_flag = models.BooleanField(default=False)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    revenue = models.IntegerField(default=0, blank=True, null=True)
    serviceTitanCustomerSince = models.DateField(blank=True, null=True)
    usps_address = models.CharField(max_length=100, blank=True, null=True)
    usps_different = models.BooleanField(default=False)

    class Meta:
        unique_together = ('company', 'name', 'address')

def formatToday():
    return datetime.today().strftime('%Y-%m-%d')

class ClientUpdate(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='clientUpdates_client')
    date = models.DateField(default=formatToday)
    status = models.CharField(max_length=25, choices=STATUS, default='No Change', blank=True, null=True)
    listed = models.CharField(max_length=30, blank=True, null=True)
    note = models.TextField(default="", blank=True, null=True)
    contacted = models.BooleanField(blank=True, null=True)
    error_flag = models.BooleanField(blank=True, null=True)

class ScrapeResponse(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    date = models.DateField(default=formatToday)
    response = models.TextField(default="")
    zip = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=25, choices=STATUS, default='No Change', blank=True, null=True)
    url = models.CharField(max_length=100, blank=True, null=True)

class Realtor(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    url = models.CharField(max_length=100)

class HomeListing(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    zipCode = models.ForeignKey(ZipCode, blank=True, null=True, on_delete=models.SET_NULL, related_name='homeListing_zipCode')
    address = models.CharField(max_length=100)
    status = models.CharField(max_length=25, choices=STATUS, default='Off Market')
    listed = models.CharField(max_length=30, default=" ")
    ScrapeResponse = models.ForeignKey(ScrapeResponse, blank=True, null=True, on_delete=models.SET_NULL, related_name='homeListing_ScrapeResponse')
    price = models.IntegerField(default=0, blank=True, null=True)
    housingType = models.CharField(max_length=100, default=" ")
    year_built = models.IntegerField(default=0, blank=True, null=True)
    tag = models.ManyToManyField("HomeListingTags", blank=True, related_name='homeListing_tag')
    # tags = JSONField(default=list)     this is how to greatly reduce the amount of data in the table
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
    roofing = models.CharField(max_length=100, default=" ", blank=True, null=True)
    garage_type = models.CharField(max_length=100, default=" ", blank=True, null=True)
    garage = models.IntegerField(default=0, blank=True, null=True)
    heating = models.CharField(max_length=100, default=" ", blank=True, null=True)
    cooling = models.CharField(max_length=100, default=" ", blank=True, null=True)
    heatingCoolingDescription = models.TextField( default=" ", blank=True, null=True)
    interiorFeaturesDescription = models.TextField(default=" ", blank=True, null=True)
    exterior = models.CharField(max_length=100, default=" ", blank=True, null=True)
    pool = models.CharField(max_length=100, default=" ", blank=True, null=True)
    fireplace = models.CharField(max_length=100, default=" ", blank=True, null=True)
    description = models.TextField(default=" ", blank=True, null=True)
    realtor = models.ForeignKey(Realtor, blank=True, null=True, on_delete=models.SET_NULL, related_name='homeListing_realtor')

    class Meta:
        unique_together = ('address', 'status', 'city', 'state')
    
class HomeListingTags(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    tag = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.tag


class Task(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    completed = models.BooleanField(default=False)
    deletedClients = models.IntegerField(default=0)

class Referral(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    enterprise = models.ForeignKey("accounts.Enterprise", on_delete=models.CASCADE, blank=True, null=True)
    referredFrom = models.ForeignKey("accounts.Company", on_delete=models.SET_NULL, related_name='referredFrom', blank=True, null=True)
    referredTo = models.ForeignKey("accounts.Company", on_delete=models.SET_NULL, related_name='referredTo', blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='referralClient', blank=True, null=True)
    contacted = models.BooleanField(default=False)

    # on save, make sure both the referredFrom and referredTo are not the same and they are part of the franchise
    def save(self, *args, **kwargs):
        if self.referredFrom == self.referredTo:
            raise ValidationError("Referred From and Referred To cannot be the same")
        if self.referredFrom.enterprise != self.enterprise or self.referredTo.enterprise != self.enterprise:
            raise ValidationError("Both Referred From and Referred To must be part of the enterprise")
        if self.client.company.enterprise != self.enterprise:
            raise ValidationError("Client must be part of the enterprise")
        if self.client.company != self.referredFrom:
            raise ValidationError("Client must have the same company as Referred From")
            
        super(Referral, self).save(*args, **kwargs)

class SavedFilter(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                            default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    company = models.ForeignKey("accounts.Company", on_delete=models.CASCADE, blank=True, null=True)
    forExistingClient = models.BooleanField(default=False)
    savedFilters = models.CharField(max_length=1000, blank=True, null=True)
    serviceTitanTag = models.IntegerField(blank=True, null=True)
    forZapier = models.BooleanField(default=False)

    class Meta:
        unique_together = ('name', 'company', 'forExistingClient')    

