from .models import Client, Company, ZipCode, HomeListing
from time import sleep
import os
import http.client
import json
from datetime import datetime, timedelta
from django.conf import settings

import requests

def count_words_at_url(url):
    resp = requests.get(url)
    return len(resp.text.split())

from rq import Queue
from worker import conn

q = Queue(connection=conn)


def getAllZipcodes(company):
    company = Company.objects.get(id=company)
    zipCode_objects = Client.objects.filter(company=company).values('zipCode')
    zipCodes = ZipCode.objects.filter(zipCode__in=zipCode_objects, lastUpdated__lt=datetime.today().strftime('%Y-%m-%d'))
    for i in range(16):
        print(i)
        sleep(2)
    # getHomesForSale(list(zipCodes.values('zipCode')))
    # getHomesForRent(list(zipCodes.values('zipCode')))
    # getSoldHomes(list(zipCodes.values('zipCode')))
    updateStatus(company, zipCode_objects)

    #TODO uncomment this
    zipCodes.update(lastUpdated=datetime.today().strftime('%Y-%m-%d'))

def getHomesForSale(zipCodes):    
    count = 0
    for zip in zipCodes:
        offset = 0
        zip = zip['zipCode']
        moreListings = True
        while(moreListings):
            conn = http.client.HTTPSConnection("us-real-estate.p.rapidapi.com")

            headers = {
                'X-RapidAPI-Key': settings.RAPID_API,
                'X-RapidAPI-Host': "us-real-estate.p.rapidapi.com"
                }

            conn.request("GET", f"/v2/for-sale-by-zipcode?zipcode={zip}&offset={offset}&limit=200&sort:newest", headers=headers)

            res = conn.getresponse()
            data = res.read().decode("utf-8")
            data = json.loads(data)
            total = data['data']['home_search']['total']
            print(f"The total amount listed for sale at {zip} is {total} and the current offset is {offset}")
            offset += data['data']['home_search']['count']
            print(f"The new offset is {offset}")
            if offset >= total:
                moreListings = False
            data = data['data']['home_search']['results']

            for listing in data:
                zip_object, created = ZipCode.objects.get_or_create(zipCode = listing['location']['address']['postal_code'])
                try:
                    HomeListing.objects.get_or_create(
                                zipCode= zip_object,
                                address= listing['location']['address']['line'],
                                status= 'For Sale',
                                listed= listing['list_date']
                                )
                except:
                    print(f"zip: {zip_object}")
                    print(f"address: {listing['location']['address']['line']}")

            try:
                with open(f"/Users/reidelkins/Work/isMyCustomerMoving/sep15_{count}_sale.json", "w+") as f:
                    count += 1
                    json.dump(data, f)
            except:
                pass
                

def getHomesForRent(zipCodes):
    count = 0
    for zip in zipCodes:
        offset = 0
        zip = zip['zipCode']
        moreListings = True
        while(moreListings):
            conn = http.client.HTTPSConnection("us-real-estate.p.rapidapi.com")

            headers = {
                'X-RapidAPI-Key': settings.RAPID_API,
                'X-RapidAPI-Host': "us-real-estate.p.rapidapi.com"
                }

            conn.request("GET", f"/v2/for-rent-by-zipcode?zipcode={zip}&offset={offset}&limit=200&sort=lowest_price", headers=headers)

            res = conn.getresponse()
            data = res.read().decode("utf-8")
            data = json.loads(data)
            

            total = data['data']['home_search']['total']
            print(f"The total amount listed for rent at {zip} is {total} and the current offset is {offset}")
            offset += data['data']['home_search']['count']
            print(f"The new offset is {offset}")
            if offset >= total:
                moreListings = False
            # with open(f"/Users/reidelkins/Work/isMyCustomerMoving/sep14_{count}_rent.json", "w+") as f:
            #     count += 1
            #     json.dump(data, f)

            data = data['data']['home_search']['results']

            for listing in data:
                zip_object, created  = ZipCode.objects.get_or_create(zipCode = listing['location']['address']['postal_code'])
                try:
                    if listing['list_date'] != None:
                        HomeListing.objects.get_or_create(
                                    zipCode= zip_object,
                                    address= listing['location']['address']['line'],
                                    status= 'For Rent',
                                    listed= listing['list_date']
                                    )
                    else:
                        HomeListing.objects.get_or_create(
                                    zipCode= zip_object,
                                    address= listing['location']['address']['line'],
                                    status= 'For Rent',
                                    )
                except Exception as e:
                    print(e)
                    print(f"Listed: {listing['list_date']}")
                    print(f"zip: {zip_object}")
                    print(f"address: {listing['location']['address']['line']}")
            try:
                with open(f"/Users/reidelkins/Work/isMyCustomerMoving/sep15_{count}_{zip}_rent.json", "w+") as f:
                    count += 1
                    json.dump(data, f)
            except:
                pass
            
                
