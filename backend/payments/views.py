from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.conf import settings

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
# Create your views here.
@api_view(['POST'])
def test_payment(request):
    if request.method == 'POST':
        test_payment_intent = stripe.PaymentIntent.create(
            amount=1000, currency='pln', 
            payment_method_types=['card'],
            receipt_email='test@example.com')
        return Response(status=status.HTTP_200_OK, data=test_payment_intent)

@api_view(['POST' ])
def save_stripe_info(request):
    if request.method == 'POST':
        print(1)
        data = request.data
        email = data['email']
        # payment_method_id = data['payment_method_id']
        extra_msg = ''

        customer_data = stripe.Customer.list(email=email).data 
        print("got data")
        # creating customer
        if len(customer_data) == 0:
            print("making customer")
            customer = stripe.Customer.create(
                email=email
            )
            # customer = stripe.Customer.create(
            # email=email, payment_method=payment_method_id, invoice_settings={
            #     'default_payment_method': payment_method_id
            # })
        else:
            customer = customer_data[0]
            extra_msg = 'Customer already exists.'
            print(1)    
        subscription = stripe.Subscription.create(
            customer=customer,
            items=[
                {
                'price': 'price_1M9vkLAkLES5P4qQY8jxNJD5' #here paste your price id
                }
            ],
            payment_behavior='default_incomplete',
            payment_settings={'save_default_payment_method': 'on_subscription'},
            expand=['latest_invoice.payment_intent'],
        )
        print("made subscription")
        return Response(status=status.HTTP_200_OK, 
            data={
                'message': 'Success', 
                'data': {'customer_id': customer.id,
                'extra_msg': extra_msg,
                'sub_id':  subscription,
                'clientSecret': subscription.latest_invoice.payment_intent.client_secret} }  
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