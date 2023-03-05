from celery import shared_task
import requests
import gc

from django.conf import settings

from accounts.models import Company
from .models import Client, Task
from .utils import saveClientList, updateClientList, doItAll
from simple_salesforce import Salesforce



@shared_task
def get_fieldEdge_clients(company_id, task_id):
    company = Company.objects.get(id=company_id)

@shared_task
def get_hubspot_clients(company_id, task_id):
    company = Company.objects.get(id=company_id)

@shared_task
def get_salesforce_clients(company_id, task_id=None):
    company = Company.objects.get(id=company_id)

    sf = Salesforce(
        instance_url="https://ismycustomermoving-dev-ed.develop.my.salesforce.com",
        session_id=company.sfAccessToken,
        consumer_key=settings.SALESFORCE_CONSUMER_KEY, 
        consumer_secret=settings.SALESFORCE_CONSUMER_SECRET)
    
    contacts = sf.query("SELECT FirstName, LastName, Phone, MailingStreet FROM Contact")
    clients=[]
    print(len(contacts['records']))
    count = 0
    for contact in contacts['records']:
    
        x = contact['MailingStreet']
        count += 1
        if x != None:
            x = x.split('\n')
            print(x)
            if len(x) > 1:
                street = x[0]
                x = x[1].replace(',', '')
                x = x.split(' ')
                # print(x)
                if len(x) == 3 and street != None:
                    client = {
                        "name": f"{contact['FirstName']} {contact['LastName']}",                
                        "phone number": contact['Phone'],
                        "address": street,
                        "city": x[0],
                        "state": x[1],
                        "zip code": x[2],
                    }
                    clients.append(client)
        

    saveClientList(clients, company_id)

    # bulk = SalesforceBulk(sessionId="https://login.salesforce.com/id/00DDn00000DsoYnMAJ/005Dn000007Eo6XIAS", host="https://ismycustomermoving-dev-ed.develop.my.salesforce.com")
    # job = bulk.create_query_job("Contact", contentType='JSON')
    # batch = bulk.query(job, "select Id,LastName from Contact")
    # bulk.close_job(job)
    # while not bulk.is_batch_done(batch):
    #     time.sleep(10)

    # for result in bulk.get_all_results_for_query_batch(batch):
    #     result = json.load(IteratorBytesIO(result))
    #     for row in result:
    #         print(row) # dictionary rows
    


@shared_task
def get_serviceTitan_clients(company_id, task_id):
    company = Company.objects.get(id=company_id)
    tenant = company.tenantID
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = f'grant_type=client_credentials&client_id={company.clientID}&client_secret={company.clientSecret}'
    response = requests.post('https://auth.servicetitan.io/connect/token', headers=headers, data=data)    

    headers = {'Authorization': response.json()['access_token'], 'Content-Type': 'application/json', 'ST-App-Key': settings.ST_APP_KEY}
    clients = []
    moreClients = True
    #get client data
    page = 1
    while(moreClients):
        print(f'getting page {page} of clients')
        response = requests.get(f'https://api.servicetitan.io/crm/v2/tenant/{tenant}/locations?page={page}&pageSize=2500', headers=headers)
        page += 1
        clients = response.json()['data']
        if response.json()['hasMore'] == False:
            moreClients = False
        saveClientList.delay(clients, company_id)
        try:
            del clients
        except:
            pass
        try:
            del response
        except:
            pass
    clients = Client.objects.filter(company=company)
    # diff = clients.count() - company.product.customerLimit
    task = Task.objects.get(id=task_id)
    # if diff > 0:
    #     deleteClients = clients[:diff].values_list('id')
    #     # Client.objects.filter(id__in=deleteClients).delete()
    #     task.deletedClients = diff
    task.completed = True
    task.save()
    doItAll.delay(company_id)


    # clearing out old data    
    try:
        del deleteClients
    except:
        pass
    try:
        del diff
    except:
        pass
    gc.collect()
    frm = ""
    moreClients = True
    page = 0
    while(moreClients):
        page += 1
        print(f'getting phone page {page} of clients')
        response = requests.get(f'https://api.servicetitan.io/crm/v2/tenant/{tenant}/export/customers/contacts?from={frm}', headers=headers)
        # for number in response.json()['data']:
        #     numbers.append(number)
        numbers = response.json()['data']
        if response.json()['hasMore'] == True:
            frm = response.json()['continueFrom']
        else:
            moreClients = False        
        updateClientList.delay(numbers)
        try:
            del numbers
        except:
            pass
        try:
            del response
        except:
            pass
    gc.collect()        
    try:
        del frm
    except:
        pass
    try:
        del moreClients
    except:
        pass
    try:
        del headers
    except:
        pass
    try:
        del data
    except:
        pass
    try:
        del company
    except:
        pass
    try:
        del tenant
    except:
        pass