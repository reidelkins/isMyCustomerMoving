import traceback
from .models import Company, Franchise, CustomUser
from .serializers import CompanySerializer

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.template.loader import get_template

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import requests
import jwt


def makeCompany(companyName, email, phone, stripeId=None):
    try:
        if stripeId:
            comp = {'name': companyName, 'phone': phone, 'email': email, 'stripeID': stripeId}
        else:
            comp = {'name': companyName, 'phone': phone, 'email': email}
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
                return company.id
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

def verify_token(token):
    try:
        decoded_token = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
    except jwt.exceptions.ExpiredSignatureError:
        raise AuthenticationFailed('Token has expired')
    except jwt.exceptions.InvalidTokenError:
        raise AuthenticationFailed('Invalid token')
    return decoded_token

class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Try to authenticate using JWT
        try:
            token = request.headers.get('Authorization', '').split(' ')[1]
            decoded_token = verify_token(token)
            user = CustomUser.objects.get(id=decoded_token['user_id'])
            return user, decoded_token
        except AuthenticationFailed:
            return None
        except Exception as e:
            print(f"Non Authentication Error: {e}")
            
        # Try to authenticate using Google OAuth
        access_token = request.headers.get("Authorization", None)
        if access_token is None:
            return None

        access_token = access_token.split(" ")[1]
        token_info = requests.get(f"https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={access_token}").json()
        if int(token_info["expires_in"]) <= 0:
            return None
        if token_info["aud"] != settings.GOOGLE_CLIENT_ID:
            return None
        user_info = requests.get(f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={access_token}").json()        
        if token_info["sub"] != user_info["sub"]:
            return None        
        # Authenticate the user using the retrieved information
        user_data = {"email": user_info["email"], "username": user_info["name"], "password": "randompassword"}
        try:        
            user = CustomUser.objects.get(email=user_data["email"])
        except ObjectDoesNotExist:
            return None
        
        return user, None



