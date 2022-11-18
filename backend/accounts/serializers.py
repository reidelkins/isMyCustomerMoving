from rest_framework import serializers
from .models import CustomUser, Company, Client
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.crypto import get_random_string

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        serializer = UserSerializerWithToken(self.user).data
        for k, v in serializer.items():
            data[k] = v
        return data

class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    avatarUrl = serializers.ImageField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    isVerified = serializers.BooleanField(read_only=True)
    status = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    # company = serializers.CharField(read_only=True)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    accessToken = serializers.CharField(read_only=True)

    def get_name(self, obj):
        return str(obj.first_name + " " + obj.last_name)

class CompanySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100)
    def create(self, validated_data):
        if Company.objects.filter(name=validated_data['name']).exists():
            return False
        return Company.objects.create(**validated_data, accessToken=get_random_string(length=32))
    class Meta:
        model = Company
        fields=['name']

class UserSerializerWithToken(UserSerializer):
    email = serializers.EmailField(read_only=True)
    access = serializers.SerializerMethodField(read_only=True)
    refresh = serializers.SerializerMethodField(read_only=True)

    def get_access(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

    def get_refresh(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token)

class UploadFileSerializer(serializers.Serializer):
    file = serializers.FileField()
    # company = serializers.CharField()

class ClientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('id', 'name', 'address', 'city', 'state', 'zipCode', 'status', 'contacted', 'note')

