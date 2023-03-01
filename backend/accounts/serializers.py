from rest_framework import serializers
from .models import CustomUser, Company, Franchise
from payments.models import Product
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.crypto import get_random_string
from django.contrib.auth.models import update_last_login

class FranchiseSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100)

    class Meta:
        model = Franchise
        fields = ['name']

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
    franchise = FranchiseSerializer(required=False)


    # service titan
    tenantID = serializers.CharField(max_length=100, required=False)
    clientID = serializers.CharField(max_length=100, required=False)
    serviceTitanForRentTagID = serializers.CharField(max_length=100, required=False)
    serviceTitanForSaleTagID = serializers.CharField(max_length=100, required=False)
    serviceTitanRecentlySoldTagID = serializers.CharField(max_length=100, required=False)

    

    def create(self, validated_data):
        if Company.objects.filter(name=validated_data['name']).exists():
            return False
        return Company.objects.create(**validated_data, accessToken=get_random_string(length=32))
    class Meta:
        model = Company
        fields=['id', 'name', 'crm', 'phone', 'email', 'tenantID', 'clientID', 'stripeID', 'serviceTitanForRentTagID', 'serviceTitanForSaleTagID', 'serviceTitanRecentlySoldTagID', 'recentlySoldPurchased', 'franchise']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UserSerializerWithToken(self.user).data
        update_last_login(None, self.user)
        for k, v in serializer.items():
            data[k] = v
        return data
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        if user.isVerified:
            return token
        else:
            raise serializers.ValidationError("User is not verified")

class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    
    email = serializers.EmailField(max_length=100)
    isVerified = serializers.BooleanField(read_only=True)
    status = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    company = CompanySerializer(read_only=True)
    accessToken = serializers.CharField(read_only=True)
    otp_enabled = serializers.BooleanField(read_only=True)
    otp_base32 = serializers.CharField(read_only=True)
    otp_auth_url = serializers.CharField(read_only=True)

    #service titan
    finishedSTIntegration = serializers.SerializerMethodField(read_only=True)
    

    def get_finishedSTIntegration(self, obj):
        return obj.company.tenantID != None and obj.company.clientID != None and obj.company.clientSecret != None


class UserSerializerWithToken(UserSerializer):
    access = serializers.SerializerMethodField(read_only=True)
    refresh = serializers.SerializerMethodField(read_only=True)

    def get_access(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

    def get_refresh(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token)

# class ClientUpdateSerializer(serializers.ModelSerializer):
#     status = serializers.CharField(max_length=100)
#     date = serializers.DateField()
#     listed = serializers.CharField(max_length=100)
#     note = serializers.CharField(max_length=100)
#     contacted = serializers.BooleanField()

#     class Meta:
#         model = ClientUpdate
#         fields = ('id', 'status', 'date', 'listed', 'note', 'contacted')
#         read_only_fields = fields

# class ClientListSerializer(serializers.ModelSerializer):
#     id = serializers.UUIDField(read_only=True)
#     name = serializers.CharField(max_length=100)
#     address = serializers.CharField(max_length=100)
#     city = serializers.CharField(max_length=100)
#     state = serializers.CharField(max_length=100)
#     zipCode = serializers.SerializerMethodField(read_only=True)
#     status = serializers.CharField(max_length=100)
#     contacted = serializers.BooleanField()
#     note = serializers.CharField(max_length=100)
#     phoneNumber = serializers.CharField(max_length=100)
#     clientUpdates = ClientUpdateSerializer(many=True, read_only=True)


    # def get_zipCode(self, obj):
    #     return obj.zipCode.zipCode

    # class Meta:
    #     model = Client
    #     fields = ('id', 'name', 'address', 'city', 'state', 'zipCode', 'status', 'contacted', 'note', 'phoneNumber', 'clientUpdates')
    #     read_only_fields = fields

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'email', 'status')

# class HomeListingSerializer(serializers.ModelSerializer):
#     id = serializers.UUIDField(read_only=True)
#     address = serializers.CharField(max_length=100)
#     zipCode = serializers.SerializerMethodField(read_only=True)
#     listed = serializers.CharField(max_length=30)

#     def get_zipCode(self, obj):
#         return obj.zipCode.zipCode
    
#     class Meta:
#         model = HomeListing
#         fields = ('id', 'address', 'listed', 'zipCode')

# class ReferralSerializer(serializers.ModelSerializer):
#     id = serializers.UUIDField(read_only=True)
#     franchise = FranchiseSerializer(required=False)
#     referredFrom = BasicCompanySerializer(required=True)
#     referredTo = BasicCompanySerializer(required=True)
#     client = ClientListSerializer(read_only=True)
#     contacted = serializers.BooleanField()

#     class Meta:
#         model = Referral
#         fields = ['id', 'franchise', 'referredFrom', 'referredTo', 'client', 'contacted']

