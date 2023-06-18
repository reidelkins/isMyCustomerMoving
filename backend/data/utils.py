from time import sleep
from accounts.models import Company, CustomUser
from config import settings
from .models import (
    Client,
    ZipCode,
    HomeListing,
    ClientUpdate,
    Task,
    HomeListingTags,
    SavedFilter,
)
from .serializers import ZapierClientSerializer, HomeListingSerializer

from celery import shared_task
from datetime import datetime, timedelta, date
import gc
import json
import logging
import requests
import traceback
import xml.etree.ElementTree as ET


from django.template.loader import get_template
from django.core.mail import EmailMessage, send_mail
from django.db.models.functions import Coalesce


def delVariables(vars):
    for var in vars:
        try:
            del var
        except:
            pass
    gc.collect()


def findClientCount(subscriptionType):
    if subscriptionType == "Small Business":
        ceiling = 5000
    elif subscriptionType == "Franchise":
        ceiling = 10000
    elif subscriptionType == "Large Business":
        ceiling = 20000
    # elif subscriptionType == "Free Tier":
    #     ceiling = 100
    else:
        ceiling = 100000
    return ceiling


def findClientsToDelete(clientCount, subscriptionType):
    ceiling = findClientCount(subscriptionType)
    if clientCount > ceiling:
        return clientCount - ceiling
    else:
        return 0


def reactivateClients(companyID):
    company = Company.objects.get(id=companyID)
    clients = Client.objects.filter(company=company)
    clientCeiling = findClientCount(company.product.product.name)
    if clientCeiling > clients.count():
        clients.update(active=True)
    else:
        toReactiveCount = clientCeiling - clients.filter(active=True).count()
        clients.filter(active=False).order_by("id")[:toReactiveCount].update(
            active=True
        )


@shared_task
def deleteExtraClients(companyID, taskID=None):
    try:
        company = Company.objects.get(id=companyID)
        clients = Client.objects.filter(company=company, active=True)
        deletedClients = findClientsToDelete(
            clients.count(), company.product.product.name
        )
        if deletedClients > 0:
            Client.objects.filter(
                id__in=list(
                    clients.values_list("id", flat=True)[:deletedClients]
                )
            ).update(active=False)
            admins = CustomUser.objects.filter(company=company, status="admin")
            mail_subject = "IMCM Clients Deleted"
            messagePlain = "Your company has exceeded the number of clients allowed for your subscription. The oldest clients have been deleted. You can upgrade your subscription at any time to increase the number of clients you can have."
            message = get_template("clientsDeleted.html").render(
                {"deletedClients": deletedClients}
            )
            for admin in admins:
                send_mail(
                    subject=mail_subject,
                    message=messagePlain,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[admin.email],
                    html_message=message,
                    fail_silently=False,
                )
    except:
        deletedClients = 0
    if taskID:
        task = Task.objects.get(id=taskID)
        task.deletedClients = deletedClients
        task.completed = True
        task.save()


def parseStreets(street):
    conversions = {
        "Alley": "Aly",
        "Avenue": "Ave",
        "Boulevard": "Blvd",
        "Circle": "Cir",
        "Court": "Crt",
        "Cove": "Cv",
        "Canyon": "Cnyn",
        "Drive": "Dr",
        "Expressway": "Expy",
        "Highway": "Hwy",
        "Lane": "Ln",
        "Parkway": "Pkwy",
        "Place": "Pl",
        "Pike": "Pk",
        "Point": "Pt",
        "Road": "Rd",
        "Square": "Sq",
        "Street": "St",
        "Terrace": "Ter",
        "Trail": "Trl",
        "South": "S",
        "North": "N",
        "West": "W",
        "East": "E",
        "Northeast": "NE",
        "Northwest": "NW",
        "Southeast": "SE",
        "Southwest": "SW",
        "Ne": "NE",
        "Nw": "NW",
        "Sw": "SW",
        "Se": "SE",
    }
    for word in street.split():
        if word in conversions:
            street = street.replace(word, conversions[word])
    return street


