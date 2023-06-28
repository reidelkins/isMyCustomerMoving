import traceback
import requests
import jwt
import logging
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.template.loader import get_template
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Company, Enterprise, CustomUser
from .serializers import CompanySerializer


def make_company(company_name, email, phone, stripe_id=None):
    """
    Creates a new company and sends an email with the access token.
    """
    try:
        comp_data = {
            "name": company_name,
            "phone": phone,
            "email": email,
            "service_titan_app_version": 2,
        }

        if stripe_id:
            comp_data["stripe_id"] = stripe_id

        serializer = CompanySerializer(data=comp_data)

        if serializer.is_valid():
            company = serializer.save()

            if company:
                mail_subject = "Access Token for Is My Customer Moving"
                message_plain = (
                    f"Thank you for signing up for Is My Customer Moving. "
                    f"Your company name is: {company.name} and your "
                    f"access token is: {company.access_token}. Please "
                    f"use this info at https://app.ismycustomermoving.com/register "
                    f"to create your account."
                )

                message = get_template("registration.html").render(
                    {
                        "company": company.name,
                        "access_token": company.access_token,
                    }
                )

                send_mail(
                    subject=mail_subject,
                    message=message_plain,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    html_message=message,
                    fail_silently=False,
                )
                return company.id
            return {"Error": "Company with that name already exists"}
        else:
            logging.error(f"Serializer error: {serializer.errors}")
            return {"Error": "Serializer not valid"}
    except Exception as e:
        logging.error(f"Error in make_company: {e}")
        return {"Error": str(e)}


def find_enterprise(area, enterprise, referred_from):
    """
    Find the franchise that is closest to the area provided for the referral.
    """
    try:
        enterprise = Enterprise.objects.get(id=enterprise)

        if area:
            companies = list(
                Company.objects.filter(enterprise=enterprise)
                .exclude(id=referred_from)
                .values_list("id", flat=True)
            )
            return companies[0]
        return None
    except Exception as e:
        logging.error(f"Error finding franchise: {e}")
        logging.error(traceback.format_exc())


def verify_token(token):
    """
    Verifies the given token.
    """
    try:
        return jwt.decode(
            token,
            settings.SIMPLE_JWT["SIGNING_KEY"],
            algorithms=[settings.SIMPLE_JWT["ALGORITHM"]],
        )
    except jwt.exceptions.ExpiredSignatureError:
        raise AuthenticationFailed("Token has expired")
    except jwt.exceptions.InvalidTokenError:
        raise AuthenticationFailed("Invalid token")


class CustomAuthentication(BaseAuthentication):
    """
    Custom Authentication class that authenticates users using JWT or Google OAuth.
    """

    def authenticate(self, request):
        # Authenticate using JWT
        try:
            token = request.headers.get("Authorization", "").split(" ")[1]
            decoded_token = verify_token(token)
            user = CustomUser.objects.get(id=decoded_token["user_id"])
            return user, decoded_token
        except AuthenticationFailed:
            return None
        except Exception as e:
            logging.error(f"Non Authentication Error: {e}")

        # Authenticate using Google OAuth
        access_token = request.headers.get("Authorization", None)

        if access_token is None:
            return None

        access_token = access_token.split(" ")[1]
        base_url = "https://www.googleapis.com/oauth2/v3"
        token_info_url = f"{base_url}/tokeninfo?access_token={access_token}"
        token_info = requests.get(
            token_info_url,
            timeout=10,
        ).json()

        if (
            int(token_info["expires_in"]) <= 0
            or token_info["aud"] != settings.GOOGLE_CLIENT_ID
        ):
            return None

        user_info_url = f"{base_url}/userinfo?access_token={access_token}"
        user_info = requests.get(
            user_info_url,
            timeout=10,
        ).json()

        if token_info["sub"] != user_info["sub"]:
            return None

        user_data = {
            "email": user_info["email"],
            "username": user_info["name"],
            "password": "randompassword",
        }

        try:
            return CustomUser.objects.get(email=user_data["email"]), None
        except ObjectDoesNotExist:
            return None


def create_keap_company(company_id):
    """
    Creates a company record in Keap.
    """
    try:
        company = Company.objects.get(id=company_id)
        url = "https://api.infusionsoft.com/crm/rest/v1/companies"
        headers = {
            "X-Keap-API-Key": settings.KEAP_API_KEY,
            "Content-Type": "application/json",
        }
        body = {
            "company_name": company.name,
            "email_address": company.email,
            "phone_number": {"number": company.phone},
            "notes": float(company.product.amount),
        }
        response = requests.post(url, headers=headers, json=body, timeout=10)

        if response.status_code != 201:
            logging.error(f"Error creating company in Keap: {response.text}")

    except Exception as e:
        logging.error(f"Error in create_keap_company: {e}")


def create_keap_user(user_id):
    """
    Creates a user record in Keap.
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        company = user.company
        url = "https://api.infusionsoft.com/crm/rest/v1/companies"
        headers = {"X-Keap-API-Key": settings.KEAP_API_KEY}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            logging.error(f"Error getting companies in Keap: {response.text}")
            return

        company_id = ""
        companies = response.json()

        for comp in companies["companies"]:
            if comp["company_name"] == company.name:
                company_id = comp["id"]
                break

        url = "https://api.infusionsoft.com/crm/rest/v1/contacts"
        headers = {
            "X-Keap-API-Key": settings.KEAP_API_KEY,
            "Content-Type": "application/json",
        }
        body = {
            "given_name": user.first_name,
            "family_name": user.last_name,
            "email_addresses": [{"email": user.email, "field": "EMAIL1"}],
            "phone_numbers": [{"number": user.phone, "field": "PHONE1"}],
            "company": {"id": company_id},
        }
        response = requests.post(url, headers=headers, json=body, timeout=10)

        if response.status_code != 201:
            logging.error(f"Error creating user in Keap: {response.text}")
            return

        if float(company.product.amount) == 0:
            url = "https://api.infusionsoft.com/crm/rest/v1/tags/127/contacts"
            body = {"ids": [response.json()["id"]]}
            response = requests.post(
                url, headers=headers, json=body, timeout=10
            )

            if response.status_code != 200:
                logging.error(
                    f"Error adding user to tag in Keap: {response.text}"
                )

    except Exception as e:
        logging.error(f"Error in create_keap_user: {e}")
