from django.shortcuts import redirect
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.template.loader import get_template
from django.http import HttpResponse
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions, status, generics
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .utils import getAllZipcodes, saveClientList, makeCompany, find_franchise
from .models import CustomUser, Client, Company, InviteToken, Task, ClientUpdate, HomeListing, Referral
from .serializers import UserSerializer, UserSerializerWithToken, UserListSerializer, ClientListSerializer, MyTokenObtainPairSerializer, HomeListingSerializer, ReferralSerializer
from .syncClients import get_salesforce_clients, get_serviceTitan_clients
import datetime
import requests
import jwt
from config import settings
import pytz
import pyotp

class ManageUserView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Invite User
            if Company.objects.filter(id=self.kwargs['id']).exists():
                try:
                    company = Company.objects.get(id=self.kwargs['id'])
                    admin = CustomUser.objects.filter(company=company, status='admin')[0]
                    if company:
                        user, created = CustomUser.objects.get_or_create(
                            email=request.data['email'],
                            company=company,
                            status='pending',
                        )
                        token, created = InviteToken.objects.get_or_create(company=company, email=request.data['email'])
                        if created:
                            mail_subject = "Account Invite For Is My Customer Moving"                            
                        else:
                            token.expiration = datetime.datetime.utcnow() + datetime.timedelta(days=1)
                            token.save()
                            mail_subject = "Invite Reminder For Is My Customer Moving"

                        messagePlain = f"You have been invited to join Is My Customer Moving by {admin.first_name} {admin.last_name}. Please click the link below to join. https://app.ismycustomermoving.com/addeduser/{str(token.id)}"
                        message = get_template("addUserEmail.html").render({
                            'admin': admin, 'token': token.id
                        })
                        send_mail(subject=mail_subject, message=messagePlain, from_email=settings.EMAIL_HOST_USER, recipient_list=[request.data['email']], html_message=message, fail_silently=False)    
                except Exception as e:
                    print(e)
                    return Response({"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST)
                users = CustomUser.objects.filter(company=user.company)
                serializer = UserListSerializer(users, many=True)
                return Response(serializer.data)
            # Accept Invite and Make User
            elif InviteToken.objects.filter(id=self.kwargs['id']).exists():
                utc = pytz.UTC
                try:
                    token = InviteToken.objects.get(id=self.kwargs['id'], email=request.data['email'])
                    if token.expiration > utc.localize(datetime.datetime.utcnow()):
                        company = token.company
                        if company:
                            try:
                                user = CustomUser.objects.get(
                                    email=request.data['email'],
                                    company=company,
                                    status='pending'
                                )
                            except Exception as e:
                                print(e)
                                return Response({"status": "Cannot find user"}, status=status.HTTP_400_BAD_REQUEST)

                            user.password = make_password(request.data['password'])
                            user.status = 'active'
                            user.first_name = request.data['firstName']
                            user.last_name = request.data['lastName']
                            user.phone = request.data['phone']
                            user.isVerified = True
                            user.save()                            
                            token.delete()
                    else:
                        return Response({"status": "Token Expired"}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    print(e)
                    return Response({"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST)
                serializer = UserSerializerWithToken(user, many=False)
                return Response(serializer.data)
            # Make User an Admin
            elif CustomUser.objects.filter(id=self.kwargs['id']).exists():
                try:
                    user = CustomUser.objects.get(id=self.kwargs['id'])
                    if user:
                        user.status = 'admin'
                        user.save()
                except Exception as e:
                    print(e)
                    return Response({"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST)
                users = CustomUser.objects.filter(company=user.company)
                serializer = UserListSerializer(users, many=True)
                return Response(serializer.data)
        except Exception as e:
            print(e)
            return Response({"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request, *args, **kwargs):
        try:
            if CustomUser.objects.filter(id=self.kwargs['id']).exists():
                user = CustomUser.objects.get(id=self.kwargs['id'])
                if user:
                    user.first_name = request.data['firstName']
                    user.last_name = request.data['lastName']
                    user.email = request.data['email']
                    user.save()
                serializer = UserSerializerWithToken(user, many=False)
                return Response(serializer.data)
            else:
                return Response({"status": "User Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST)        
    def delete(self, request, *args, **kwargs):
        try:
            if len(request.data) == 1:
                user = CustomUser.objects.get(id=request.data[0])
                user.delete()
            else:
                CustomUser.objects.filter(id__in=request.data).delete()
            users = CustomUser.objects.filter(company=self.kwargs['id'])
            serializer = UserListSerializer(users, many=True)
            return Response(serializer.data)
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
            if request.data['forSaleTag'] != "":
                company.serviceTitanForSaleTagID = request.data['forSaleTag']
            if request.data['forRentTag'] != "":
                company.serviceTitanForRentTagID = request.data['forRentTag']
            if request.data['soldTag'] != "":
                company.serviceTitanRecentlySoldTagID = request.data['soldTag']
            if request.data['crm'] != "":
                company.crm = request.data['crm']
            company.save()
            user = CustomUser.objects.get(id=request.data['user'])
            serializer = UserSerializerWithToken(user, many=False)
            return Response( serializer.data , status=status.HTTP_201_CREATED, headers="")
        except Exception as e:
            print(e)
            return Response({"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST)   

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
        phone = data.get('phone')
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
                    status='admin',
                    isVerified=True,
                    phone = phone
                )
                # user = CustomUser.objects.get(email=email)
                # current_site = get_current_site(request)
                # tokenSerializer = UserSerializerWithToken(user, many=False)
                # mail_subject = "Activation Link for Is My Customer Moving"
                # messagePlain = "Verify your account for Is My Customer Moving by going here {}/api/v1/accounts/confirmation/{}/{}/".format(current_site, tokenSerializer.data['refresh'], user.id)
                # message = get_template("registration.html").render({
                #     'current_site': current_site, 'token': tokenSerializer.data['refresh'], 'user_id': user.id
                # })
                # send_mail(subject=mail_subject, message=messagePlain, from_email=settings.EMAIL_HOST_USER, recipient_list=[email], html_message=message, fail_silently=False)
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
        return redirect('http://www.ismycustomermoving.com/login')

    elif (datetime.datetime.fromtimestamp(token['exp']) < datetime.datetime.now()):

        # For resending confirmation email use send_mail with the following encryption
        # print(jwt.encode({'user_id': user.user.id, 'exp': datetime.datetime.now() + datetime.timedelta(days=1)}, settings.SECRET_KEY, algorithm='HS256'))
        
        return HttpResponse('Your activation link has been expired')
    else:
        return redirect('http://www.ismycustomermoving.com/login')
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserViewSet(ReadOnlyModelViewSet):
    throttle_classes = [UserRateThrottle]
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

class OTPGenerateView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]
    authentication_classes = []

    def post(self, request):
        try:
            user = CustomUser.objects.get(id=request.data['id'])
            if user == None:
                return Response({'detail': f'User with this email does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            otp_base32 = pyotp.random_base32()
            otp_auth_url = pyotp.totp.TOTP(otp_base32).provisioning_uri(
                name=user.email.lower(), issuer_name='Is My Customer Moving')

            user.otp_auth_url = otp_auth_url
            user.otp_base32 = otp_base32
            user.save()
            serializer = UserSerializerWithToken(user, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(e)
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

class OTPVerifyView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]
    authentication_classes = []

    def post(self, request):
        print(request.data['otp'])
        try:
            user = CustomUser.objects.get(id=request.data['id'])
            if user == None:
                return Response({'detail': f'User with this email does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            if user.otp_base32 == None:
                return Response({'detail': f'OTP not generated for this user'}, status=status.HTTP_400_BAD_REQUEST)
            totp = pyotp.TOTP(user.otp_base32)
            if totp.verify(request.data['otp']):
                user.otp_enabled = True
                user.otp_verified = True
                user.save()
                serializer = UserSerializerWithToken(user, many=False)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                print("verification failed")
                return Response({'detail': f'OTP verification failed'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print(e)
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)       

class OTPValidateView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]
    authentication_classes = []

    def post(self, request):
        otp = request.data['otp']
        messages = {'errors': []}
        user = CustomUser.objects.get(id=request.data['id'])
        if not user.otp_verified:
            messages['errors'].append('OTP not verified')
        if user.otp_base32 == None:
            return Response({'detail': f'OTP not generated for this user'}, status=status.HTTP_400_BAD_REQUEST)
        if len(messages['errors']) > 0:
            return Response({"detail": messages['errors']}, status=status.HTTP_400_BAD_REQUEST)
        try:                                    
            totp = pyotp.TOTP(user.otp_base32)
            if totp.verify(otp, valid_window=1):
                serializer = UserSerializerWithToken(user, many=False)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'detail': f'OTP verification failed'}, status=status.HTTP_400_BAD_REQUEST)            
        except Exception as e:
            print(e)
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

class OTPDisableView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]
    authentication_classes = []

    def post(self, request):
        try:            
            user = CustomUser.objects.get(id=request.data['id'])            
            user.otp_enabled = False
            user.otp_verified = False
            user.otp_base32 = None
            user.otp_auth_url = None
            user.save()
            serializer = UserSerializerWithToken(user, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(e)
            return Response({'detail': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

class AllClientListView(generics.ListAPIView):
    serializer_class = ClientListSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = CustomUser.objects.get(id=self.request.user.id)
        return Client.objects.filter(company=user.company).order_by('status')
        
class CustomPagination(PageNumberPagination):
    page_size = 1000

class ClientListView(generics.ListAPIView):
    serializer_class = ClientListSerializer
    pagination_class = CustomPagination
    
    def get_queryset(self):
        user = CustomUser.objects.get(id=self.kwargs['user'])
        if user.status == 'admin':
            return Client.objects.prefetch_related('clientUpdates').filter(company=user.company).order_by('status')
        else:
            return Client.objects.prefetch_related('clientUpdates').filter(company=user.company).exclude(status='No Change').order_by('status')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        user = CustomUser.objects.get(id=self.kwargs['user'])

        forSale = Client.objects.filter(company=user.company, status="House For Sale", contacted=False).count()
        recentlySold = Client.objects.filter(company=user.company, status="House Recently Sold (6)", contacted=False).count()
        forSaleAllTime = ClientUpdate.objects.filter(client__company=user.company, status="House For Sale").count()
        recentlySoldAllTime = ClientUpdate.objects.filter(client__company=user.company, status="House Recently Sold (6)").count()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            clients = serializer.data
            return self.get_paginated_response({"forSale": forSale, "forSaleAllTime": forSaleAllTime, "recentlySoldAllTime": recentlySoldAllTime, "recentlySold": recentlySold, "clients": clients})

        serializer = self.get_serializer(queryset, many=True)
        return Response({"forSale": forSale, "forSaleAllTime": forSaleAllTime, "recentlySoldAllTime": recentlySoldAllTime, "recentlySold": recentlySold, "clients": clients})

class RecentlySoldView(generics.ListAPIView):
    serializer_class = HomeListingSerializer
    pagination_class = CustomPagination
    def get_queryset(self):
        company = Company.objects.get(id=self.kwargs['company'])
        if company.recentlySoldPurchased:
            zipCode_objects = Client.objects.filter(company=company).values('zipCode')            
            return HomeListing.objects.filter(zipCode__in=zipCode_objects, listed__gt=(datetime.datetime.today()-datetime.timedelta(days=30)).strftime('%Y-%m-%d')).order_by('listed')
        else:
            return HomeListing.objects.none()

class AllRecentlySoldView(generics.ListAPIView):
    serializer_class = HomeListingSerializer
    def get_queryset(self):
        company = Company.objects.get(id=self.kwargs['company'])
        if company.recentlySoldPurchased:
            zipCode_objects = Client.objects.filter(company=company).values('zipCode')            
            return HomeListing.objects.filter(zipCode__in=zipCode_objects, listed__gt=(datetime.datetime.today()-datetime.timedelta(days=30)).strftime('%Y-%m-%d')).order_by('listed')
        else:
            return HomeListing.objects.none()

class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    def get_queryset(self):
        return CustomUser.objects.filter(company=self.kwargs['company'])

class UpdateStatusView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            getAllZipcodes.delay(self.kwargs['company'])
        except Exception as e:
            print(f"ERROR: Update Status View: {e}")
        return Response("", status=status.HTTP_201_CREATED, headers="")

class ClientListAndUpdatesView(generics.ListAPIView):
    serializer_class = ClientListSerializer
    pagination_class = CustomPagination
    def get_queryset(self):
        company = Company.objects.get(id=self.kwargs['company'])
        print(Client.objects.filter(company=company).count())
        return Client.objects.prefetch_related('clientUpdates').filter(company=company).order_by('status')

class UploadFileView(generics.ListAPIView):
    def put(self, request, *args, **kwargs):
        company_id = self.kwargs['company']
        try:
            company = Company.objects.get(id=company_id)
        except Exception as e:
            print(e)
            return Response({"status": "Company Error"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            saveClientList.delay(request.data, company_id)
        except Exception as e:
            print(e)
            return Response({"status": "File Error"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "File Uploaded"}, status=status.HTTP_201_CREATED, headers="")

@api_view(['PUT', 'DELETE'])
def update_client(request):
    try:
        if request.method == 'PUT':
            try:
                client = Client.objects.get(id=request.data['clients'])
                if request.data['note']:
                    client.note = request.data['note']
                    ClientUpdate.objects.create(client=client, note=request.data['note'])
                if request.data['contacted'] != "":
                    client.contacted = request.data['contacted']
                    ClientUpdate.objects.create(client=client, contacted=request.data['contacted'])
                client.save()
            except Exception as e:
                print(e)
                return Response({"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            try:
                if len(request.data['clients']) == 1:
                    client = Client.objects.get(id=request.data['clients'][0])
                    client.delete()
                else:
                    Client.objects.filter(id__in=request.data['clients']).delete()
            except Exception as e:
                print(e)
                return Response({"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Success"}, status=status.HTTP_201_CREATED, headers="")
    except Exception as e:
        print(e)
        return Response({"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST)

# class view to return all referrals for a company where the company is either the referred from or referred to
class ReferralView(generics.ListAPIView):
    print("REFERRAL VIEW")
    serializer_class = ReferralSerializer
    pagination_class = CustomPagination
    def get_queryset(self):
        company = Company.objects.get(id=self.kwargs['company'])
        print(company)
        return Referral.objects.filter(Q(referredFrom=company) | Q(referredTo=company)).order_by('franchise')

    # method for creating a new referral
    def post(self, request, *args, **kwargs):
        
        try:
            referredFrom = Company.objects.get(id=self.kwargs['company'])
            # find closest franchise to area provided
            referredToId = find_franchise(request.data['area'], referredFrom.franchise.id, referredFrom.id)
            referredTo = Company.objects.get(id=referredToId)
            client = Client.objects.get(id=request.data['id'])
            referral = Referral.objects.create(franchise=referredFrom.franchise, referredTo=referredTo, referredFrom=referredFrom, client=client)
            return Response({"status": "SUCCESS", "referral": ReferralSerializer(referral).data}, status=status.HTTP_201_CREATED, headers="")
        except Exception as e:
            print(e)
            return Response({"status": "ERROR"}, status=status.HTTP_400_BAD_REQUEST)

    # method for updating a referral
    def put(self, request, *args, **kwargs):
        try:
            referral = Referral.objects.get(id=request.data['referral'])
            if request.data['status']:
                referral.status = request.data['status']
            if request.data['note']:
                referral.note = request.data['note']
            referral.save()
            return Response({"status": "SUCCESS", "referral": ReferralSerializer(referral).data}, status=status.HTTP_201_CREATED, headers="")
        except Exception as e:
            print(e)
            return Response({"status": "ERROR"}, status=status.HTTP_400_BAD_REQUEST)

class ServiceTitanView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            try:
                task = Task.objects.get(id=self.kwargs['company'])
                if task.completed:
                    deleted = task.deletedClients
                    task.delete()
                    return Response({"status": "SUCCESS", "deleted": deleted}, status=status.HTTP_201_CREATED, headers="")
                else:
                    # clients = Company.objects.get(id="faee8ca7-e5de-4c60-8578-0ac6bc576930").client_set.all()
                    # if clients.count() > 0:
                    #     return Response({"status": "UNFINISHED", "clients": ClientListSerializer(clients[:1000], many=True).data}, status=status.HTTP_201_CREATED)
                    return Response({"status": "UNFINISHED", "clients": []}, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(e)
                return Response({"status": "Task Error"}, status=status.HTTP_400_BAD_REQUEST)          
        except Exception as e:
            print(e)
            return Response({"status": "error"}, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request, *args, **kwargs):
        try:
            company_id = self.kwargs['company']
            try:
                Company.objects.get(id=company_id)
                task = Task.objects.create() 
                get_serviceTitan_clients.delay(company_id, task.id)                          
                return Response({"status": "Success", "task": task.id}, status=status.HTTP_201_CREATED, headers="")
            except Exception as e:
                print(e)
                return Response({"status": "Company Error"}, status=status.HTTP_400_BAD_REQUEST)            
        except Exception as e:
            print(e)
            return Response({"status": "error"}, status=status.HTTP_400_BAD_REQUEST)

class SalesforceConsumerView(APIView):
    # GET request that returns the Salesforce Consumer Key and Consumer Secret from the config file, make this protected
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            return Response({"consumer_key": settings.SALESFORCE_CONSUMER_KEY, "consumer_secret": settings.SALESFORCE_CONSUMER_SECRET}, status=status.HTTP_201_CREATED, headers="")
        except Exception as e:
            print(e)
            return Response({"status": "error"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        try:
            company_id = self.kwargs['company']
            try:
                company = Company.objects.get(id=company_id)
                company.crm = "Salesforce"
                code = request.data['code']
                headers = {
                    'Content-type': 'application/x-www-form-urlencoded',
                }

                # Make the request
                response = requests.post(f'https://login.salesforce.com/services/oauth2/token?grant_type=authorization_code&client_id={settings.SALESFORCE_CONSUMER_KEY}&client_secret={settings.SALESFORCE_CONSUMER_SECRET}&redirect_uri=http://localhost:3000/dashboard/settings&code={code}', headers=headers)

                # Parse the response
                response_data = response.json()
                new_access_token = response_data['access_token']
                new_refresh_token = response_data['refresh_token']
                company.sfAccessToken = new_access_token
                company.sfRefreshToken = new_refresh_token
                company.save()
                user = CustomUser.objects.get(id=request.data['id'])
                serializer = UserSerializerWithToken(user, many=False)
                return Response(serializer.data)
            except Exception as e:
                print(e)
                return Response({"status": "Company Error"}, status=status.HTTP_400_BAD_REQUEST)            
        except Exception as e:
            print(e)
            return Response({"status": "error"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        try:
            company_id = self.kwargs['company']
            
            try:
                get_salesforce_clients(company_id)
                return Response({"status": "Success"}, status=status.HTTP_201_CREATED, headers="")
            except Exception as e:
                print(e)
                return Response({"status": "Company Error"}, status=status.HTTP_400_BAD_REQUEST)            
        except Exception as e:
            print(e)
            return Response({"status": "error"}, status=status.HTTP_400_BAD_REQUEST)