def formatZip(zip):
    try:
        if type(zip) == float:
            zip = int(zip)
        if type(zip) == str:
            zip = zip.replace(" ", "")
            zip = (zip.split("-"))[0]
        if int(zip) > 500 and int(zip) < 99951:
            if len(zip) == 4:
                zip = "0" + str(zip)
            elif len(zip) == 3:
                zip = "00" + str(zip)
            elif len(zip) != 5:
                return False
        return zip
    except:
        return False


@shared_task
def saveClientList(clients, company_id, task=None):
    clientsToAdd, company, badStreets = "", "", ""
    # create
    clientsToAdd = []
    company = Company.objects.get(id=company_id)
    badStreets = [
        "none",
        "null",
        "na",
        "n/a",
        "tbd",
        ".",
        "unk",
        "unknown",
        "no address listed",
        "no address",
        "cmo",
    ]
    for i in range(len(clients)):
        # service titan
        try:
            if "active" in clients[i]:
                if clients[i]["active"]:
                    street = parseStreets(
                        (str(clients[i]["address"]["street"])).title()
                    )
                    if street.lower() in badStreets or "tbd" in street.lower():
                        continue
                    zip = formatZip(clients[i]["address"]["zip"])
                    if int(zip) < 500 or int(zip) > 99951:
                        continue
                    zipCode = ZipCode.objects.get_or_create(zipCode=str(zip))[0]
                    city = (clients[i]["address"]["city"],)
                    city = city[0]
                    state = clients[i]["address"]["state"]
                    name = clients[i]["name"]
                    if (
                        clients[i]["address"]["zip"] == None
                        or not street
                        or not zip
                        or not city
                        or not state
                        or not name
                        or zip == 0
                    ):
                        continue
                    clientsToAdd.append(
                        Client(
                            address=street,
                            zipCode=zipCode,
                            city=city,
                            state=state,
                            name=name,
                            company=company,
                            servTitanID=clients[i]["customerId"],
                        )
                    )
            # file upload
            else:
                street = parseStreets((str(clients[i]["address"])).title())
                if street.lower() in badStreets:
                    continue
                zip = formatZip(clients[i]["zip code"])
                zipCode = ZipCode.objects.get_or_create(zipCode=str(zip))[0]
                city = clients[i]["city"]
                state = clients[i]["state"]
                name = clients[i]["name"]
                if "phone number" in clients[i]:
                    phoneNumber = clients[i]["phone number"]
                else:
                    phoneNumber = ""
                if (
                    clients[i]["zip code"] == None
                    or not street
                    or not zip
                    or not city
                    or not state
                    or not name
                    or zip == 0
                ):
                    continue
                clientsToAdd.append(
                    Client(
                        address=street,
                        zipCode=zipCode,
                        city=city,
                        state=state,
                        name=name,
                        company=company,
                        phoneNumber=phoneNumber,
                    )
                )
        except Exception as e:
            logging.error("create error")
            logging.error(e)
    Client.objects.bulk_create(clientsToAdd, ignore_conflicts=True)

    if task:
        deleteExtraClients.delay(company_id, task)
        doItAll.delay(company_id)
    delVariables([clientsToAdd, clients, company, company_id, badStreets])


@shared_task
def updateClientList(numbers):
    phoneNumbers, clients = "", ""
    phoneNumbers = {}
    for number in numbers:
        try:
            phoneNumbers[number["customerId"]] = number["phoneSettings"][
                "phoneNumber"
            ]
        except:
            continue
    clients = Client.objects.filter(servTitanID__in=list(phoneNumbers.keys()))
    for client in clients:
        client.phoneNumber = phoneNumbers[client.servTitanID]
        client.save()
    delVariables([phoneNumbers, clients, numbers])


