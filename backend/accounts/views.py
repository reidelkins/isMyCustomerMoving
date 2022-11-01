from django.shortcuts import render
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from rest_framework import permissions, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
import io, csv, pandas as pd
from .utils import getAllZipcodes, saveClientList, send_password_reset_email
from .models import CustomUser, Client, Company, ZipCode
from .serializers import UserSerializer, UserSerializerWithToken, UploadFileSerializer, ClientListSerializer

class AddUserView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        company = self.kwargs['company']
        data = request.data
        print(data)
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        email = data.get('email')
        messages = {'errors': []}

        if first_name == None:
            messages['errors'].append('first_name can\'t be empty')
        if last_name == None:
            messages['errors'].append('last_name can\'t be empty')
        if email == None:
            messages['errors'].append('Email can\'t be empty')
        if company == None:
            messages['errors'].append('Company can\'t be empty')

        if CustomUser.objects.filter(email=email).exists():
            messages['errors'].append(
                "Account already exists with this email id.")
        if len(messages['errors']) > 0:
            print(messages['errors'])
            return Response({"detail": messages['errors']}, status=status.HTTP_400_BAD_REQUEST)
        try:
            company = Company.objects.get(id=company)
            user = CustomUser.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                company=company,
                status='active'
            )
            print("how you doing")
            serializer = UserSerializerWithToken(user, many=False)
        except Exception as e:
            print(e)
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]
    authentication_classes = []

    def post(self, request):
        data = request.data
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        email = data.get('email')
        password = data.get('password')
        company = data.get('company')
        accessToken = data.get('accessToken')
        messages = {'errors': []}
        if first_name == None:
            messages['errors'].append('first_name can\'t be empty')
        if last_name == None:
            messages['errors'].append('last_name can\'t be empty')
        if email == None:
            messages['errors'].append('Email can\'t be empty')
        if password == None:
            messages['errors'].append('Password can\'t be empty')
        if company == None:
            messages['errors'].append('Company can\'t be empty')
        if accessToken == None:
            messages['errors'].append('Access Token can\'t be empty')

        if CustomUser.objects.filter(email=email).exists():
            messages['errors'].append(
                "Account already exists with this email id.")
        if len(messages['errors']) > 0:
            return Response({"detail": messages['errors']}, status=status.HTTP_400_BAD_REQUEST)
        try:
            company = Company.objects.get(name=company, accessToken=accessToken)
            noAdmin = CustomUser.objects.filter(company=company)
            if len(noAdmin) == 0:
                user = CustomUser.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=make_password(password),
                    company=company,
                    status='admin',
                    accessToken=accessToken
                )
                # current_site = get_current_site(request)
                # mail_subject = 'Activation link has been sent to your email id'
                # tokenSerializer = UserSerializerWithToken(user, many=False)

                # Next version will add a HTML template
                # message = "Confirm your email {}/api/v1/accounts/confirmation{}/{}/".format(current_site, tokenSerializer.data['refresh'], user.id)
                # to_email = email
                # send_mail(
                #         mail_subject, message, "youremail@email.com", [to_email]
                # )
                serializer = UserSerializerWithToken(user, many=False)
            else:
                return Response({'detail': f'Access Token Already Used. Ask an admin to login and create profile for you.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

from django.http import HttpResponse
import datetime
import jwt
from config import settings

@api_view(['GET'])
def confirmation(request, pk, uid):
    user = CustomUser.objects.get(id=uid)
    token = jwt.decode(pk, settings.SECRET_KEY, algorithms=["HS256"])

    if user.isVerified == False and datetime.datetime.fromtimestamp(token['exp']) > datetime.datetime.now():
        user.isVerified = True
        user.save()
        return HttpResponse('Your account has been activated')

    elif (datetime.datetime.fromtimestamp(token['exp']) < datetime.datetime.now()):

        # For resending confirmation email use send_mail with the following encryption
        # print(jwt.encode({'user_id': user.user.id, 'exp': datetime.datetime.now() + datetime.timedelta(days=1)}, settings.SECRET_KEY, algorithm='HS256'))
        
        return HttpResponse('Your activation link has been expired')
    else:
        return HttpResponse('Your account has already been activated')
    
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        serializer = UserSerializerWithToken(self.user).data
        for k, v in serializer.items():
            data[k] = v

        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class UserViewSet(ReadOnlyModelViewSet):
    throttle_classes = [UserRateThrottle]
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

class ClientListView(generics.ListAPIView):
    serializer_class = ClientListSerializer
    def get_queryset(self):
        return Client.objects.filter(company=self.kwargs['company'])

class UpdateStatusView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            getAllZipcodes.delay(self.kwargs['company'])
        except Exception as e:
            print("Update Status View")
            print(e)
        return Response("", status=status.HTTP_201_CREATED, headers="")

class UploadFileView(generics.CreateAPIView):
    serializer_class = UploadFileSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        company_id = list(serializer.initial_data.dict().keys())[0]
        file = serializer.initial_data[company_id]
        try:
            Company.objects.get(id=company_id)
        except:
            return Response({"status": "Company Error"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            reader = pd.read_csv(file, on_bad_lines='skip')
            reader.columns= reader.columns.str.lower()
            for column in reader.columns:
                if "name" in column:
                    reader.columns = reader.columns.str.replace(column, 'name')
                if "zip" in column:
                    reader.columns = reader.columns.str.replace(column, 'zip')
                if "street" in column:
                    reader.columns = reader.columns.str.replace(column, 'street')
                if "city" in column:
                    reader.columns = reader.columns.str.replace(column, 'city')
                if "state" in column:
                    reader.columns = reader.columns.str.replace(column, 'state')
        except Exception as e:
            print(e)
            return Response({"status": "File Error"}, status=status.HTTP_400_BAD_REQUEST)
        for _, row in reader.iterrows():
            saveClientList.delay(row.to_dict(), company_id)
        return Response({"status": "success"},
                        status.HTTP_201_CREATED)

class UpdateNoteView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        print(request.data)
        try:
            company_object = Company.objects.get(id = self.kwargs['company'])
            zipcode_object = ZipCode.objects.get(zipCode = int(request.data['zipCode']))
            customer = Client.objects.get(company=company_object, zipCode=zipcode_object, address=request.data['address'])
            customer.note = request.data['note']
            customer.save()
        except Exception as e:
            print(e)
            return Response({"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST)
        return Response("", status=status.HTTP_201_CREATED, headers="")

class UpdateContactedView(generics.CreateAPIView):
    serializer_class = UserSerializer
    def post(self, request, *args, **kwargs):
        print(request.data)
        try:
            company_object = Company.objects.get(id = self.kwargs['company'])
            zipcode_object = ZipCode.objects.get(zipCode = int(request.data['zipCode']))
            customer = Client.objects.get(company=company_object, zipCode=zipcode_object, address=request.data['address'])
            if customer.contacted:
                customer.contacted = False
            else:
                customer.contacted = True
            customer.save()
        except Exception as e:
            print(e)
            return Response({"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST)
        return Response("", status=status.HTTP_201_CREATED, headers="")

# class ResetView()

class ResetRequestView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        try:
            company_object = Company.objects.get(id = self.kwargs['company'])
            user = CustomUser.objects.get(company=company_object, email=self.kwargs['email'])
            send_password_reset_email(self.kwargs['email'])
        except Exception as e:
            print(e)
            return Response({"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST)

        return Response("", status=status.HTTP_201_CREATED, headers="")
    