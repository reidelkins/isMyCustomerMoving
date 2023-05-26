from rest_framework import serializers
from .models import CustomUser, Company, Enterprise
from data.models import ClientUpdate, Client
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.crypto import get_random_string
from django.contrib.auth.models import update_last_login



class BasicCompanySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=100)
    class Meta:
        model = Company
        fields = ['id', 'name']


class CompanySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20)
    email = serializers.EmailField(max_length=100)
    stripeID = serializers.CharField(max_length=100, required=False)
    recentlySoldPurchased = serializers.BooleanField(default=False)
    crm = serializers.CharField(max_length=100, required=False)
    product = serializers.SerializerMethodField('get_product', read_only=True)


    # service titan
    tenantID = serializers.CharField(max_length=100, required=False)
    clientID = serializers.CharField(max_length=100, required=False)
    serviceTitanForRentTagID = serializers.CharField(max_length=100, required=False)
    serviceTitanForSaleTagID = serializers.CharField(max_length=100, required=False)
    serviceTitanRecentlySoldTagID = serializers.CharField(max_length=100, required=False)
    serviceTitanForSaleContactedTagID = serializers.CharField(max_length=100, required=False)
    serviceTitanSoldContactedTagID = serializers.CharField(max_length=100, required=False)

    users_count = serializers.SerializerMethodField()
    leads_count = serializers.SerializerMethodField()
    clients_count = serializers.SerializerMethodField()
    

    def create(self, validated_data):
        if Company.objects.filter(name=validated_data['name']).exists():
            return False
        return Company.objects.create(**validated_data, accessToken=get_random_string(length=32))
    
    def get_product(self, obj):
        if obj.product:
            return obj.product.id
        else:
            return "No product"
        
    def get_users_count(self, obj):
        return CustomUser.objects.filter(company=obj).count()

    def get_leads_count(self, obj):
        return ClientUpdate.objects.filter(client__company=obj).exclude(status="No Change").count()
    
    def get_clients_count(self, obj):
        return Client.objects.filter(company=obj).count()
    class Meta:
        model = Company
        fields=['id', 'name', 'crm', 'phone', 'email', 'tenantID', 'clientID', 'stripeID', 'serviceTitanForRentTagID', 'serviceTitanForSaleTagID', 'serviceTitanRecentlySoldTagID', 'recentlySoldPurchased', 'serviceTitanForSaleContactedTagID', 'serviceTitanSoldContactedTagID', 'product', 'users_count', 'leads_count', 'clients_count']

class EnterpriseSerializer(serializers.ModelSerializer):
    companies = CompanySerializer(many=True, read_only=True)

    class Meta:
        model = Enterprise
        fields = ['id', 'name', 'companies']

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UserSerializerWithToken(self.user).data
        update_last_login(None, self.user)
        for k, v in serializer.items():
            data[k] = v
        if not self.user.isVerified:
            print("User is not verified")
            raise serializers.ValidationError("User is not verified")
        return data
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        if user.isVerified:
            return token
        else:
            print("User is not verified 2")
            raise serializers.ValidationError("User is not verified. Either you have not verified your email or your account has been disabled. Accounts are disabled if you have not paid for the service. Please contact us reid@ismycustomermoving.com if you have any questions.")

class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    phone = serializers.CharField(max_length=20)
    email = serializers.EmailField(max_length=100)
    isVerified = serializers.BooleanField(read_only=True)
    status = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    company = CompanySerializer(read_only=True)
    accessToken = serializers.CharField(read_only=True)
    otp_enabled = serializers.BooleanField(read_only=True)
    otp_base32 = serializers.CharField(read_only=True)
    otp_auth_url = serializers.CharField(read_only=True)
    is_enterprise_owner = serializers.BooleanField(read_only=True)

    #service titan
    finishedSTIntegration = serializers.SerializerMethodField(read_only=True)
    

    def get_finishedSTIntegration(self, obj):
        return obj.company.tenantID != None and obj.company.clientID != None and obj.company.clientSecret != None


class UserSerializerWithToken(UserSerializer):
    accessToken = serializers.SerializerMethodField(read_only=True)
    refreshToken = serializers.SerializerMethodField(read_only=True)

    def get_accessToken(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

    def get_refreshToken(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token)

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'email', 'status', 'is_enterprise_owner')