@shared_task
def updateStatus(zip, company, status):
    (
        zipCode_object,
        listedAddresses,
        clientsToUpdate,
        previousListed,
        newlyListed,
        toList,
        listing,
        clientsToUpdate,
    ) = ("", "", "", "", "", "", "", "")
    company = Company.objects.get(id=company)
    try:
        zipCode_object = ZipCode.objects.get(zipCode=zip)
    except Exception as e:
        logging.error(f"ERROR during updateStatus: {e} with zipCode {zip}")
        return
    # addresses from all home listings with the provided zip code and status
    listedAddresses = HomeListing.objects.filter(
        zipCode=zipCode_object, status=status
    ).values("address")
    clientsToUpdate = Client.objects.filter(
        company=company,
        address__in=listedAddresses,
        zipCode=zipCode_object,
        active=True,
        error_flag=False,
    )
    previousListed = Client.objects.filter(
        company=company,
        zipCode=zipCode_object,
        status=status,
        active=True,
        error_flag=False,
    )
    newlyListed = clientsToUpdate.difference(previousListed)
    # TODO add logic so if date for one listing is older than date of other, it will not update status
    for toList in newlyListed:
        existingUpdates = ClientUpdate.objects.filter(
            client=toList,
            status__in=["House For Sale", "House Recently Sold (6)"],
        )
        update = True
        try:
            for listing in existingUpdates:
                if (
                    listing.listed
                    > HomeListing.objects.filter(
                        address=toList.address, status=status
                    )[0].listed
                ):
                    update = False
        except Exception as e:
            logging.error(e)
        if update:
            homeListing = HomeListing.objects.get(
                address=toList.address, status=status
            )
            toList.status = status
            toList.price = homeListing.price
            toList.year_built = homeListing.year_built
            toList.housingType = homeListing.housingType
            toList.save()
            for tag in homeListing.tag.all():
                toList.tag.add(tag)

            if company.zapier_forSale and status == "House For Sale":
                try:
                    serializer = ZapierClientSerializer(toList)
                    serialized_data = serializer.data
                    requests.post(company.zapier_forSale, data=serialized_data)
                except Exception as e:
                    logging.error(e)
            if company.zapier_sold and status == "House Recently Sold (6)":
                try:
                    serializer = ZapierClientSerializer(toList)
                    serialized_data = serializer.data
                    requests.post(company.zapier_sold, data=serialized_data)
                except Exception as e:
                    logging.error(f"Zapier Sold: {e}")

        try:
            listing = HomeListing.objects.filter(
                zipCode=zipCode_object, address=toList.address, status=status
            )
            ClientUpdate.objects.get_or_create(
                client=toList, status=status, listed=listing[0].listed
            )
        except Exception as e:
            logging.error("Cant find listing to list")
            logging.error("This should not be the case")
    # TODO There is an issue where clients uploaded with wrong zip code and are being marked to be unlisted when they should not be
    # unlisted = previousListed.difference(clientsToUpdate)
    # for toUnlist in unlisted:
    #     toUnlist.status = "Taken Off Market"
    #     toUnlist.save()
    #     ClientUpdate.objects.create(client=toUnlist, status="Taken Off Market")

    clientsToUpdate = list(
        clientsToUpdate.values_list("servTitanID", flat=True)
    )
    for client in clientsToUpdate:
        if client is None:
            clientsToUpdate.remove(client)

    if clientsToUpdate:
        update_serviceTitan_client_tags.delay(
            clientsToUpdate, company.id, status
        )
    delVariables(
        [
            zipCode_object,
            listedAddresses,
            clientsToUpdate,
            previousListed,
            newlyListed,
            toList,
            listing,
            clientsToUpdate,
        ]
    )


@shared_task
def update_clients_statuses(company_id=None):
    companies, company, zipCode_objects, zipCodes, zips, zip = (
        "",
        "",
        "",
        "",
        "",
        "",
    )
    if company_id:
        companies = Company.objects.filter(id=company_id)
    else:
        companies = Company.objects.all()
    for company in companies:
        try:
            if company.product.id != "price_1MhxfPAkLES5P4qQbu8O45xy":
                zipCode_objects = Client.objects.filter(
                    company=company, active=True
                ).values("zipCode")
                zipCodes = zipCode_objects.distinct()
                zips = list(zipCodes.order_by("zipCode").values("zipCode"))
                for zip in zips:
                    zip = zip["zipCode"]
                    updateStatus.delay(zip, company.id, "House For Sale")
                for zip in zips:
                    zip = zip["zipCode"]
                    updateStatus.delay(
                        zip, company.id, "House Recently Sold (6)"
                    )
        except Exception as e:
            logging.error(
                f"ERROR during update_clients_statuses: {e} with company {company}"
            )
            logging.error(traceback.format_exc())

    delVariables([companies, company, zipCode_objects, zipCodes, zips, zip])


