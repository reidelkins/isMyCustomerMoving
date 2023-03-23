import traceback
import requests
from typing import Dict, Any
from datetime import datetime, timedelta
from .models import Company, Franchise, CustomUser
from .serializers import CompanySerializer, UserSerializerWithToken

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.template.loader import get_template
from django.http import HttpResponse


GOOGLE_ID_TOKEN_INFO_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'

def makeCompany(companyName, email, phone, stripeId):
    try:
        comp = {'name': companyName, 'phone': phone, 'email': email, 'stripeID': stripeId}
        serializer = CompanySerializer(data=comp)
        if serializer.is_valid():
            company = serializer.save()
            if company:
                mail_subject = "Access Token for Is My Customer Moving"
                messagePlain = "Your access token is: " + company.accessToken
                messagePlain = "Thank you for signing up for Is My Customer Moving. Your company name is: " + company.name +  "and your access token is: " + company.accessToken + ". Please use this info at https://app.ismycustomermoving.com/register to create your account."
                message = get_template("registration.html").render({
                    'company': company.name, 'accessToken': company.accessToken
                })
                send_mail(subject=mail_subject, message=messagePlain, from_email=settings.EMAIL_HOST_USER, recipient_list=[email], html_message=message, fail_silently=False)
                return company
            else:
                return {'Error': "Company with that name already exists"}
        else:
            print(serializer.errors)
            return {'Error': 'Serializer not valid'}
    except Exception as e:
        print(e)
        return {'Error': f'{e}'}
            
# find franchise that is the closest to the area provided for the referral
def find_franchise(area, franchise, referredFrom):
    try:
        franchise = Franchise.objects.get(id=franchise)
        
        if area:
            companies = list(Company.objects.filter(franchise=franchise).exclude(id=referredFrom).values_list('id', flat=True))
            return companies[0]
        else:
            return None
    except Exception as e:
        print("finding franchise failed")
        print(f"ERROR: {e}")
        print(traceback.format_exc())

def get_first_matching_attr(obj, *attrs, default=None):
    for attr in attrs:
        if hasattr(obj, attr):
            return getattr(obj, attr)

    return default

def get_error_message(exc) -> str:
    if hasattr(exc, 'message_dict'):
        return exc.message_dict
    error_msg = get_first_matching_attr(exc, 'message', 'messages')

    if isinstance(error_msg, list):
        error_msg = ', '.join(error_msg)

    if error_msg is None:
        error_msg = str(exc)

    return error_msg

def jwt_payload_handler_func(user):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow()
    }
    return payload

def jwt_login(*, response: HttpResponse, user: CustomUser) -> HttpResponse:
    serializer = UserSerializerWithToken(user, many=False)
    token = serializer.data['access']
    
    # set JWT cookie
    if settings.IS_HEROKU:
        print("jk I am right here")
        print(response.__dict__)
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'], 
            value=str(token), 
            max_age=3600, secure=True, httponly=True, samesite='None', domain="app.ismycustomermoving.com"  # Set the secure flag to true
        )
        print(response.__dict__)
        print(response.cookies.__dict__)
        print("...and no issues")
    else:    
        response.set_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'], str(token), max_age=3600, httponly=False)

    return response

def google_get_access_token(*, code: str, redirect_uri: str) -> str:
    # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#obtainingaccesstokens
    data = {
        'code': code,
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }

    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)

    if not response.ok:
        raise ValidationError('Failed to obtain access token from Google.')

    access_token = response.json()['access_token']

    return access_token


def google_get_user_info(*, access_token: str) -> Dict[str, Any]:
    # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#callinganapi
    response = requests.get(
        GOOGLE_USER_INFO_URL,
        params={'access_token': access_token}
    )

    if not response.ok:
        raise ValidationError('Failed to obtain user info from Google.')

    return response.json()
