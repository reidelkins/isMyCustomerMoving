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
from .utils import getAllZipcodes, count_words_at_url
from .models import CustomUser, Client, Company, ZipCode
from .serializers import UserSerializer, UserSerializerWithToken, UploadFileSerializer, ClientListSerializer
from worker import conn
from rq import Queue
from rq.worker import HerokuWorker as Worker

q = Queue(connection=conn)

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
            company = Company.objects.get(name=company)
            print(company)
            user = CustomUser.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=make_password(password),
                company=company,
                # accessToken=accessToken
            )
            current_site = get_current_site(request)
            mail_subject = 'Activation link has been sent to your email id'
            tokenSerializer = UserSerializerWithToken(user, many=False)

            # Next version will add a HTML template
            message = "Confirm your email {}/api/v1/accounts/confirmation{}/{}/".format(current_site, tokenSerializer.data['refresh'], user.id)
            to_email = email
            send_mail(
                    mail_subject, message, "youremail@email.com", [to_email]
            )
            serializer = UserSerializerWithToken(user, many=False)
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
            print("hello")
            result = q.enqueue(count_words_at_url, 'http://heroku.com')
            print(result.result)
        except:
            pass
        print("there")
        return Response("", status=status.HTTP_201_CREATED, headers="")

class UploadFileView(generics.CreateAPIView):
    serializer_class = UploadFileSerializer
    
    def post(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)
        print(list(serializer.initial_data.dict().keys())[0])
        company_id = list(serializer.initial_data.dict().keys())[0]
        file = serializer.initial_data[company_id]
        try:
            company = Company.objects.get(id=company_id)
        except:
            return Response({"status": "Company Error"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            reader = pd.read_csv(file)
            reader.columns= reader.columns.str.lower()
        except:
            return Response({"status": "File Error"}, status=status.HTTP_400_BAD_REQUEST)
        for _, row in reader.iterrows():
            try:
                # if type(row['zip']) != int:
                #     row['zip'] = (row['zip'].split('-'))[0]
                #     print(row['zip'])
                if int(row['zip']) > 500 and int(row['zip']) < 99951:
                    zipCode, created = ZipCode.objects.get_or_create(zipCode=row["zip"])
                    Client.objects.update_or_create(
                            name= row["name"],
                            address= row['street'],
                            zipCode= zipCode,
                            company= company
                            )
            except:
                try:
                    if type(row['zip']) != int:
                        row['zip'] = (row['zip'].split('-'))[0]
                    if int(row['zip']) > 500 and int(row['zip']) < 99951:
                        zipCode, created = ZipCode.objects.get_or_create(zipCode=row["zip"])
                        Client.objects.update_or_create(
                                name= row["name"],
                                address= row['street'],
                                zipCode= zipCode,
                                company= company
                                )
                except Exception as e:
                    print(e)
        # getAllZipcodes(company_id)
        return Response({"status": "success"},
                        status.HTTP_201_CREATED)