@shared_task
def sendDailyEmail(company_id=None):
    (
        companies,
        company,
        emails,
        subject,
        forSaleCustomers,
        soldCustomers,
        message,
        email,
        msg,
    ) = ("", "", "", "", "", "", "", "", "")
    if company_id:
        companies = Company.objects.filter(id=company_id)
    else:
        companies = Company.objects.all()
    for company in companies:
        try:
            if company.product.id != "price_1MhxfPAkLES5P4qQbu8O45xy":
                emails = list(
                    CustomUser.objects.filter(company=company).values_list(
                        "email"
                    )
                )
                subject = "Did Your Customers Move?"

                forSaleCustomers = (
                    Client.objects.filter(
                        company=company, status="House For Sale", active=True
                    )
                    .exclude(contacted=True)
                    .count()
                )
                soldCustomers = (
                    Client.objects.filter(
                        company=company,
                        status="House Recently Sold (6)",
                        active=True,
                    )
                    .exclude(contacted=True)
                    .count()
                )
                message = get_template("dailyEmail.html").render(
                    {"forSale": forSaleCustomers, "sold": soldCustomers}
                )

                if soldCustomers > 0 or forSaleCustomers > 0:
                    for email in emails:
                        email = email[0]
                        msg = EmailMessage(
                            subject, message, settings.EMAIL_HOST_USER, [email]
                        )
                        msg.content_subtype = "html"
                        msg.send()
        except Exception as e:
            logging.error(
                f"ERROR during sendDailyEmail: {e} with company {company}"
            )
            logging.error(traceback.format_exc())
    # if not company_id:
    #     HomeListing.objects.all().delete()
    ZipCode.objects.filter(
        lastUpdated__lt=datetime.today() - timedelta(days=3)
    ).delete()
    delVariables(
        [
            companies,
            company,
            emails,
            subject,
            forSaleCustomers,
            soldCustomers,
            message,
            email,
            msg,
        ]
    )


@shared_task
def auto_update(company_id=None, zip=None):
    from .realtor import getAllZipcodes

    company = ""
    if company_id:
        try:
            company = Company.objects.get(id=company_id)
            getAllZipcodes(company_id)

        except:
            logging.error("Company does not exist")
            return
        delVariables([company_id, company])
    elif zip:
        try:
            ZipCode.objects.get_or_create(zipCode=zip)
            getAllZipcodes("", zip=zip)
        except:
            logging.error("Zip does not exist")
            return
    else:
        company, companies = "", ""
        companies = Company.objects.all()
        for company in companies:
            try:
                logging.error(f"Auto Update: {company.product} {company.name}")
                if company.product.id != "price_1MhxfPAkLES5P4qQbu8O45xy":
                    logging.error("In the if statement")
                    getAllZipcodes(company.id)
                else:
                    logging.error("free tier")
            except Exception as e:
                logging.error(f"Auto Update Error: {e}")
        delVariables([company, companies])


def get_serviceTitan_accessToken(company):
    company = Company.objects.get(id=company)
    if company.serviceTitanAppVersion == 2:
        app_key = settings.ST_APP_KEY_2
    else:
        app_key = settings.ST_APP_KEY
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = f"grant_type=client_credentials&client_id={company.clientID}&client_secret={company.clientSecret}"
    response = requests.post(
        "https://auth.servicetitan.io/connect/token", headers=headers, data=data
    )
    headers = {
        "Authorization": response.json()["access_token"],
        "Content-Type": "application/json",
        "ST-App-Key": app_key,
    }
    return headers


