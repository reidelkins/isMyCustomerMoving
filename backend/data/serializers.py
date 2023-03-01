from rest_framework import serializers

from .models import Client, ClientUpdate, HomeListing

class ClientUpdateSerializer(serializers.ModelSerializer):
    status = serializers.CharField(max_length=100)
    date = serializers.DateField()
    listed = serializers.CharField(max_length=100)
    note = serializers.CharField(max_length=100)
    contacted = serializers.BooleanField()

    class Meta:
        model = ClientUpdate
        fields = ('id', 'status', 'date', 'listed', 'note', 'contacted')
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
    clientUpdates = ClientUpdateSerializer(many=True, read_only=True)


    def get_zipCode(self, obj):
        return obj.zipCode.zipCode

    class Meta:
        model = Client
        fields = ('id', 'name', 'address', 'city', 'state', 'zipCode', 'status', 'contacted', 'note', 'phoneNumber', 'clientUpdates')
        read_only_fields = fields

class HomeListingSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    address = serializers.CharField(max_length=100)
    zipCode = serializers.SerializerMethodField(read_only=True)
    listed = serializers.CharField(max_length=30)

    def get_zipCode(self, obj):
        return obj.zipCode.zipCode
    
    class Meta:
        model = HomeListing
        fields = ('id', 'address', 'listed', 'zipCode')