def getSoldHomes(zipCodes):
    count = 0
    for zip in zipCodes:
        offset = 0
        zip = zip['zipCode']
        moreListings = True
        while(moreListings):
            conn = http.client.HTTPSConnection("us-real-estate.p.rapidapi.com")

            headers = {
                'X-RapidAPI-Key': settings.RAPID_API,
                'X-RapidAPI-Host': "us-real-estate.p.rapidapi.com"
                }

            conn.request("GET", f"/v2/sold-homes-by-zipcode?zipcode={zip}&offset={offset}&limit=200&sort=sold_date&max_sold_days=400", headers=headers)

            res = conn.getresponse()
            data = res.read().decode("utf-8")
            data = json.loads(data)
            

            total = data['data']['home_search']['total']
            print(f"The total amount that have been sold at {zip} is {total} and the current offset is {offset}")
            offset += data['data']['home_search']['count']
            print(f"The new offset is {offset}")
            if offset >= total:
                moreListings = False

            data = data['data']['home_search']['results']

            for listing in data:
                zip_object, created  = ZipCode.objects.get_or_create(zipCode = listing['location']['address']['postal_code'])
                sold_date = datetime.strptime(listing['description']['sold_date'], '%Y-%m-%d')
                halfYear = datetime.today() - timedelta(days=180)
                if sold_date > halfYear:
                    status = 'Recently Sold (6)'
                else:
                    status = 'Recently Sold (12)'
                try:
                    HomeListing.objects.get_or_create(
                                zipCode= zip_object,
                                address= listing['location']['address']['line'],
                                status= status,
                                listed= listing['description']['sold_date']
                                )
                except Exception as e:
                    print(e)
                    print(f"zip: {zip_object}")
                    print(f"address: {listing['location']['address']['line']}")
            
            try:
                with open(f"/Users/reidelkins/Work/isMyCustomerMoving/sep15_{count}_{zip}_sold.json", "w+") as f:
                    count += 1
                    json.dump(data, f)
            except:
                pass


def updateStatus(company, zipCodes):
    listedAddresses = HomeListing.objects.filter(zipCode__in=zipCodes, status='For Rent').values('address')
    print(len(listedAddresses))
    clientsToUpdate = Client.objects.filter(company=company, address__in=listedAddresses)
    clientsToUpdate.update(status="For Rent")

    listedAddresses = HomeListing.objects.filter(zipCode__in=zipCodes, status='For Sale').values('address')
    print(len(listedAddresses))
    clientsToUpdate = Client.objects.filter(company=company, address__in=listedAddresses)
    clientsToUpdate.update(status="For Sale")

    listedAddresses = HomeListing.objects.filter(zipCode__in=zipCodes, status='Recently Sold (6)').values('address')
    print(len(listedAddresses))
    clientsToUpdate = Client.objects.filter(company=company, address__in=listedAddresses)
    clientsToUpdate.update(status="Recently Sold (6)")

    listedAddresses = HomeListing.objects.filter(zipCode__in=zipCodes, status='Recently Sold (12)').values('address')
    print(len(listedAddresses))
    clientsToUpdate = Client.objects.filter(company=company, address__in=listedAddresses)
    clientsToUpdate.update(status="Recently Sold (12)")

