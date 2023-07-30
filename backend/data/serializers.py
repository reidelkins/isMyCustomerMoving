from rest_framework import serializers

from accounts.serializers import EnterpriseSerializer, BasicCompanySerializer
from .models import (
    Client,
    ClientUpdate,
    HomeListing,
    Referral,
    HomeListingTags,
)


class ClientUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientUpdate
        fields = [f.name for f in ClientUpdate._meta.fields]
        read_only_fields = fields


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            "name",
            "address",
            "city",
            "state",
            "zip_code",
        ]


class ClientListSerializer(serializers.ModelSerializer):
    zip_code = serializers.SerializerMethodField()
    tag = serializers.SerializerMethodField()
    service_titan_customer_since_year = serializers.SerializerMethodField()
    client_updates_client = ClientUpdateSerializer(many=True, read_only=True)

    def get_zip_code(self, obj):
        return obj.zip_code.zip_code

    def get_tag(self, obj):
        return [tag.tag for tag in obj.tag.all()]

    def get_service_titan_customer_since_year(self, obj):
        return (
            obj.service_titan_customer_since.year
            if obj.service_titan_customer_since
            else 1900
        )

    class Meta:
        model = Client
        fields = [
            f.name
            for f in Client._meta.fields
            if f.name != "service_titan_customer_since"
            and f.name != "zip_code"
        ] + [
            "zip_code",
            "tag",
            "service_titan_customer_since_year",
            "client_updates_client",
        ]
        read_only_fields = fields


class ZapierClientSerializer(serializers.ModelSerializer):
    zip_code = serializers.SerializerMethodField()

    def get_zip_code(self, obj):
        return obj.zip_code.zip_code

    class Meta:
        model = Client
        fields = (
            "name",
            "address",
            "city",
            "state",
            "zip_code",
            "phone_number",
        )
        read_only_fields = fields


class HomeListingTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeListingTags
        fields = ["tag"]


class HomeListingSerializer(serializers.ModelSerializer):
    zip_code = serializers.StringRelatedField()
    tags = HomeListingTagsSerializer(many=True, read_only=True)

    class Meta:
        model = HomeListing
        fields = [
            f.name for f in HomeListing._meta.fields if f.name != "zip_code"
        ] + ["zip_code", "tags"]


class ReferralSerializer(serializers.ModelSerializer):
    enterprise = EnterpriseSerializer(required=False)
    referred_from = BasicCompanySerializer(required=True)
    referred_to = BasicCompanySerializer(required=True)
    client = ClientListSerializer(read_only=True)

    class Meta:
        model = Referral
        fields = [
            "contacted",
            "id",
            "enterprise",
            "referred_from",
            "referred_to",
            "client",
        ]
        read_only_fields = fields
