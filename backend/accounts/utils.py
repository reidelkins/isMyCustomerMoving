from .models import Client, Company, ZipCode, HomeListing

import os
import http.client
import json
from datetime import datetime, timedelta
from django.conf import settings


def getAllZipcodes(company):
    company = Company.objects.get(id=company)
    zipCode_objects = Client.objects.filter(company=company).values('zipCode')
    zipCodes = list(ZipCode.objects.filter(zipCode__in=zipCode_objects, lastUpdated__lt=datetime.today().strftime('%Y-%m-%d')).values('zipCode'))
    # getHomesForSale(zipCodes)
    # getHomesForRent(zipCodes)
    getSoldHomes(zipCodes)
    # updateStatus(company, zipCode_objects)

    #TODO uncomment this
    # ZipCode.objects.filter(zipCode__in=zipCode_objects, lastUpdated__lt=datetime.today().strftime('%Y-%m-%d')).update(lastUpdated=datetime.today().strftime('%Y-%m-%d'))
    

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

                total = data['data']['home_search']['total']
                print(f"The total amount listed here is {total} and the current offset is {offset}")
                offset += data['data']['home_search']['count']
                print(f"The new offset is {offset}")
                if offset >= total:
                    moreListings = False
                with open(f"/Users/reidelkins/Work/isMyCustomerMoving/sep14_{count}.json", "w+") as f:
                    count += 1
                    json.dump(data, f)


    #TODO remove this
    for i in range(10):
        with open(f"/Users/reidelkins/Work/isMyCustomerMoving/sep14_{i}.json", "r") as f:
            data = json.load(f)

        data = data['data']['home_search']['results']
        print(f"This is how much data in {i}: {len(data)}")
        for listing in data:
            zip_object = ZipCode.objects.get(zipCode = listing['location']['address']['postal_code'])
            try:
                HomeListing.objects.get_or_create(
                            zipCode= zip_object,
                            address= listing['location']['address']['line'],
                            )
            except:
                print(f"zip: {zip_object}")
                print(f"address: {listing['location']['address']['line']}")


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
            print(f"The total amount listed here is {total} and the current offset is {offset}")
            offset += data['data']['home_search']['count']
            print(f"The new offset is {offset}")
            if offset >= total:
                moreListings = False
            with open(f"/Users/reidelkins/Work/isMyCustomerMoving/sep14_{count}_rent.json", "w+") as f:
                count += 1
                json.dump(data, f)

            data = data['data']['home_search']['results']

            for listing in data:
                zip_object, created  = ZipCode.objects.get_or_create(zipCode = listing['location']['address']['postal_code'])
                try:
                    HomeListing.objects.get_or_create(
                                zipCode= zip_object,
                                address= listing['location']['address']['line'],
                                status= 'For Rent',
                                listed= listing['list_date']
                                )
                except:
                    print(f"zip: {zip_object}")
                    print(f"address: {listing['location']['address']['line']}")

                
def getSoldHomes(zipCodes):
    zipCodes = zipCodes[-3:-2]
    count = 0
    for zip in zipCodes:
        offset = 0
        zip = zip['zipCode']
        moreListings = True
        while(moreListings):
            # conn = http.client.HTTPSConnection("us-real-estate.p.rapidapi.com")

            # headers = {
            #     'X-RapidAPI-Key': settings.RAPID_API,
            #     'X-RapidAPI-Host': "us-real-estate.p.rapidapi.com"
            #     }

            # conn.request("GET", f"/v2/sold-homes-by-zipcode?zipcode={zip}&offset={offset}&limit=200&sort=sold_date&max_sold_days=365", headers=headers)

            # res = conn.getresponse()
            # data = res.read().decode("utf-8")
            # data = json.loads(data)
            

            # total = data['data']['home_search']['total']
            # print(f"The total amount listed here is {total} and the current offset is {offset}")
            # offset += data['data']['home_search']['count']
            # print(f"The new offset is {offset}")
            # if offset >= total:
            #     moreListings = False
            # with open(f"/Users/reidelkins/Work/isMyCustomerMoving/sep14_{count}_sold.json", "w+") as f:
            #     count += 1
            #     json.dump(data, f)
            with open(f"/Users/reidelkins/Work/isMyCustomerMoving/sep14_{1}_sold.json", "r") as f:
                data = json.load(f)

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
            return


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

