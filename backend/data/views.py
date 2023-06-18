from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

import datetime
import logging
import json
import requests

from accounts.models import CustomUser, Company
from accounts.serializers import UserSerializerWithToken
from config import settings
from .models import Client, ClientUpdate, HomeListing, Task, SavedFilter
from .serializers import ClientListSerializer, HomeListingSerializer
from .syncClients import get_salesforce_clients, get_serviceTitan_clients
from .realtor import getAllZipcodes
from .utils import (
    saveClientList,
    add_serviceTitan_contacted_tag,
    filter_recentlysold,
    filter_clients,
    remove_all_serviceTitan_tags,
)

from django.http import HttpResponse
import csv


# Create your views here.
class DownloadClientView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user, format=None):
        queryset = self.get_queryset(user)
        # Define the CSV header row
        header = [
            "name",
            "address",
            "city",
            "state",
            "zipCode",
            "status",
            "phoneNumber",
        ]
        # Create a response object with the CSV content
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="clients.csv"'
        # Create a CSV writer object
        writer = csv.writer(response)
        # Write the header row to the CSV file
        writer.writerow(header)
        # Write the data rows to the CSV file
        for client in queryset:
            row = [
                client.name,
                client.address,
                client.city,
                client.state,
                client.zipCode.zipCode,
                client.status,
                client.phoneNumber,
            ]
            writer.writerow(row)
        # Return the response
        return response

    def get_queryset(self, user):
        query_params = self.request.query_params
        user = CustomUser.objects.get(id=user)
        queryset = Client.objects.filter(
            company=user.company, active=True
        ).order_by("status")
        return filter_clients(query_params, queryset)


class CustomPagination(PageNumberPagination):
    page_size = 1000


class ClientListView(generics.ListAPIView):
    serializer_class = ClientListSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = CustomUser.objects.get(id=self.kwargs["user"])
        query_params = self.request.query_params

        # Initialize the queryset with the base filters
        queryset = Client.objects.prefetch_related(
            "clientUpdates_client"
        ).filter(company=user.company, active=True)

        queryset = filter_clients(query_params, queryset)
        # TODO
        # if 'tags' in query_params:
        #     tags = [tag.replace('[', '').replace(']', '').replace(' ', '_') for tag in query_params.get('tags', '').split(',')]
        #     queryset = queryset.filter(tag__tag__in=tags)
        try:
            if user.company.product.id == "price_1MhxfPAkLES5P4qQbu8O45xy":
                queryset = queryset.order_by("name")
            elif user.status == "admin":
                queryset = queryset.order_by("status")
            else:
                queryset = queryset.exclude(status="No Change").order_by(
                    "status"
                )
        except:
            queryset = queryset.order_by("status")
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        user = CustomUser.objects.get(id=self.kwargs["user"])
        allClients = Client.objects.filter(company=user.company, active=True)
        forSale = allClients.filter(
            status="House For Sale", contacted=False
        ).count()
        recentlySold = allClients.filter(
            status="House Recently Sold (6)", contacted=False
        ).count()
        allClientUpdates = ClientUpdate.objects.filter(
            client__company=user.company
        )
        forSaleAllTime = allClientUpdates.filter(
            status="House For Sale"
        ).count()
        recentlySoldAllTime = allClientUpdates.filter(
            status="House Recently Sold (6)"
        ).count()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            clients = serializer.data
            return self.get_paginated_response(
                {
                    "forSale": forSale,
                    "forSaleAllTime": forSaleAllTime,
                    "recentlySoldAllTime": recentlySoldAllTime,
                    "recentlySold": recentlySold,
                    "clients": clients,
                }
            )

        serializer = self.get_serializer(queryset, many=True)
        clients = serializer.data
        return Response(
            {
                "forSale": forSale,
                "forSaleAllTime": forSaleAllTime,
                "recentlySoldAllTime": recentlySoldAllTime,
                "recentlySold": recentlySold,
                "clients": clients,
            }
        )


