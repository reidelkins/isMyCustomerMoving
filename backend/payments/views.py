from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.conf import settings
from .models import Product
from accounts.utils import makeCompany
from datetime import datetime, timedelta

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY_TEST

@api_view(['POST' ])
def save_stripe_info(request):
    if request.method == 'POST':
        data = request.data
        try:
            product = Product.objects.get(tier=data['tier'], timeFrame=data['timeFrame'])
        except Product.DoesNotExist:
            return Response("Product does not exist", status=status.HTTP_400_BAD_REQUEST)
        email = data['email']
        company = data['company']
        phone = data['phone']
        comp = makeCompany(company, email, phone)
        if type(comp) == dict:
            return Response(comp, status=status.HTTP_400_BAD_REQUEST)
        

        payment_method_id = data['payment_method_id']
        extra_msg = ''
        customer_data = stripe.Customer.list(email=email).data

        if len(customer_data) == 0:
            customer = stripe.Customer.create(
            email=email, payment_method=payment_method_id, invoice_settings={
                'default_payment_method': payment_method_id
            })
        else:
            customer = customer_data[0]
            extra_msg = 'Customer already exists.'
        trialEnd = int((datetime.now()+ timedelta(days=7)).timestamp())
        subscription = stripe.Subscription.create(
            customer=customer,
            items=[
                {
                'price': product.pid
                }
            ],
            trial_end=trialEnd
        )
        return Response(status=status.HTTP_200_OK, 
            data={
                'message': 'Success', 
                'data': {'customer_id': customer.id,
                'extra_msg': extra_msg,
                'sub_id':  subscription,
                } }  
        )

@api_view(['POST'])
def setup_intent(request):
    if request.method == 'POST':
        intent = stripe.SetupIntent.create(
            payment_method_types=['card'],
        )
        return Response(status=status.HTTP_200_OK,
            data={
                'message': 'Success',
                'data': {'client_secret': intent.client_secret } }
        )
        
@api_view(['GET'])
def publishable_key(request):
    if request.method == 'GET':
        return Response(status=status.HTTP_200_OK,
            data={
                'message': 'Success',
                'data': {'publishable_key': settings.STRIPE_PUBLISHABLE_KEY_TEST } }
        )