from rest_framework import serializers

from accounts.serializers import EnterpriseSerializer, BasicCompanySerializer
from .models import Client, ClientUpdate, HomeListing, Referral

class ClientUpdateSerializer(serializers.ModelSerializer):
    status = serializers.CharField(max_length=100)
    date = serializers.DateField()
    listed = serializers.CharField(max_length=100)
    note = serializers.CharField(max_length=100)
    contacted = serializers.BooleanField()
    error_flag = serializers.BooleanField()

    class Meta:
        model = ClientUpdate
        fields = ('id', 'status', 'date', 'listed', 'note', 'contacted', 'error_flag')
        read_only_fields = fields

class ClientListSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=100)
    address = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    zipCode = serializers.SerializerMethodField(read_only=True)
    status = serializers.CharField(max_length=100)
    contacted = serializers.BooleanField()
    note = serializers.CharField(max_length=100)
    phoneNumber = serializers.CharField(max_length=100)
    price = serializers.IntegerField()
    housingType = serializers.CharField(max_length=100)
    year_built = serializers.IntegerField()
    tags = serializers.SerializerMethodField(read_only=True)
    equipmentInstalledDate = serializers.DateField()
    error_flag = serializers.BooleanField()
    clientUpdates_client = ClientUpdateSerializer(many=True, read_only=True)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    serviceTitanCustomerSinceYear = serializers.SerializerMethodField()

    def get_zipCode(self, obj):
        return obj.zipCode.zipCode
    
    def get_tags(self, obj):
        return obj.tag.all().values_list('tag', flat=True)
    
    def get_serviceTitanCustomerSinceYear(self, obj):
        if obj.serviceTitanCustomerSince is None:
            return 1900
        return obj.serviceTitanCustomerSince.year

    class Meta:
        model = Client
        fields = ('id', 'name', 'address', 'city', 'state', 'zipCode', 'status', 'contacted', 'note', 'phoneNumber', 'clientUpdates_client', 'price', 'housingType', 'year_built', 'tags','error_flag', 'equipmentInstalledDate', 'latitude', 'longitude', 'serviceTitanCustomerSinceYear')
        read_only_fields = fields

class ZapierClientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100)
    address = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    zipCode = serializers.SerializerMethodField(read_only=True)
    phoneNumber = serializers.CharField(max_length=100)

    def get_zipCode(self, obj):
        return obj.zipCode.zipCode
    
    class Meta:
        model = Client
        fields = ('name', 'address', 'city', 'state', 'zipCode', 'phoneNumber')
        read_only_fields = fields


class HomeListingSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    address = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    zipCode = serializers.SerializerMethodField(read_only=True)
    listed = serializers.CharField(max_length=30)
    price = serializers.IntegerField()
    housingType = serializers.CharField(max_length=100)
    year_built = serializers.IntegerField()
    tags = serializers.SerializerMethodField(read_only=True)

    def get_zipCode(self, obj):
        return obj.zipCode.zipCode
    
    def get_tags(self, obj):
        return obj.tag.all().values_list('tag', flat=True)
    
    class Meta:
        model = HomeListing
        fields = ('id', 'address', 'state', 'city', 'listed', 'zipCode', 'price', 'housingType', 'year_built', 'tags')

class ReferralSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    enterprise = EnterpriseSerializer(required=False)
    referredFrom = BasicCompanySerializer(required=True)
    referredTo = BasicCompanySerializer(required=True)
    client = ClientListSerializer(read_only=True)
    contacted = serializers.BooleanField()

    class Meta:
        model = Referral
        fields = ['id', 'enterprise', 'referredFrom', 'referredTo', 'client', 'contacted']

