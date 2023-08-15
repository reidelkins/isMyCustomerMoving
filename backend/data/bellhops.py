from config import settings
from data.models import Client

from celery import shared_task
import logging
import requests


def get_bellhop_auth():
    url = "https://partners.bellhop.com/api/partner-api/authorize"
    data = {
        "grant_type": "client_credentials",
        "clientId": settings.BELLHOP_OAUTH_CLIENT_ID,
        "clientSecret": settings.BELLHOP_OAUTH_CLIENT_SECRET,
        "audience": "https://partners.bellhop.com"
    }

    response = requests.post(url, data=data)
    if response.status_code != 200:
        raise Exception("Bellhop authentication failed")
    return response.data["access_token"]


@shared_task
def create_bellhops_lead(client_id, access_token):
    client = Client.objects.get(id=client_id)
    url = "https://partners.bellhop.com/api/partner-api/v0/sales/leads"

    new_zip_code = "N/A"
    new_street = "N/A"
    new_city = "N/A"
    new_state = "N/A"
    if client.new_address:
        new_zip_code = client.new_zip_code.zip_code
        new_street = client.new_address
        new_city = client.new_city
        new_state = client.new_state

    data = {
        "first_name": client.first_name,
        "last_name": client.last_name,
        "description": "",
        "email": client.email,
        "phone": client.phone_number,
        "origin_street": client.address,
        "origin_city": client.city,
        "origin_postal_code": client.zip_code.zip_code,
        "origin_state": client.state,
        "destination_street": new_street,
        "destination_city": new_city,
        "destination_postal_code": new_zip_code,
        "destination_state": new_state,
        "lead_type": "IMCM",
        "lead_record_type": "IMCM",
        "load_date": "N/A",
        "close_date": "N/A"
    }
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.post(url, data=data, headers=headers)
    if response.status_code != 200:
        logging.error(f"Bellhop lead creation failed for client {client.id}")
