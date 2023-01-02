from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import EmailMessage
from django.db import models
from django.utils.translation import gettext as _
import uuid
from datetime import datetime, timedelta
from django.utils.crypto import get_random_string
from django.conf import settings
from django.template.loader import get_template
from payments.models import Product


STATUS_CHOICES = (

    ('active', 'ACTIVE'),
    ('banned', 'BANNED'),
    ('admin', 'ADMIN'),
    ('pending', 'PENDING'),
)

STATUS = [
    ('For Sale','For Sale'),
    ('For Rent','For Rent'),
    ('Recently Sold (6)','Recently Sold (6)'),
    ('Recently Sold (12)','Recently Sold (12)'),
    ('Off Market', 'Off Market'),
    ('No Change', 'No Change')
]

PAY_TIER = [
    ('Free', 'Free'),
    ('Basic', 'Basic'),
    ('Premium', 'Premium'),
    ('Enterprise', 'Enterprise')
]


class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

def create_access_token():
    return get_random_string(length=32)

class Company(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    accessToken = models.CharField(default=create_access_token, max_length=100)
    avatarUrl = models.ImageField(
        upload_to='customers', null=True, blank=True, default='/placeholder.png')
    email_frequency = models.IntegerField(default=0)
    next_email_date = models.DateField(default=datetime.utcnow)
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.SET_NULL)
    phone = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    tenantID = models.IntegerField(blank=True, null=True)
    clientID = models.CharField(max_length=100, blank=True, null=True)
    clientSecret = models.CharField(max_length=100, blank=True, null=True)


def zipTime():
    return (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

class ZipCode(models.Model):
    zipCode = models.CharField(max_length=5, primary_key=True, unique=True)
    lastUpdated = models.DateField(default=zipTime)

class Client(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    zipCode = models.ForeignKey(ZipCode, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=STATUS, default='No Change')
    city = models.CharField(max_length=30, blank=True, null=True)
    state = models.CharField(max_length=31, blank=True, null=True)
    contacted = models.BooleanField(default=False)
    note = models.TextField(default="")
    servTitanID = models.IntegerField(blank=True, null=True)

class ClientList(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='files')
    # company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.SET_NULL)

class HomeListing(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    zipCode = models.ForeignKey(ZipCode, blank=True, null=True, on_delete=models.SET_NULL)
    address = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS, default='Off Market')
    listed = models.CharField(max_length=30, default=" ")

class CustomUser(AbstractUser):
    username = None
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    isVerified = models.BooleanField(default=False)
    avatarUrl = models.ImageField(
        upload_to='users', null=True, blank=True, default='/placeholder.png')
    status = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default='active')
    company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.CASCADE)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        ordering = ["-id"]

def utc_tomorrow():
    return datetime.utcnow() + timedelta(days=1)

class InviteToken(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    email = models.EmailField()
    company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.CASCADE)
    expiration = models.DateTimeField(default=utc_tomorrow)

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    if CustomUser.objects.filter(email=reset_password_token.user.email).exists(): 
        subject = 'Password Reset: IsMyCustomerMoving.com'
        message = get_template("resetPassword.html").render({
            'token': reset_password_token.key
        })

        msg = EmailMessage(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [reset_password_token.user.email]
                    # html_message=message,
                )
        msg.content_subtype ="html"# Main content is now text/html
        msg.send()