from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.conf import settings
from .models import Product
from accounts.utils import makeCompany
from datetime import datetime, timedelta

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST' ])
def save_stripe_info(request):
    if request.method == 'POST':
        print("here")
        data = request.data
        try:
            product = Product.objects.get(tier=data['tier'], timeFrame=data['timeFrame'])
        except Product.DoesNotExist:
            print("Product does not exist")
            return Response("Product does not exist", status=status.HTTP_400_BAD_REQUEST)
        email = data['email']
        company = data['company']
        phone = data['phone']
        comp = makeCompany(company, email, phone)
        if type(comp) == dict:
            print("company equals dict")
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
        print("I am now here")
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
                'data': {'publishable_key': settings.STRIPE_PUBLISHABLE_KEY } }
        )

@api_view(['POST'])
def stripe_webhooks(request):
    print(1)
    if request.method == 'POST':
        print(2)
        payload = request.body
        print(3)
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        print(4)
        event = None
        print(5)
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_SECRET_TEST
            )
            print(6)
        except ValueError as e:
            print(7)
            # Invalid payload
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            print(8)
            # Invalid signature
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # Handle the checkout.session.completed event
        print(9)
        print(event['type'])
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            print(session)
            # Fulfill the purchase...
            print('Payment was successful.')
            print(11)
        return Response(status=status.HTTP_200_OK)
