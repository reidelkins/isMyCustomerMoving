from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import EmailMessage
from django.db import models
from django.utils.translation import gettext as _
from django.contrib.postgres.fields import ArrayField
import uuid
from datetime import datetime, timedelta
from django.utils.crypto import get_random_string
from django.conf import settings
from django.template.loader import get_template
from django.db import transaction
from payments.models import Product
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.exceptions import TokenError

STATUS_CHOICES = (
    ("active", "ACTIVE"),
    ("banned", "BANNED"),
    ("admin", "ADMIN"),
    ("pending", "PENDING"),
)

STATUS = [
    ("House For Sale", "House For Sale"),
    ("House For Rent", "House For Rent"),
    ("House Recently Sold (6)", "House Recently Sold (6)"),
    ("Recently Sold (12)", "Recently Sold (12)"),
    ("Taken Off Market", "Taken Off Market"),
    ("No Change", "No Change"),
]

PAY_TIER = [
    ("Free", "Free"),
    ("Basic", "Basic"),
    ("Premium", "Premium"),
    ("Enterprise", "Enterprise"),
]

CRM = [
    ("ServiceTitan", "ServiceTitan"),
    ("HubSpot", "HubSpot"),
    ("Zoho", "Zoho"),
    ("Salesforce", "Salesforce"),
    ("FieldEdge", "FieldEdge"),
    ("None", "None"),
]

CLIENT_OPTIONS = [
    ("option1", "option1"),
    ("option2", "option2"),
    ("option3", "option3"),
]


def create_access_token():
    return get_random_string(length=32)


def zip_time():
    return (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")


def format_today():
    return datetime.today().strftime("%Y-%m-%d")


def utc_tomorrow():
    return datetime.utcnow() + timedelta(days=1)


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class Enterprise(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Company(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    name = models.CharField(max_length=100, unique=True)
    access_token = models.CharField(
        default=create_access_token, max_length=100
    )
    product = models.ForeignKey(
        Product,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        default=None,
    )
    phone = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    stripe_id = models.CharField(max_length=100, blank=True, null=True)
    crm = models.CharField(max_length=100, choices=CRM, default="None")
    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="companies",
    )
    # Hubspot
    hubspot_api_key = models.CharField(max_length=100, blank=True, null=True)

    # Service Titan
    service_titan_app_version = models.IntegerField(blank=True, null=True)
    tenant_id = models.IntegerField(blank=True, null=True)
    client_id = models.CharField(max_length=100, blank=True, null=True)
    client_secret = models.CharField(max_length=100, blank=True, null=True)
    service_titan_for_sale_tag_id = models.IntegerField(blank=True, null=True)
    service_titan_for_rent_tag_id = models.IntegerField(blank=True, null=True)
    service_titan_recently_sold_tag_id = models.IntegerField(
        blank=True, null=True
    )
    service_titan_for_sale_contacted_tag_id = models.IntegerField(
        blank=True, null=True
    )
    service_titan_recently_sold_contacted_tag_id = models.IntegerField(
        blank=True, null=True
    )
    service_titan_sold_date_custom_field_id = models.IntegerField(
        blank=True, null=True)
    service_titan_listed_date_custom_field_id = models.IntegerField(
        blank=True, null=True)
    for_sale_purchased = models.BooleanField(default=False)
    recently_sold_purchased = models.BooleanField(default=False)
    service_titan_customer_sync_option = models.CharField(
        max_length=100, choices=CLIENT_OPTIONS, default="option1"
    )

    # Salesforce
    sf_access_token = models.CharField(max_length=100, blank=True, null=True)
    sf_refresh_token = models.CharField(max_length=100, blank=True, null=True)

    # Zapier
    zapier_for_sale = models.CharField(max_length=100, blank=True, null=True)
    zapier_sold = models.CharField(max_length=100, blank=True, null=True)
    zapier_recently_sold = models.CharField(
        max_length=100, blank=True, null=True
    )
    service_area_zip_codes = models.ManyToManyField(
        "data.ZipCode", blank=True, related_name="service_area_zip_codes"
    )
    client_tags = ArrayField(models.CharField(max_length=200),
                             blank=True, null=True, default=list)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    username = None
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    email = models.EmailField(_("email address"), unique=True)
    is_verified = models.BooleanField(default=False)
    status = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default="active"
    )
    phone = models.CharField(max_length=100, blank=True, null=True)
    company = models.ForeignKey(
        Company, blank=True, null=True, on_delete=models.CASCADE
    )
    enterprise = models.ForeignKey(
        Enterprise,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="users",
    )
    is_enterprise_owner = models.BooleanField(default=False)
    otp_enabled = models.BooleanField(default=False)
    otp_verified = models.BooleanField(default=False)
    otp_base32 = models.CharField(max_length=255, null=True, blank=True)
    otp_auth_url = models.CharField(max_length=255, null=True, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.company and not self.enterprise:
            self.enterprise = self.company.enterprise
        super().save(*args, **kwargs)

    @transaction.atomic
    def delete_with_tokens(self):
        user_refresh_tokens = OutstandingToken.objects.filter(user=self)
        for token in user_refresh_tokens:
            try:
                refresh_token = RefreshToken(token.token)
                refresh_token.blacklist()
            except TokenError:
                pass
        self.delete()

    class Meta:
        ordering = ["-id"]


class InviteToken(models.Model):
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    email = models.EmailField()
    company = models.ForeignKey(
        Company, blank=True, null=True, on_delete=models.CASCADE
    )
    expiration = models.DateTimeField(default=utc_tomorrow)


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, instance, reset_password_token, *args, **kwargs
):
    if CustomUser.objects.filter(
        email=reset_password_token.user.email
    ).exists():
        subject = "Password Reset: IsMyCustomerMoving.com"
        message = get_template("resetPassword.html").render(
            {"token": reset_password_token.key}
        )
        msg = EmailMessage(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [reset_password_token.user.email]
            # html_message=message,
        )
        msg.content_subtype = "html"
        msg.send()