class RecentlySoldView(generics.ListAPIView):
    serializer_class = HomeListingSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query_params = self.request.query_params
        company = Company.objects.get(id=self.kwargs["company"])
        if company.recentlySoldPurchased:
            zipCode_objects = Client.objects.filter(company=company).values(
                "zipCode"
            )
            queryset = HomeListing.objects.filter(
                zipCode__in=zipCode_objects,
                status="House Recently Sold (6)",
                listed__gt=(
                    datetime.datetime.today() - datetime.timedelta(days=30)
                ).strftime("%Y-%m-%d"),
            ).order_by("listed")
            return filter_recentlysold(query_params, queryset, company.id)

        else:
            return HomeListing.objects.none()

    def get(self, request, company, format=None):
        queryset = self.get_queryset()
        savedFilters = list(
            SavedFilter.objects.filter(
                company=company, forExistingClient=False
            ).values_list("name", flat=True)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            recentlySold = serializer.data
            return self.get_paginated_response(
                {"data": recentlySold, "savedFilters": savedFilters}
            )

        serializer = self.get_serializer(queryset, many=True)
        recentlySold = serializer.data
        return Response({"data": recentlySold, "savedFilters": savedFilters})

    def post(self, request, company, format=None):
        data = request.data
        company = Company.objects.get(id=company)

        filterName = data["filterName"]

        if SavedFilter.objects.filter(
            name=filterName, company=company, forExistingClient=True
        ).exists():
            return Response(
                {"error": "A filter with that name already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            filters = {
                "min_price": data["minPrice"],
                "max_price": data["maxPrice"],
                "min_year": data["minYear"],
                "max_year": data["maxYear"],
                "min_days_ago": data["minDaysAgo"],
                "max_days_ago": data["maxDaysAgo"],
                "tags": data["tagFilters"],
                "city": data["city"],
                "state": data["state"],
                "zip_code": data["zipCode"],
            }

            forZapier = data["forZapier"]
            SavedFilter.objects.create(
                name=filterName,
                company=company,
                savedFilters=json.dumps(filters),
                forZapier=forZapier,
            )
            return Response(
                {"success": "Filter created successfully"},
                status=status.HTTP_200_OK,
            )

    def delete(self, request, company, format=None):
        data = request.data
        filterName = data["filterName"]
        company = Company.objects.get(id=company)
        SavedFilter.objects.filter(name=filterName, company=company).delete()
        return Response(
            {"success": "Filter deleted successfully"},
            status=status.HTTP_200_OK,
        )

    class Meta:
        unique_together = ("name", "company")


class AllRecentlySoldView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, company, format=None):
        queryset = self.get_queryset(company)
        # Define the CSV header row
        header = [
            "address",
            "city",
            "state",
            "zipCode",
            "Listing Price",
            "Year Built",
        ]
        # Create a response object with the CSV content
        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="HomeListings.csv"'
        # Create a CSV writer object
        writer = csv.writer(response)
        # Write the header row to the CSV file
        writer.writerow(header)
        # Write the data rows to the CSV file
        for homeListing in queryset:
            row = [
                homeListing.address,
                homeListing.city,
                homeListing.state,
                homeListing.zipCode.zipCode,
                homeListing.price,
                homeListing.year_built,
            ]
            writer.writerow(row)
        # Return the response
        return response

    def get_queryset(self, company):
        query_params = self.request.query_params
        company = Company.objects.get(id=company)
        if company.recentlySoldPurchased:
            zipCode_objects = Client.objects.filter(company=company).values(
                "zipCode"
            )
            queryset = HomeListing.objects.filter(
                zipCode__in=zipCode_objects,
                listed__gt=(
                    datetime.datetime.today() - datetime.timedelta(days=30)
                ).strftime("%Y-%m-%d"),
            ).order_by("listed")
            return filter_recentlysold(query_params, queryset)

        else:
            return HomeListing.objects.none()


class UpdateStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            getAllZipcodes.delay(self.kwargs["company"])
        except Exception as e:
            logging.error(f"ERROR: Update Status View: {e}")
        return Response("", status=status.HTTP_201_CREATED, headers="")


class UploadFileView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            try:
                task = Task.objects.get(id=self.kwargs["company"])
                if task.completed:
                    deleted = task.deletedClients
                    # task.delete()
                    return Response(
                        {
                            "status": "SUCCESS",
                            "data": "Clients Uploaded! Come back in about an hour to see your results.",
                            "deleted": deleted,
                        },
                        status=status.HTTP_201_CREATED,
                        headers="",
                    )
                else:
                    return Response(
                        {"status": "UNFINISHED", "clients": []},
                        status=status.HTTP_201_CREATED,
                    )
            except Exception as e:
                logging.error(e)
                return Response(
                    {"status": "Task Error"}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logging.error(e)
            return Response(
                {"status": "error"}, status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request, *args, **kwargs):
        company_id = self.kwargs["company"]
        try:
            company = Company.objects.get(id=company_id)
        except Exception as e:
            logging.error(e)
            return Response(
                {"status": "Company Error"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            task = Task.objects.create()
            saveClientList.delay(request.data, company_id, task=task.id)
        except Exception as e:
            logging.error(e)
            return Response(
                {"status": "File Error"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                "data": "Clients Uploaded! Come back in about an hour to see your results",
                "task": task.id,
            },
            status=status.HTTP_201_CREATED,
            headers="",
        )


# create a class for update client that will be used for the put and delete requests
class UpdateClientView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        try:
            if request.data["type"] == "delete":
                if len(request.data["clients"]) == 1:
                    client = Client.objects.get(id=request.data["clients"][0])
                    client.delete()
                else:
                    for client in request.data["clients"]:
                        client = Client.objects.get(id=client)
                        client.delete()
                return Response(
                    {"status": "Client Deleted"},
                    status=status.HTTP_201_CREATED,
                    headers="",
                )
            else:
                client = Client.objects.get(id=request.data["clients"])
                if request.data["note"]:
                    client.note = request.data["note"]
                    ClientUpdate.objects.create(
                        client=client, note=request.data["note"]
                    )
                if request.data["contacted"] != "":
                    client.contacted = request.data["contacted"]
                    ClientUpdate.objects.create(
                        client=client, contacted=request.data["contacted"]
                    )
                    if request.data["contacted"] and client.servTitanID:
                        if (
                            client.status == "House For Sale"
                            and client.company.serviceTitanForSaleContactedTagID
                        ):
                            add_serviceTitan_contacted_tag.delay(
                                client.id,
                                client.company.serviceTitanForSaleContactedTagID,
                            )
                        elif (
                            client.status == "House Recently Sold (6)"
                            and client.company.serviceTitanRecentlySoldContactedTagID
                        ):
                            add_serviceTitan_contacted_tag.delay(
                                client.id,
                                client.company.serviceTitanRecentlySoldContactedTagID,
                            )
                if request.data["errorFlag"] != "":
                    client.status = "No Change"
                    client.error_flag = request.data["errorFlag"]
                    ClientUpdate.objects.create(
                        client=client, error_flag=request.data["errorFlag"]
                    )
                    if client.servTitanID:
                        remove_all_serviceTitan_tags.delay(client=client.id)
                if request.data["latitude"] != "":
                    client.latitude = request.data["latitude"]
                if request.data["longitude"] != "":
                    client.longitude = request.data["longitude"]
                client.save()
                return Response(
                    {"status": "Client Updated"},
                    status=status.HTTP_201_CREATED,
                    headers="",
                )
        except Exception as e:
            logging.error(e)
            return Response(
                {"status": "Data Error"}, status=status.HTTP_400_BAD_REQUEST
            )


class ServiceTitanView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            try:
                task = Task.objects.get(id=self.kwargs["company"])
                if task.completed:
                    deleted = task.deletedClients
                    task.delete()
                    return Response(
                        {
                            "status": "SUCCESS",
                            "data": "Clients Synced! Come back in about an hour to see your results.",
                            "deleted": deleted,
                        },
                        status=status.HTTP_201_CREATED,
                        headers="",
                    )
                else:
                    # clients = Company.objects.get(id="faee8ca7-e5de-4c60-8578-0ac6bc576930").client_set.all()
                    # if clients.count() > 0:
                    #     return Response({"status": "UNFINISHED", "clients": ClientListSerializer(clients[:1000], many=True).data}, status=status.HTTP_201_CREATED)
                    return Response(
                        {"status": "UNFINISHED", "clients": []},
                        status=status.HTTP_201_CREATED,
                    )
            except Exception as e:
                logging.error(e)
                return Response(
                    {"status": "Task Error"}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logging.error(e)
            return Response(
                {"status": "error"}, status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request, *args, **kwargs):
        try:
            company_id = self.kwargs["company"]
            option = request.data["option"]
            try:
                Company.objects.get(id=company_id)
                task = Task.objects.create()
                get_serviceTitan_clients.delay(company_id, task.id, option)
                return Response(
                    {"status": "Success", "task": task.id},
                    status=status.HTTP_201_CREATED,
                    headers="",
                )
            except Exception as e:
                logging.error(e)
                return Response(
                    {"status": "Company Error"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            logging.error(e)
            return Response(
                {"status": "error"}, status=status.HTTP_400_BAD_REQUEST
            )


class SalesforceConsumerView(APIView):
    # GET request that returns the Salesforce Consumer Key and Consumer Secret from the config file, make this protected
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            return Response(
                {
                    "consumer_key": settings.SALESFORCE_CONSUMER_KEY,
                    "consumer_secret": settings.SALESFORCE_CONSUMER_SECRET,
                },
                status=status.HTTP_201_CREATED,
                headers="",
            )
        except Exception as e:
            logging.error(e)
            return Response(
                {"status": "error"}, status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request, *args, **kwargs):
        try:
            company_id = self.kwargs["company"]
            try:
                company = Company.objects.get(id=company_id)
                company.crm = "Salesforce"
                code = request.data["code"]
                headers = {
                    "Content-type": "application/x-www-form-urlencoded",
                }

                # Make the request
                response = requests.post(
                    f"https://login.salesforce.com/services/oauth2/token?grant_type=authorization_code&client_id={settings.SALESFORCE_CONSUMER_KEY}&client_secret={settings.SALESFORCE_CONSUMER_SECRET}&redirect_uri=http://localhost:3000/dashboard/settings&code={code}",
                    headers=headers,
                )

                # Parse the response
                response_data = response.json()
                new_access_token = response_data["access_token"]
                new_refresh_token = response_data["refresh_token"]
                company.sfAccessToken = new_access_token
                company.sfRefreshToken = new_refresh_token
                company.save()
                user = CustomUser.objects.get(id=request.data["id"])
                serializer = UserSerializerWithToken(user, many=False)
                return Response(serializer.data)
            except Exception as e:
                logging.error(e)
                return Response(
                    {"status": "Company Error"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            logging.error(e)
            return Response(
                {"status": "error"}, status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request, *args, **kwargs):
        try:
            company_id = self.kwargs["company"]

            try:
                get_salesforce_clients(company_id)
                return Response(
                    {"status": "Success"},
                    status=status.HTTP_201_CREATED,
                    headers="",
                )
            except Exception as e:
                logging.error(e)
                return Response(
                    {"status": "Company Error"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            logging.error(e)
            return Response(
                {"status": "error"}, status=status.HTTP_400_BAD_REQUEST
            )
