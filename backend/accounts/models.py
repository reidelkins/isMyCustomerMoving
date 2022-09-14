import os

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.models import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext as _
import uuid
from datetime import datetime, timedelta


# This is just an example no need to keep them
ROLE_CHOICES = (

    ('Backend Developer', 'Backend Developer'),
    ('Full Stack Designer', 'Full Stack Designer'),
    ('Front End Developer', 'Front End Developer'),
    ('Full Stack Developer', 'Full Stack Developer'),
)

STATUS_CHOICES = (

    ('active', 'ACTIVE'),
    ('banned', 'BANNED'),
    ('admin', 'ADMIN'),
)

COMPANY_NAME = (

    ('test', 'test'),
    ('kinetico_knoxville', 'kinetico_knoxville'),
    ('isMyCustomerMoving', 'isMyCustomerMoving')
)

COMPANY_TOKEN = (

    ('test', 'test'),
    ('1qaz2wsx', '1qaz2wsx'),
    ('a29tp(u%hy@a5_p3x_d%!ct)m8r_@qj-skvksrz7id=k8nd9^m', 'a29tp(u%hy@a5_p3x_d%!ct)m8r_@qj-skvksrz7id=k8nd9^m')
)

STATUS = [
    ('For Sale','For Sale'),
    ('For Rent','For Rent'),
    ('Recently Sold (6)','Recently Sold (6)'),
    ('Recently Sold (12)','Recently Sold (12)'),
    ('Off Market', 'Off Market'),
    ('No Change', 'No Change')
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

class Company(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100, choices=COMPANY_NAME)
    accessToken = models.CharField(
        max_length=100, choices=COMPANY_TOKEN)
    avatarUrl = models.ImageField(
        upload_to='customers', null=True, blank=True, default='/placeholder.png')

class ZipCode(models.Model):
    zipCode = models.IntegerField(primary_key=True, unique=True)
    lastUpdated = models.DateField(default=(datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d'))

class Client(models.Model):
    id = models.UUIDField(primary_key=True, unique=True,
                          default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    zipCode = models.ForeignKey(ZipCode, blank=True, null=True, on_delete=models.SET_NULL)
    company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=STATUS, default='No Change')

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
    listed = models.CharField(max_length=25, default=str(datetime.now()))

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
    role = models.CharField(
        max_length=100, choices=ROLE_CHOICES, default='Full Stack Developer')
    company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.CASCADE)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        ordering = ["-id"]


