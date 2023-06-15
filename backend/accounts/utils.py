import traceback
from .models import Company, Enterprise, CustomUser
from .serializers import CompanySerializer

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.template.loader import get_template

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import requests
import jwt
import logging


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
            logging.error(serializer.errors)
            return {'Error': 'Serializer not valid'}
    except Exception as e:
        logging.error(e)
        return {'Error': f'{e}'}
            
# find franchise that is the closest to the area provided for the referral
def find_enterprise(area, enterprise, referredFrom):
    try:
        enterprise = Enterprise.objects.get(id=enterprise)
        
        if area:
            companies = list(Company.objects.filter(enterprise=enterprise).exclude(id=referredFrom).values_list('id', flat=True))
            return companies[0]
        else:
            return None
    except Exception as e:
        logging.error("finding franchise failed")
        logging.error(f"ERROR: {e}")
        logging.error(traceback.format_exc())

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
            logging.error(f"Non Authentication Error: {e}")
            
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

def create_keap_company(company_id):
    try:
        company = Company.objects.get(id=company_id)
        url = 'https://api.infusionsoft.com/crm/rest/v1/companies'
        headers = {
            'X-Keap-API-Key': settings.KEAP_API_KEY,
            'Content-Type': 'application/json'
        }
        body = {
            'company_name': company.name,
            'email_address': company.email,
            'phone_number': {
                'number': company.phone,
            },
            'notes': float(company.product.amount)
        }
        response = requests.post(url, headers=headers, json=body)
        if response.status_code != 201:
            logging.error(f"ERROR: {response.text}")
            logging.error("Could not create company in Keap")

    except Exception as e:
        logging.error(f"ERROR: {e}")
        logging.error("Could not create company in Keap")


def create_keap_user(user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        company = user.company
        url = 'https://api.infusionsoft.com/crm/rest/v1/companies'
        headers = {
            'X-Keap-API-Key': settings.KEAP_API_KEY
        }        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logging.error(f"ERROR: {response.text}")
            logging.error("Could not get companies in Keap")
        else:
            company_id = ""
            companies = response.json()
            for comp in companies['companies']:
                if comp['company_name'] == company.name:
                    company_id = comp['id']
                    break
            url = 'https://api.infusionsoft.com/crm/rest/v1/contacts'
            headers = {
                'X-Keap-API-Key': settings.KEAP_API_KEY,
                'Content-Type': 'application/json'
            }
            body = {
                'given_name': user.first_name,
                'family_name': user.last_name,
                'email_addresses': [
                    {
                        'email': user.email,
                        'field': 'EMAIL1'
                    }
                ],
                'phone_numbers': [
                    {
                        'number': user.phone,
                        'field': 'PHONE1'
                    }
                ],
                'company': {
                    'id': company_id
                }
            }
            response = requests.post(url, headers=headers, json=body)
            if response.status_code != 201:
                logging.error(f"ERROR: {response.text}")
                logging.error("Could not create user in Keap")

            if float(company.product.amount) == 0:
                url = "https://api.infusionsoft.com/crm/rest/v1/tags/127/contacts"
                body = {
                    'ids': [
                        response.json()['id']
                    ]
                }
                response = requests.post(url, headers=headers, json=body)
                if response.status_code != 200:
                    logging.error(f"ERROR: {response.text}")
                    logging.error("Could not add user to tag in Keap")


            if float(company.product.amount) == 0:
                url = "https://api.infusionsoft.com/crm/rest/v1/tags/127/contacts"
                body = {
                    'ids': [
                        response.json()['id']
                    ]
                }
                response = requests.post(url, headers=headers, json=body)
                if response.status_code != 200:
                    print(f"ERROR: {response.text}")
                    print("Could not add user to tag in Keap")


    except Exception as e:
        logging.error(f"ERROR: {e}")
        logging.error("Could not create company in Keap")

