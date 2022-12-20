from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import get_template
from django.http import HttpResponse
from rest_framework import permissions, status, generics
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
import pandas as pd
from .utils import getAllZipcodes, saveClientList, makeCompany, get_serviceTitan_clients
from .models import CustomUser, Client, Company, InviteToken
from .serializers import UserSerializer, UserSerializerWithToken, UploadFileSerializer, ClientListSerializer, MyTokenObtainPairSerializer, CompanySerializer
import datetime
import jwt
from config import settings
import pytz

class ManageUserView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            if Company.objects.filter(id=self.kwargs['id']).exists():
                try:
                    company = Company.objects.get(id=self.kwargs['id'])
                    admin = CustomUser.objects.filter(company=company, status='admin')[0]
                    if company:
                        token = InviteToken.objects.create(company=company, email=request.data['email'])
                        mail_subject = "Account Invite For Is My Customer Moving"
                        messagePlain = f"You have been invited to join Is My Customer Moving by {admin.first_name} {admin.last_name}. Please click the link below to join. https://app.ismycustomermoving.com/addeduser/{str(token.id)}"
                    #     # # Next version will add a HTML template
                        message = get_template("addUserEmail.html").render({
                            'admin': admin, 'token': token.id
                        })
                        send_mail(subject=mail_subject, message=messagePlain, from_email=settings.EMAIL_HOST_USER, recipient_list=[request.data['email']], html_message=message, fail_silently=False)
                except Exception as e:
                    print(e)
                    return Response({"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST)
                return Response("", status=status.HTTP_201_CREATED, headers="")
            elif InviteToken.objects.filter(id=self.kwargs['id']).exists():
                utc = pytz.UTC
                try:
                    token = InviteToken.objects.get(id=self.kwargs['id'], email=request.data['email'])
                    if token.expiration > utc.localize(datetime.datetime.utcnow()):
                        company = token.company
                        if company:
                            user = CustomUser.objects.create(
                                email=request.data['email'],
                                password=make_password(request.data['password']),
                                company=company,
                                status='active',
                                first_name=request.data['firstName'],
                                last_name=request.data['lastName'],
                                isVerified=True
                            )
                            user.save()
                            token.delete()
                    else:
                        return Response({"status": "Token Expired"}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    print(e)
                    return Response({"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST)
                serializer_class = MyTokenObtainPairSerializer
        except Exception as e:
            print(e)
            return Response({"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'PUT'])
def company(request):
    if request.method == 'POST':
        try:
            company = request.data['name']
            email = request.data['email']
            comp = makeCompany(company, email)
            if comp == "":
                return Response("", status=status.HTTP_201_CREATED, headers="")
            else:
                return Response(comp, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PUT':
        try:
            company = Company.objects.get(id=request.data['company'])
            if request.data['email'] != "":
                company.email = request.data['email']
            if request.data['phone'] != "":
                company.phone = request.data['phone']
            if request.data['tenantID'] != "":
                company.tenantID = request.data['tenantID']
            if request.data['clientID'] != "":
                company.clientID = request.data['clientID']
                company.clientSecret = request.data['clientSecret']
            company.save()
            user = CustomUser.objects.get(id=request.data['user'])
            serializer = UserSerializerWithToken(user, many=False)
            return Response( serializer.data , status=status.HTTP_201_CREATED, headers="")
        except Exception as e:
            print(e)
            return Response({"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST)   

class AddUserView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        company = self.kwargs['company']
        data = request.data
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
            serializer = UserSerializerWithToken(user, many=False)
        except Exception as e:
            print(e)
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

class VerifyRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        try:
            token = request.data['token']
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user = CustomUser.objects.get(id=payload['user_id'])
                if not user.isVerified:
                    user.isVerified = True
                    user.save()
            except jwt.ExpiredSignatureError as identifier:
                return Response({'detail': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
            except jwt.exceptions.DecodeError as identifier:
                return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Successfully activated'}, status=status.HTTP_200_OK)

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
            noAdmin = CustomUser.objects.filter(company=company, isVerified=True)
            if len(noAdmin) == 0:
                user = CustomUser.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=make_password(password),
                    company=company,
                    status='admin'
                )
                user = CustomUser.objects.get(email=email)
                current_site = get_current_site(request)
                tokenSerializer = UserSerializerWithToken(user, many=False)
                mail_subject = "Activation Link for Is My Customer Moving"
                messagePlain = "Verify your account for Is My Customer Moving by going here {}/api/v1/accounts/confirmation/{}/{}/".format(current_site, tokenSerializer.data['refresh'], user.id)
                message = get_template("registration.html").render({
                    'current_site': current_site, 'token': tokenSerializer.data['refresh'], 'user_id': user.id
                })
                send_mail(subject=mail_subject, message=messagePlain, from_email=settings.EMAIL_HOST_USER, recipient_list=[email], html_message=message, fail_silently=False)
                serializer = UserSerializerWithToken(user, many=False)
            else:
                return Response({'detail': f'Access Token Already Used. Ask an admin to login and create profile for you.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

@api_view(['GET'])
def confirmation(request, pk, uid):
    user = CustomUser.objects.get(id=uid)
    token = jwt.decode(pk, settings.SECRET_KEY, algorithms=["HS256"])

    if user.isVerified == False and datetime.datetime.fromtimestamp(token['exp']) > datetime.datetime.now():
        user.isVerified = True
        user.save()
        return redirect('http://localhost:3006/login')

    elif (datetime.datetime.fromtimestamp(token['exp']) < datetime.datetime.now()):

        # For resending confirmation email use send_mail with the following encryption
        # print(jwt.encode({'user_id': user.user.id, 'exp': datetime.datetime.now() + datetime.timedelta(days=1)}, settings.SECRET_KEY, algorithm='HS256'))
        
        return HttpResponse('Your activation link has been expired')
    else:
        return redirect('http://localhost:3000/login')
    
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
            print(f"ERROR: Update Status View: {e}")
        return Response("", status=status.HTTP_201_CREATED, headers="")

class UploadFileView(generics.CreateAPIView):
    serializer_class = UploadFileSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        company_id = list(serializer.initial_data.dict().keys())[0]
        file = serializer.initial_data[company_id]
        try:
            Company.objects.get(id=company_id)
        except Exception as e:
            print(e)
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
                elif "address" in column:
                    reader.columns = reader.columns.str.replace(column, 'street')
                if "city" in column:
                    reader.columns = reader.columns.str.replace(column, 'city')
                if "state" in column:
                    reader.columns = reader.columns.str.replace(column, 'state')
        except Exception as e:
            print(e)
            return Response({"status": "File Error"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            saveClientList.delay(reader.to_json(), company_id)
        except Exception as e:
            print(e)
            return Response({"status": "File Error"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "success"},
                        status.HTTP_201_CREATED)

@api_view(['PUT'])
def update_client(request, pk):
    print("here")
    
    try:
        print(len(request.data['clients']))
        print(request)
        company = Company.objects.get(id=pk)
        if request.method == 'PUT':
            try:
                if len(request.data['clients']) > 1:
                    clients = Client.objects.filter(id__in=request.data['clients']).delete()
                else:
                    client = Client.objects.get(id=request.data['clients'])
                    if request.data['note']:
                        client.note = request.data['note']
                    if request.data['contacted']:
                        print("contacted")
                        client.contacted = request.data['contacted']
                    client.save()
            except Exception as e:
                print(e)
                return Response({"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST)
        clients = Client.objects.filter(company=company)
        clients = ClientListSerializer(clients, many=True).data
        return Response(clients , status=status.HTTP_201_CREATED, headers="")
    except Exception as e:
        print(e)
        return Response({"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST)

class ServiceTitanView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            get_serviceTitan_clients.delay(self.kwargs['company'])
            return Response({"status": "success"}, status=status.HTTP_201_CREATED, headers="")
        except Exception as e:
            print(e)
            return Response({"status": "error"}, status=status.HTTP_400_BAD_REQUEST)
