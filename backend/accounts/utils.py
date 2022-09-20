from .models import Client, Company, ZipCode, HomeListing
from time import sleep
import os
import http.client
import json
from celery import shared_task
from datetime import datetime, timedelta
from django.conf import settings


@shared_task
def saveClientList(row, company_id):
    company = Company.objects.get(id=company_id)
    try:
        if int(row['zip']) > 500 and int(row['zip']) < 99951:
        # if int(row['zip']) > 37770 and int(row['zip']) < 37775:
            zipCode, created = ZipCode.objects.get_or_create(zipCode=row["zip"])
            Client.objects.update_or_create(
                    name= row['name'],
                    address= row['street'],
                    zipCode= zipCode,
                    company= company,
                    city= row['city'],
                    state = row['state'],
                    )
    except:
        try:
            if type(row['zip']) != int:
                row['zip'] = (row['zip'].split('-'))[0]
            if int(row['zip']) > 500 and int(row['zip']) < 99951:
            # if int(row['zip']) > 37770 and int(row['zip']) < 37775:
                zipCode, created = ZipCode.objects.get_or_create(zipCode=row["zip"])
                Client.objects.update_or_create(
                        name= row["name"],
                        address= row['street'],
                        zipCode= zipCode,
                        company= company,
                        city= row['city'],
                        state = row['state'],
                        )
        except Exception as e:
            print(e)

@shared_task
def getAllZipcodes(company):
    company_object = Company.objects.get(id=company)
    zipCode_objects = Client.objects.filter(company=company_object).values('zipCode')
    zipCodes = ZipCode.objects.filter(zipCode__in=zipCode_objects, lastUpdated__lt=datetime.today().strftime('%Y-%m-%d'))
    for zip in list(zipCodes.values('zipCode')):
        getHomesForSale.delay(zip, company)
        getHomesForRent.delay(zip, company)
        getSoldHomes.delay(zip, company)
    # getHomesForSale.delay(list(zipCodes.values('zipCode')), company)
    # getHomesForRent.delay(list(zipCodes.values('zipCode')), company)
    # getSoldHomes.delay(list(zipCodes.values('zipCode')), company)

    #TODO uncomment this
    zipCodes.update(lastUpdated=datetime.today().strftime('%Y-%m-%d'))

@shared_task
def getHomesForSale(zip, company):#, company, zipCode_objects):        
    print(zip)
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

        # try:
        #     with open(f"/Users/reidelkins/Work/isMyCustomerMoving/sep15_{count}_sale.json", "w+") as f:
        #         count += 1
        #         json.dump(data, f)
        # except:
        #     pass
    updateStatus(zip, company, 'For Sale')
   


# @shared_task
# def getHomesForSale(zipCodes, company):#, company, zipCode_objects):    
#     count = 0
#     print(len(zipCodes))
#     for zip in zipCodes:
#         print(zip)
#         offset = 0
#         zip = zip['zipCode']
#         moreListings = True
#         while(moreListings):
#             conn = http.client.HTTPSConnection("us-real-estate.p.rapidapi.com")

#             headers = {
#                 'X-RapidAPI-Key': settings.RAPID_API,
#                 'X-RapidAPI-Host': "us-real-estate.p.rapidapi.com"
#                 }

#             conn.request("GET", f"/v2/for-sale-by-zipcode?zipcode={zip}&offset={offset}&limit=200&sort:newest", headers=headers)

#             res = conn.getresponse()
#             data = res.read().decode("utf-8")
#             data = json.loads(data)
#             total = data['data']['home_search']['total']
#             print(f"The total amount listed for sale at {zip} is {total} and the current offset is {offset}")
#             offset += data['data']['home_search']['count']
#             print(f"The new offset is {offset}")
#             if offset >= total:
#                 moreListings = False
#             data = data['data']['home_search']['results']

#             for listing in data:
#                 zip_object, created = ZipCode.objects.get_or_create(zipCode = listing['location']['address']['postal_code'])
#                 try:
#                     HomeListing.objects.get_or_create(
#                                 zipCode= zip_object,
#                                 address= listing['location']['address']['line'],
#                                 status= 'For Sale',
#                                 listed= listing['list_date']
#                                 )
#                 except:
#                     print(f"zip: {zip_object}")
#                     print(f"address: {listing['location']['address']['line']}")

#             # try:
#             #     with open(f"/Users/reidelkins/Work/isMyCustomerMoving/sep15_{count}_sale.json", "w+") as f:
#             #         count += 1
#             #         json.dump(data, f)
#             # except:
#             #     pass
#     updateStatus(company, 'For Sale')
       

@shared_task
def getHomesForRent(zip, company):
    count = 0
    # for zip in zipCodes:
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
            # try:
            #     with open(f"/Users/reidelkins/Work/isMyCustomerMoving/sep15_{count}_{zip}_rent.json", "w+") as f:
            #         count += 1
            #         json.dump(data, f)
            # except:
            #     pass
    updateStatus(zip, company, 'For Rent')


@shared_task               
def getSoldHomes(zip, company):
    count = 0
    # for zip in zipCodes:
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
        # try:
        #     with open(f"/Users/reidelkins/Work/isMyCustomerMoving/sep15_{count}_{zip}_sold.json", "w+") as f:
        #         count += 1
        #         json.dump(data, f)
        # except:
        #     pass
    updateStatus(zip, company, 'Recently Sold (6)')
    updateStatus(zip, company, 'Recently Sold (12)')

def updateStatus(zip, company, status):
    company_object = Company.objects.get(id=company)
    zip = ZipCode.objects.get(zipCode=zip)
    listedAddresses = HomeListing.objects.filter(zipCode=zip, status=status).values('address')
    print(len(listedAddresses))
    Client.objects.filter(company=company_object, address__in=listedAddresses).update(status=status)
    