@shared_task
def update_serviceTitan_client_tags(forSale, company, status):
    headers, data, response, payload, tagType, resp, error, word = (
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    )
    try:
        company = Company.objects.get(id=company)
        if forSale and (
            company.serviceTitanForSaleTagID
            or company.serviceTitanRecentlySoldTagID
        ):
            headers = get_serviceTitan_accessToken(company.id)
            if status == "House For Sale":
                tagType = [str(company.serviceTitanForSaleTagID)]
            elif status == "House Recently Sold (6)":
                forSaleToRemove = forSale
                tagType = [str(company.serviceTitanRecentlySoldTagID)]
                payload = {
                    "customerIds": forSaleToRemove,
                    "tagTypeIds": [str(company.serviceTitanForSaleTagID)],
                }
                response = requests.delete(
                    f"https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tags",
                    headers=headers,
                    json=payload,
                )
                if response.status_code != 200:
                    resp = response.json()
                    error = resp["title"]
                    error = (
                        error.replace("(", "")
                        .replace(")", "")
                        .replace(",", " ")
                        .replace(".", "")
                        .split()
                    )
                    for word in error:
                        if word.isdigit():
                            # Client.objects.filter(servTitanID=word).delete()
                            word = int(word)
                            if word in forSaleToRemove:
                                forSaleToRemove.remove(word)
                    payload = {
                        "customerIds": forSaleToRemove,
                        "tagTypeIds": tagType,
                    }
                    response = requests.delete(
                        f"https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tags",
                        headers=headers,
                        json=payload,
                    )
                    if response.status_code != 200:
                        logging.error(response.json())
            payload = {"customerIds": forSale, "tagTypeIds": tagType}
            response = requests.put(
                f"https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tags",
                headers=headers,
                json=payload,
            )
            if response.status_code != 200:
                resp = response.json()
                error = resp["title"]
                error = (
                    error.replace("(", "")
                    .replace(")", "")
                    .replace(",", " ")
                    .replace(".", "")
                    .split()
                )
                for word in error:
                    if word.isdigit():
                        # Client.objects.filter(servTitanID=word).delete()
                        word = int(word)
                        if word in forSale:
                            forSale.remove(word)
                if status == "House Recently Sold (6)":
                    payload = {
                        "customerIds": forSale,
                        "tagTypeIds": [str(company.serviceTitanForSaleTagID)],
                    }
                    response = requests.delete(
                        f"https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tags",
                        headers=headers,
                        json=payload,
                    )
                payload = {"customerIds": forSale, "tagTypeIds": tagType}
                response = requests.put(
                    f"https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tags",
                    headers=headers,
                    json=payload,
                )
    except Exception as e:
        logging.error("updating service titan clients failed")
        logging.error(f"ERROR: {e}")
        logging.error(traceback.format_exc())
    delVariables(
        [
            headers,
            data,
            response,
            payload,
            company,
            status,
            tagType,
            forSale,
            resp,
            error,
            word,
        ]
    )


@shared_task
def add_serviceTitan_contacted_tag(client, tagId):
    client = Client.objects.get(id=client)
    headers = get_serviceTitan_accessToken(client.company.id)
    payload = {"customerIds": [str(client.id)], "tagTypeIds": [str(tagId)]}
    requests.put(
        f"https://api.servicetitan.io/crm/v2/tenant/{str(client.company.tenantID)}/tags",
        headers=headers,
        json=payload,
    )


