from rest_framework import serializers

from accounts.serializers import EnterpriseSerializer, BasicCompanySerializer
from .models import Client, ClientUpdate, HomeListing, Referral, HomeListingTags


class ClientUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientUpdate
        fields = (
            "id",
            "status",
            "date",
            "listed",
            "note",
            "contacted",
            "error_flag",
        )
        read_only_fields = fields


class ClientListSerializer(serializers.ModelSerializer):
    zipCode = (
        serializers.SerializerMethodField()
    )  # this will call get_zipCode method to get the zipCode
    tag = (
        serializers.SerializerMethodField()
    )  # this will call get_tags method to get the tags
    serviceTitanCustomerSinceYear = serializers.SerializerMethodField()
    clientUpdates_client = ClientUpdateSerializer(many=True, read_only=True)

    def get_zipCode(self, obj):
        return obj.zipCode.zipCode

    def get_tag(self, obj):
        return [tag.tag for tag in obj.tag.all()]

    def get_serviceTitanCustomerSinceYear(self, obj):
        if obj.serviceTitanCustomerSince is None:
            return 1900
        return obj.serviceTitanCustomerSince.year

    class Meta:
        model = Client
        fields = (
            "id",
            "name",
            "address",
            "city",
            "state",
            "zipCode",
            "status",
            "contacted",
            "note",
            "phoneNumber",
            "clientUpdates_client",
            "price",
            "housingType",
            "year_built",
            "tag",
            "error_flag",
            "equipmentInstalledDate",
            "latitude",
            "longitude",
            "serviceTitanCustomerSinceYear",
        )
        read_only_fields = fields


class ZapierClientSerializer(serializers.ModelSerializer):
    zipCode = serializers.SerializerMethodField()

    def get_zipCode(self, obj):
        return obj.zipCode.zipCode

    class Meta:
        model = Client
        fields = ("name", "address", "city", "state", "zipCode", "phoneNumber")
        read_only_fields = fields


class HomeListingTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeListingTags
        fields = ["tag"]


class HomeListingSerializer(serializers.ModelSerializer):
    zipCode = serializers.StringRelatedField()  # assuming that ZipCode has a __str__
    # method that returns a meaningful string
    tags = HomeListingTagsSerializer(many=True, read_only=True)

    class Meta:
        model = HomeListing
        fields = [
            "id",
            "zipCode",
            "address",
            "listed",
            "price",
            "housingType",
            "year_built",
            "tags",
            "city",
            "state",
            "bedrooms",
            "bathrooms",
            "sqft",
            "lot_sqft",
            "roofing",
            "garage_type",
            "garage",
            "heating",
            "cooling",
            "exterior",
            "pool",
            "fireplace",
        ]


class ReferralSerializer(serializers.ModelSerializer):
    enterprise = EnterpriseSerializer(required=False)
    referredFrom = BasicCompanySerializer(required=True)
    referredTo = BasicCompanySerializer(required=True)
    client = ClientListSerializer(read_only=True)

    class Meta:
        model = Referral
        fields = [
            "id",
            "enterprise",
            "referredFrom",
            "referredTo",
            "client",
            "contacted",
        ]
        read_only_fields = fields
