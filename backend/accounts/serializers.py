from rest_framework import serializers
from .models import CustomUser, Company, Enterprise
from data.models import ClientUpdate, Client
from payments.serializers import ProductSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.crypto import get_random_string
from django.contrib.auth.models import update_last_login
import logging


# Basic Company Serializer
class BasicCompanySerializer(serializers.ModelSerializer):
    users_count = serializers.SerializerMethodField()
    leads_count = serializers.SerializerMethodField()
    clients_count = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "users_count",
            "leads_count",
            "clients_count",
        ]

    def get_users_count(self, obj):
        return CustomUser.objects.filter(company=obj).count()

    def get_leads_count(self, obj):
        return (
            ClientUpdate.objects.filter(client__company=obj)
            .exclude(status="No Change")
            .count()
        )

    def get_clients_count(self, obj):
        return Client.objects.filter(company=obj).count()

    def get_service_area_zip_codes(self, obj):
        return list(obj.service_area_zip_codes.values_list('zip_code', flat=True))


# Company Serializer with more detailed information
class CompanySerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    service_area_zip_codes = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "crm",
            "phone",
            "email",
            "tenant_id",
            "client_id",
            "client_secret",
            "stripe_id",
            "service_titan_for_sale_tag_id",
            "service_titan_recently_sold_tag_id",
            "service_titan_for_sale_contacted_tag_id",
            "service_titan_recently_sold_contacted_tag_id",
            "service_titan_sold_date_custom_field_id",
            "service_titan_listed_date_custom_field_id",
            "for_sale_purchased",
            "recently_sold_purchased",
            "service_titan_customer_sync_option",
            "product",
            "service_titan_app_version",
            "service_area_zip_codes"
        ]

    def create(self, validated_data):
        if Company.objects.filter(name=validated_data["name"]).exists():
            return False
        return Company.objects.create(
            **validated_data, access_token=get_random_string(length=32)
        )

    def get_service_area_zip_codes(self, obj):
        return list(obj.service_area_zip_codes.values_list('zip_code', flat=True))


# Serializer for Enterprise model
class EnterpriseSerializer(serializers.ModelSerializer):
    companies = BasicCompanySerializer(many=True, read_only=True)

    class Meta:
        model = Enterprise
        fields = ["id", "name", "companies"]


# Serializer for generating JWT token pairs
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            serializer = UserSerializerWithToken(self.user).data
            update_last_login(None, self.user)
            for k, v in serializer.items():
                data[k] = v
            if not self.user.is_verified:
                logging.error("User is not verified")
                raise serializers.ValidationError("User is not verified")
            return data
        except Exception as e:
            logging.exception("An error occurred during validation")
            raise e


# Serializer for User model
class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    phone = serializers.CharField(max_length=20)
    email = serializers.EmailField(max_length=100)
    is_verified = serializers.BooleanField(read_only=True)
    status = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    company = CompanySerializer(read_only=True)
    access_token = serializers.CharField(read_only=True)
    otp_enabled = serializers.BooleanField(read_only=True)
    otp_base32 = serializers.CharField(read_only=True)
    otp_auth_url = serializers.CharField(read_only=True)
    is_enterprise_owner = serializers.BooleanField(read_only=True)
    finished_st_integration = serializers.SerializerMethodField(
        read_only=True
    )

    def get_finished_st_integration(self, obj):
        return (
            obj.company.tenant_id is not None
            and obj.company.client_id is not None
            and obj.company.client_secret is not None
        )


# Serializer for User model with JWT tokens
class UserSerializerWithToken(UserSerializer):
    access_token = serializers.SerializerMethodField(read_only=True)
    refresh_token = serializers.SerializerMethodField(read_only=True)

    def get_access_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

    def get_refresh_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token)


# Serializer for User model for lists
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "status",
            "is_enterprise_owner",
        )