@shared_task
def remove_all_serviceTitan_tags(company=None, client=None):
    if company:
        try:
            company = Company.objects.get(id=company)
            if (
                company.serviceTitanForSaleTagID
                or company.serviceTitanRecentlySoldTagID
            ):
                headers = get_serviceTitan_accessToken(company.id)
                time = datetime.now()
                tagTypes = [
                    [str(company.serviceTitanForSaleTagID)],
                    [str(company.serviceTitanRecentlySoldTagID)],
                ]
                for tag in tagTypes:
                    # get a list of all the servTitanIDs for the clients with one from this company
                    clients = list(
                        Client.objects.filter(company=company)
                        .exclude(servTitanID=None)
                        .values_list("servTitanID", flat=True)
                    )
                    iters = (len(clients) // 250) + 1
                    for i in range(iters):
                        if time < datetime.now() - timedelta(minutes=15):
                            headers = get_serviceTitan_accessToken(company.id)
                            time = datetime.now()
                        x = clients[i * 250 : (i + 1) * 250]
                        payload = {"customerIds": x, "tagTypeIds": tag}
                        response = requests.delete(
                            f"https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tags",
                            headers=headers,
                            json=payload,
                        )
                        if response.status_code != 200:
                            resp = response.json()
                            error = resp["title"]
                            error = (
                                error.replace("(", "")
                                .replace(")", "")
                                .replace(",", " ")
                                .replace(".", "")
                            )
                            error = error.split()
                            for word in error:
                                if word.isdigit():
                                    word = int(word)
                                    # Client.objects.filter(servTitanID=word).delete()
                                    if word in x:
                                        x.remove(word)
                            if x:
                                payload = {"customerIds": x, "tagTypeIds": tag}
                                response = requests.delete(
                                    f"https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tags",
                                    headers=headers,
                                    json=payload,
                                )
                                if response.status_code != 200:
                                    logging.error(response.json())
                Client.objects.filter(company=company).update(
                    status="No Change"
                )
        except Exception as e:
            logging.error("updating service titan clients failed")
            logging.error(f"ERROR: {e}")
            logging.error(traceback.format_exc())
    if client:
        try:
            client = CustomUser.objects.get(id=client)
            headers = get_serviceTitan_accessToken(client.company.id)
            tagTypes = [
                [str(company.serviceTitanForSaleTagID)],
                [str(company.serviceTitanRecentlySoldTagID)],
                [str(company.serviceTitanForSaleContactedTagID)],
                [str(company.serviceTitanRecentlySoldContactedTagID)],
            ]
            for tag in tagTypes:
                payload = {
                    "customerIds": [str(client.servTitanID)],
                    "tagTypeIds": tag,
                }
                response = requests.delete(
                    f"https://api.servicetitan.io/crm/v2/tenant/{str(client.company.tenantID)}/tags",
                    headers=headers,
                    json=payload,
                )
        except Exception as e:
            logging.error(e)


def update_serviceTitan_tasks(clients, company, status):
    headers, data, response = "", "", ""
    if clients and (
        company.serviceTitanForSaleTagID
        or company.serviceTitanRecentlySoldTagID
    ):
        try:
            headers = get_serviceTitan_accessToken(company.id)
            response = requests.get(
                f"https://api.servicetitan.io/taskmanagement/v2/tenant/{str(company.tenantID)}/data",
                headers=headers,
            )
            with open("tasks.json", "w") as f:
                json.dump(response.json(), f)
            # if response.status_code != 200:
            #     resp = response.json()
            #     error = resp['errors'][''][0]
            #     error = error.replace('(', "").replace(')', "").replace(',', " ").replace(".", "").split()
            #     for word in error:
            #         if word.isdigit():
            #             Client.objects.filter(servTitanID=word).delete()
            #             forSale.remove(word)
            #     payload={'customerIds': forSale, 'taskTypeId': str(company.serviceTitanTaskID)}
            #     response = requests.put(f'https://api.servicetitan.io/crm/v2/tenant/{str(company.tenantID)}/tasks', headers=headers, json=payload)
        except Exception as e:
            logging.error("updating service titan tasks failed")
            logging.error(f"ERROR: {e}")
            logging.error(traceback.format_exc())
    delVariables([headers, data, response, company, status])


# send email to every customuser with the html file that has the same name as the template
def send_update_email(templateName):
    try:
        users = list(
            CustomUser.objects.filter(isVerified=True).values_list(
                "email", flat=True
            )
        )
        mail_subject = "Is My Customer Moving Product Updates"
        messagePlain = "Thank you for signing up for Is My Customer Moving. We have some updates for you. Please visit https://app.ismycustomermoving.com/ to see them."
        message = get_template(f"{templateName}.html").render()
        for user in users:
            send_mail(
                subject=mail_subject,
                message=messagePlain,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user],
                html_message=message,
                fail_silently=False,
            )
    except Exception as e:
        logging.error("sending update email failed")
        logging.error(f"ERROR: {e}")
        logging.error(traceback.format_exc())


