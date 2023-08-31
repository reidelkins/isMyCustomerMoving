from rest_framework import serializers


from accounts.serializers import EnterpriseSerializer, BasicCompanySerializer
from .models import (
    Client,
    ClientUpdate,
    HomeListing,
    HomeListingTags,
    Realtor,
    Referral
)


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


class ClientUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientUpdate
        fields = ["id", "date", "status", "listed", "note", "contacted"]
        read_only_fields = fields


# class ClientListSerializer(serializers.Serializer):
#     zip_code = serializers.CharField(source='zip_code.zip_code')
#     tag = serializers.SerializerMethodField()
#     service_titan_customer_since_year = serializers.IntegerField(default=1900)
#     client_updates_client = ClientUpdateSerializer(many=True, read_only=True)

#     def get_tag(self, obj):
#         return [tag.tag for tag in obj.tag.all()]

#     class Meta:
#         model = Client
#         fields = [
#             f.name
#             for f in Client._meta.fields
#             if f.name != "service_titan_customer_since"
#             and f.name != "zip_code"
#         ] + [
#             "zip_code",
#             "tag",
#             "service_titan_customer_since_year",
#             "client_updates_client",
#         ]
#         read_only_fields = fields

# Use normal serializer instead of a ModelSerializer
class ClientListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=255)
    zip_code = serializers.CharField(source='zip_code.zip_code')
    city = serializers.CharField(max_length=255)
    state = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=255)
    contacted = serializers.BooleanField(default=False)
    status = serializers.CharField(max_length=255)
    note = serializers.CharField()
    price = serializers.IntegerField(default=0)
    housing_type = serializers.CharField(max_length=255)
    year_built = serializers.IntegerField(default=1900)
    tag = serializers.SerializerMethodField()
    equipment_installed_date = serializers.DateField(default=1900)
    latitude = serializers.FloatField(default=0)
    longitude = serializers.FloatField(default=0)
    revenue = serializers.IntegerField(default=0)
    service_titan_customer_since_year = serializers.IntegerField(default=1900)
    service_titan_lifetime_revenue = serializers.IntegerField(default=0)
    service_titan_customer_since_year = serializers.IntegerField(default=1900)
    client_updates_client = ClientUpdateSerializer(many=True, read_only=True)

    def get_tag(self, obj):
        return [tag.tag for tag in obj.tag.all()]


class ZapierClientSerializer(serializers.ModelSerializer):
    zip_code = serializers.CharField(source='zip_code.zip_code')

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
    zip_code = serializers.CharField(source='zip_code.zip_code')
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
    client = ClientListSerializer()

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


class RealtorSerializer(serializers.ModelSerializer):
    listing_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Realtor
        fields = ('id', 'name', 'company', 'phone',
                  'email', 'url', 'listing_count')