@shared_task(rate_limit="1/s")
def doItAll(company):
    try:
        company = Company.objects.get(id=company)
        result = auto_update.delay(
            company_id=company.id
        )  # Schedule auto_update task
        sleep(3600)  # TODO Calculate ETA for update_clients_statuses task
        result = update_clients_statuses(
            company.id
        )  # Schedule update_clients_statuses task
        sleep(360)
        result.then(sendDailyEmail.apply_async, args=[company.id])
    except Exception as e:
        logging.error("doItAll failed")
        logging.error(f"ERROR: {e}")
        logging.error(traceback.format_exc())


def filter_recentlysold(query_params, queryset, company):
    if "saved_filter" in query_params:
        company = Company.objects.get(id=company)
        query_params = SavedFilter.objects.get(
            name=query_params["saved_filter"],
            company=company,
            forExistingClient=False,
        ).savedFilters
        query_params = json.loads(query_params)
        query_params = {k: v for k, v in query_params.items() if v != ""}
    if "min_price" in query_params:
        queryset = queryset.filter(price__gte=query_params["min_price"])
    if "max_price" in query_params:
        queryset = queryset.filter(
            price__lte=query_params["max_price"], price__gt=0
        )
    if "min_year" in query_params:
        queryset = queryset.filter(year_built__gte=query_params["min_year"])
    if "max_year" in query_params:
        queryset = queryset.filter(
            year_built__lte=query_params["max_year"], year_built__gt=0
        )
    if "min_days_ago" in query_params:
        queryset = queryset.filter(
            listed__lt=(
                datetime.today()
                - timedelta(days=int(query_params["min_days_ago"]))
            ).strftime("%Y-%m-%d")
        )
    if "max_days_ago" in query_params:
        queryset = queryset.filter(
            listed__gt=(
                datetime.today()
                - timedelta(days=int(query_params["max_days_ago"]))
            ).strftime("%Y-%m-%d")
        )
    if "tags" in query_params:
        try:
            tags = query_params["tags"].split(",")
        except:
            tags = query_params["tags"]
        if tags != [""]:
            matching_tags = HomeListingTags.objects.filter(tag__in=tags)
            queryset = queryset.filter(tag__in=matching_tags)
    if "state" in query_params:
        queryset = queryset.filter(state=query_params["state"].upper())
    if "city" in query_params:
        queryset = queryset.filter(city=query_params["city"].capitalize())
    if "zip_code" in query_params:
        zipCode = ZipCode.objects.filter(zipCode=query_params["zip_code"])
        if len(zipCode) > 0:
            queryset = queryset.filter(zipCode=zipCode[0])
    return queryset


def filter_clients(query_params, queryset):
    if "min_price" in query_params:
        queryset = queryset.filter(price__gte=query_params["min_price"])
    if "max_price" in query_params:
        queryset = queryset.filter(
            price__lte=query_params["max_price"], price__gt=0
        )
    if "min_year" in query_params:
        queryset = queryset.filter(year_built__gte=query_params["min_year"])
    if "max_year" in query_params:
        queryset = queryset.filter(
            year_built__lte=query_params["max_year"], year_built__gt=0
        )
    if "state" in query_params:
        queryset = queryset.filter(state=query_params["state"].upper())
    if "city" in query_params:
        queryset = queryset.filter(city=query_params["city"].capitalize())
    if "zip_code" in query_params:
        zipCode = ZipCode.objects.filter(zipCode=query_params["zip_code"])
        if len(zipCode) > 0:
            queryset = queryset.filter(zipCode=zipCode[0])
    if "tags" in query_params:
        tags = query_params["tags"].split(",")
        matching_tags = HomeListingTags.objects.filter(tag__in=tags)
        queryset = queryset.filter(tag__in=matching_tags)
    if "status" in query_params:
        statuses = []
        if "For Sale" in query_params["status"]:
            statuses.append("House For Sale")
        if "Recently Sold" in query_params["status"]:
            statuses.append("House Recently Sold (6)")
        queryset = queryset.filter(status__in=statuses)
    if "equip_install_date_min" in query_params:
        queryset = queryset.filter(
            equipmentInstalledDate__gte=query_params["equip_install_date_min"]
        )
    if "equip_install_date_max" in query_params:
        queryset = queryset.filter(
            equipmentInstalledDate__lte=query_params["equip_install_date_max"]
        )
    if "customer_since_min" in query_params:
        start_date = date(int(query_params["customer_since_min"]), 1, 1)
        queryset = queryset.filter(serviceTitanCustomerSince__gte=start_date)
    if "customer_since_max" in query_params:
        end_date = date(int(query_params["customer_since_max"]), 12, 31)
        queryset = queryset.filter(serviceTitanCustomerSince__lte=end_date)
    return queryset


@shared_task
def remove_error_flag():
    old_enough_updates = ClientUpdate.objects.filter(
        error_flag=True, date__lt=datetime.today() - timedelta(days=180)
    )
    for update in old_enough_updates:
        client = update.client
        client.error_flag = False
        client.save()


@shared_task
def verify_address(client_id):
    client = Client.objects.get(id=client_id)
    zip_code = client.zipCode.zipCode
    base_url = "http://production.shippingapis.com/ShippingAPI.dll"
    user_id = settings.USPS_USER_ID
    api = "Verify"

    xml_request = f"""
    <AddressValidateRequest USERID="{user_id}">
        <Address ID="1">
            <Address1></Address1>
            <Address2>{client.address}</Address2>
            <City>{client.city}</City>
            <State>{client.state}</State>
            <Zip5>{zip_code}</Zip5>
            <Zip4/>
        </Address>
    </AddressValidateRequest>
    """

    params = {"API": api, "XML": xml_request}

    response = requests.get(base_url, params=params)
    response_xml = response.text

    parsed_response = ET.fromstring(response_xml)
    address_element = parsed_response.find("Address")
    error = address_element.find("Error")
    if error:
        usps_address = "Error"

    else:
        address2 = address_element.find("Address2").text.title()
        city = address_element.find("City").text.title()
        state = address_element.find("State").text
        zip5 = address_element.find("Zip5").text
        if (
            address2 != client.address
            or state != client.state
            or zip5 != zip_code
        ):
            client.usps_different = True
        usps_address = f"{address2}, {city}, {state} {zip5}"

    client.usps_address = usps_address
    client.save()


@shared_task
def send_zapier_recentlySold(company_id):
    company = Company.objects.get(id=company_id)
    if company.zapier_recentlySold:
        zipCode_objects = Client.objects.filter(company=company).values(
            "zipCode"
        )
        queryset = HomeListing.objects.filter(
            zipCode__in=zipCode_objects,
            listed__gt=(datetime.today() - timedelta(days=7)).strftime(
                "%Y-%m-%d"
            ),
        ).order_by("listed")
        savedFilters = SavedFilter.objects.filter(
            company=company, forExistingClient=False, forZapier=True
        )
        for savedFilter in savedFilters:
            query_params = json.loads(savedFilter.savedFilters)
            query_params = {k: v for k, v in query_params.items() if v != ""}
            queryset = filter_recentlysold(query_params, queryset, company_id)
            if len(queryset) > 0:
                try:
                    if len(queryset) == 1:
                        serializer = HomeListingSerializer(queryset[0])
                        serialized_data = serializer.data
                        serialized_data["filter_name"] = savedFilter.name
                    else:
                        serializer = HomeListingSerializer(queryset, many=True)
                        serialized_data = serializer.data
                        for (
                            data
                        ) in (
                            serialized_data
                        ):  # Add savedFilter.name to each item in the list
                            data["filterName"] = savedFilter.name
                    requests.post(
                        company.zapier_recentlySold, data=serialized_data
                    )
                except Exception as e:
                    logging.error(e)
