from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from datetime import datetime, timedelta
import logging
import json
import csv

# from accounts.serializers import UserSerializerWithToken
from accounts.models import Company, CustomUser
from config import settings
from payments.models import ServiceTitanInvoice
from .models import Client, ClientUpdate, HomeListing, Task, SavedFilter
from .serializers import ClientListSerializer, HomeListingSerializer
from .syncClients import get_salesforce_clients, complete_service_titan_sync
from .realtor import get_all_zipcodes
from .utils import (
    save_client_list,
    add_service_titan_contacted_tag,
    filter_home_listings,
    filter_clients,
    remove_all_service_titan_tags,
)


# Create your views here.
class DownloadClientView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        queryset = self.get_queryset()
        header = [
            "name",
            "address",
            "city",
            "state",
            "zip_code",
            "status",
            "phone_number",
        ]
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="clients.csv"'
        writer = csv.writer(response)
        writer.writerow(header)

        for client in queryset:
            row = [
                client.name,
                client.address,
                client.city,
                client.state,
                client.zip_code.zip_code,
                client.status,
                client.phone_number,
            ]
            writer.writerow(row)
        return response

    def get_queryset(self):
        query_params = self.request.query_params
        user = self.request.user
        queryset = Client.objects.filter(
            company=user.company, active=True
        ).order_by("status")
        return filter_clients(query_params, queryset, user.company.id)


class CustomPagination(PageNumberPagination):
    page_size = 1000


class ClientListView(generics.ListAPIView):
    serializer_class = ClientListSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        query_params = self.request.query_params
        queryset = Client.objects.prefetch_related(
            "client_updates_client"
        ).filter(company=user.company, active=True)
        queryset = filter_clients(query_params, queryset, user.company.id)
        # TODO
        # if "tags" in query_params:
        #     tags = [
        #         tag.replace("[", "").replace("]", "").replace(" ", "_")
        #         for tag in query_params.get("tags", "").split(",")
        #     ]
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
        except Exception as e:
            logging.error(e)
            queryset = queryset.order_by("status")
        return queryset

    def list(self, request, *args, **kwargs):
        user = self.request.user
        if "newAddress" in request.query_params:
            clients = Client.objects.filter(
                company=user.company, active=True
            ).exclude(new_address=None)
            serializer = self.get_serializer(clients, many=True)
            clients = serializer.data
            return Response({"clients": clients}, status=status.HTTP_200_OK)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            user = self.request.user
            allClients = Client.objects.filter(
                company=user.company, active=True)
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
            savedFilters = list(
                SavedFilter.objects.filter(
                    company=user.company, filter_type="Client"
                ).values_list("name", flat=True)
            )

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
                        "savedFilters": savedFilters,
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
                },
                status=status.HTTP_200_OK,
            )

    def post(self, request, format=None):
        try:
            data = request.data
            company = self.request.user.company

            filterName = data["filter_name"]

            if SavedFilter.objects.filter(
                name=filterName, company=company, filter_type="Client"
            ).exists():
                return Response(
                    {"error": "A filter with that name already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                filters = {
                    "min_price": data["min_price"],
                    "max_price": data["max_price"],
                    "min_year": data["min_year"],
                    "max_year": data["max_year"],
                    "min_beds": data["min_beds"],
                    "max_beds": data["max_beds"],
                    "min_baths": data["min_baths"],
                    "max_baths": data["max_baths"],
                    "min_sqft": data["min_sqft"],
                    "max_sqft": data["max_sqft"],
                    "min_lot_sqft": data["min_lot_sqft"],
                    "max_lot_sqft": data["max_lot_sqft"],
                    "equip_install_date_min": data["equip_install_date_min"],
                    "equip_install_date_max": data["equip_install_date_max"],
                    "tags": data["tag_filters"],
                    "city": data["city"],
                    "state": data["state"],
                    "zip_code": data["zip_code"],
                    "customer_since_min": data["customer_since_min"],
                    "customer_since_max": data["customer_since_max"],
                    "status": data["status_filters"],
                    "usps_changed": data["usps_changed"],

                }

                forZapier = data["for_zapier"]
                SavedFilter.objects.create(
                    name=filterName,
                    company=company,
                    saved_filters=json.dumps(filters),
                    for_zapier=forZapier,
                    filter_type="Client",
                )
                return Response(
                    {"success": "Filter created successfully"},
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            logging.error(e)
            return Response(
                {"error": "Something went wrong"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RecentlySoldView(generics.ListAPIView):
    serializer_class = HomeListingSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query_params = self.request.query_params
        company = self.request.user.company
        if company.recently_sold_purchased:
            zip_code_objects = Client.objects.filter(company=company).values(
                "zip_code"
            )
            queryset = HomeListing.objects.filter(
                zip_code__in=zip_code_objects,
                status="House Recently Sold (6)",
                listed__gt=(
                    datetime.today() - timedelta(days=30)
                ).strftime("%Y-%m-%d"),
            ).order_by("-listed")
            return filter_home_listings(
                query_params, queryset, company.id, "Recently Sold"
            )
        else:
            return HomeListing.objects.none()

    def get(self, request, format=None):
        queryset = self.get_queryset()
        company = self.request.user.company
        savedFilters = list(
            SavedFilter.objects.filter(
                company=company, filter_type="Recently Sold"
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

    def post(self, request, format=None):
        try:
            data = request.data
            company = self.request.user.company

            filterName = data["filter_name"]

            if SavedFilter.objects.filter(
                name=filterName, company=company, filter_type="Recently Sold"
            ).exists():
                return Response(
                    {"error": "A filter with that name already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                filters = {
                    "min_price": data["min_price"],
                    "max_price": data["max_price"],
                    "min_year": data["min_year"],
                    "max_year": data["max_year"],
                    "min_days_ago": data["min_days_ago"],
                    "max_days_ago": data["max_days_ago"],
                    "min_beds": data["min_beds"],
                    "max_beds": data["max_beds"],
                    "min_baths": data["min_baths"],
                    "max_baths": data["max_baths"],
                    "min_sqft": data["min_sqft"],
                    "max_sqft": data["max_sqft"],
                    "min_lot_sqft": data["min_lot_sqft"],
                    "max_lot_sqft": data["max_lot_sqft"],
                    "tags": data["tag_filters"],
                    "city": data["city"],
                    "state": data["state"],
                    "zip_code": data["zip_code"],
                }

                forZapier = data["for_zapier"]
                SavedFilter.objects.create(
                    name=filterName,
                    company=company,
                    saved_filters=json.dumps(filters),
                    for_zapier=forZapier,
                    filter_type="Recently Sold",
                )
                return Response(
                    {"success": "Filter created successfully"},
                    status=status.HTTP_200_OK,
                )
        except KeyError:
            return Response(
                {"Error": "Request body did not include correct information"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, format=None, **kwargs):
        filter_name = kwargs["filter"]
        try:
            filter = SavedFilter.objects.get(
                name=filter_name, company=request.user.company
            )
            filter.delete()
        except ObjectDoesNotExist:
            return Response(
                {"Error": "Filter and company combination does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"success": "Filter deleted successfully"},
            status=status.HTTP_200_OK,
        )

    class Meta:
        unique_together = ("name", "company")


class AllRecentlySoldView(generics.ListAPIView):
    """
    An API view that allows users to download all recently sold home listings
    as a CSV file.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        queryset = self.get_queryset()
        header = [
            "address",
            "city",
            "state",
            "zip_code",
            "listing_price",
            "year_built",
        ]
        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="HomeListings.csv"'
        writer = csv.writer(response)
        writer.writerow(header)

        for home_listing in queryset:
            row = [
                home_listing.address,
                home_listing.city,
                home_listing.state,
                home_listing.zip_code.zip_code,
                home_listing.price,
                home_listing.year_built,
            ]
            writer.writerow(row)
        return response

    def get_queryset(self):
        query_params = self.request.query_params
        company = self.request.user.company
        if company.recently_sold_purchased:
            zip_code_objects = Client.objects.filter(
                company=company, active=True
            ).values("zip_code")
            queryset = HomeListing.objects.filter(
                zip_code__in=zip_code_objects,
                status="House Recently Sold (6)",
                listed__gt=(
                    datetime.today() - timedelta(days=30)
                ).strftime("%Y-%m-%d"),
            ).order_by("-listed")
            return filter_home_listings(
                query_params, queryset, company.id, "Recently Sold"
            )
        else:
            return HomeListing.objects.none()


class ForSaleView(generics.ListAPIView):
    serializer_class = HomeListingSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query_params = self.request.query_params
        company = self.request.user.company
        if company.for_sale_purchased:
            zip_code_objects = Client.objects.filter(company=company).values(
                "zip_code"
            )
            queryset = HomeListing.objects.filter(
                zip_code__in=zip_code_objects,
                status="House For Sale",
                listed__gt=(
                    datetime.today() - timedelta(days=30)
                ).strftime("%Y-%m-%d"),
            ).order_by("-listed")
            return filter_home_listings(
                query_params, queryset, company.id, "For Sale"
            )
        else:
            return HomeListing.objects.none()

    def get(self, request, format=None):
        queryset = self.get_queryset()
        company = self.request.user.company
        savedFilters = list(
            SavedFilter.objects.filter(
                company=company, filter_type="For Sale"
            ).values_list("name", flat=True)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            forSale = serializer.data
            return self.get_paginated_response(
                {"data": forSale, "savedFilters": savedFilters}
            )

        serializer = self.get_serializer(queryset, many=True)
        forSale = serializer.data
        return Response({"data": forSale, "savedFilters": savedFilters})

    def post(self, request, format=None):
        try:
            data = request.data
            company = self.request.user.company

            filterName = data["filter_name"]

            if SavedFilter.objects.filter(
                name=filterName, company=company, filter_type="For Sale"
            ).exists():
                return Response(
                    {"error": "A filter with that name already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                filters = {
                    "min_price": data["min_price"],
                    "max_price": data["max_price"],
                    "min_year": data["min_year"],
                    "max_year": data["max_year"],
                    "min_days_ago": data["min_days_ago"],
                    "max_days_ago": data["max_days_ago"],
                    "min_beds": data["min_beds"],
                    "max_beds": data["max_beds"],
                    "min_baths": data["min_baths"],
                    "max_baths": data["max_baths"],
                    "min_sqft": data["min_sqft"],
                    "max_sqft": data["max_sqft"],
                    "min_lot_sqft": data["min_lot_sqft"],
                    "max_lot_sqft": data["max_lot_sqft"],
                    "tags": data["tag_filters"],
                    "city": data["city"],
                    "state": data["state"],
                    "zip_code": data["zip_code"],
                }

                forZapier = data["for_zapier"]
                SavedFilter.objects.create(
                    name=filterName,
                    company=company,
                    saved_filters=json.dumps(filters),
                    for_zapier=forZapier,
                    filter_type="For Sale",
                )
                return Response(
                    {"success": "Filter created successfully"},
                    status=status.HTTP_200_OK,
                )
        except KeyError:
            return Response(
                {"Error": "Request body did not include correct information"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, format=None, **kwargs):
        filter_name = kwargs["filter"]
        try:
            filter = SavedFilter.objects.get(
                name=filter_name, company=request.user.company
            )
            filter.delete()
        except ObjectDoesNotExist:
            return Response(
                {"Error": "Filter and company combination does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"success": "Filter deleted successfully"},
            status=status.HTTP_200_OK,
        )

    class Meta:
        unique_together = ("name", "company")


class AllForSaleView(generics.ListAPIView):
    """
    An API view that allows users to download all for sale home listings
    as a CSV file.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        queryset = self.get_queryset()
        header = [
            "address",
            "city",
            "state",
            "zip_code",
            "listing_price",
            "year_built",
        ]
        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="HomeListings.csv"'
        writer = csv.writer(response)
        writer.writerow(header)

        for home_listing in queryset:
            row = [
                home_listing.address,
                home_listing.city,
                home_listing.state,
                home_listing.zip_code.zip_code,
                home_listing.price,
                home_listing.year_built,
            ]
            writer.writerow(row)
        return response

    def get_queryset(self):
        query_params = self.request.query_params
        company = self.request.user.company
        if company.for_sale_purchased:
            zip_code_objects = Client.objects.filter(
                company=company, active=True
            ).values("zip_code")
            queryset = HomeListing.objects.filter(
                zip_code__in=zip_code_objects,
                status="House For Sale",
                listed__gt=(
                    datetime.today() - timedelta(days=30)
                ).strftime("%Y-%m-%d"),
            ).order_by("-listed")
            return filter_home_listings(
                query_params, queryset, company.id, "For Sale"
            )
        else:
            return HomeListing.objects.none()


class UpdateStatusView(APIView):
    """
    An API view to trigger the process to update the status of home listings.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            company = self.request.user.company
            get_all_zipcodes.delay(company.id)
        except Exception as e:
            logging.error(f"ERROR: Update Status View: {e}")
            return Response(
                "ERROR: Invalid Company ID",
                status=status.HTTP_400_BAD_REQUEST,
                headers="",
            )
        return Response("", status=status.HTTP_200_OK, headers="")


class UploadFileView(generics.ListAPIView):
    """
    An API view to upload a list of clients and track the task status.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            try:
                task = Task.objects.get(id=kwargs["task"])
                if task.completed:
                    deleted = task.deleted_clients
                    # task.delete()
                    return Response(
                        {
                            "status": "SUCCESS",
                            "data": """Clients Uploaded!
                            Come back in about an hour to see your results.""",
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
                    {"status": "Task Error"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            logging.error(e)
            return Response(
                {"status": "error"}, status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request, *args, **kwargs):
        try:
            task = Task.objects.create()
            save_client_list.delay(
                request.data, self.request.user.company.id, task=task.id
            )
        except Exception as e:
            logging.error(e)
            return Response({"status": e}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "data": """Clients Uploaded!
                Come back in about an hour to see your results""",
                "task": task.id,
            },
            status=status.HTTP_201_CREATED,
            headers="",
        )


# create a class for update client that will be used for the put and delete requests
class UpdateClientView(APIView):
    """
    An API view to handle client updates or deletions.
    """

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
                    if request.data["contacted"] and client.serv_titan_id:
                        if (
                            client.status == "House For Sale"
                            and client.serv_titan_id  # noqa
                            and client.company.service_titan_for_sale_contacted_tag_id  # noqa
                        ):
                            add_service_titan_contacted_tag.delay(
                                client.id,
                                client.company.service_titan_for_sale_contacted_tag_id,  # noqa
                            )
                        elif (
                            client.status == "House Recently Sold (6)"
                            and client.serv_titan_id  # noqa
                            and client.company.service_titan_recently_sold_contacted_tag_id  # noqa
                        ):
                            add_service_titan_contacted_tag.delay(
                                client.id,
                                client.company.service_titan_recently_sold_contacted_tag_id,  # noqa
                            )
                if request.data["errorFlag"] != "":
                    client.status = "No Change"
                    client.error_flag = request.data["errorFlag"]
                    ClientUpdate.objects.create(
                        client=client, error_flag=request.data["errorFlag"]
                    )
                    if client.serv_titan_id:
                        remove_all_service_titan_tags.delay(client=client.id)
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
    """
    An API view to handle the process related to ServiceTitan clients.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            try:
                task = Task.objects.get(id=kwargs["task"])
                if task.completed:
                    deleted = task.deleted_clients
                    task.delete()
                    return Response(
                        {
                            "status": "SUCCESS",
                            "data": """Clients Synced!
                                Come back in about an hour to see your results.""",
                            "deleted": deleted,
                        },
                        status=status.HTTP_201_CREATED,
                        headers="",
                    )
                else:
                    # clients = Company.objects.get(
                    #     id="faee8ca7-e5de-4c60-8578-0ac6bc576930"
                    # ).client_set.all()
                    # if clients.count() > 0:
                    #     return Response(
                    #         {
                    #             "status": "UNFINISHED",
                    #             "clients": ClientListSerializer(
                    #                 clients[:1000], many=True
                    #             ).data,
                    #         },
                    #         status=status.HTTP_201_CREATED,
                    #     )
                    return Response(
                        {"status": "UNFINISHED", "clients": []},
                        status=status.HTTP_201_CREATED,
                    )
            except Exception as e:
                logging.error(e)
                return Response(
                    {"status": "Task Error"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            logging.error(e)
            return Response(
                {"status": "error"}, status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request, *args, **kwargs):
        company_id = self.request.user.company.id
        option = request.data.get("option", "")
        try:
            task = Task.objects.create()
            complete_service_titan_sync.delay(company_id, task.id, option)
            return Response(
                {"status": "Success", "task": task.id},
                status=status.HTTP_201_CREATED,
                headers="",
            )
        except Exception as e:
            logging.error(e)
            return Response(
                {"status": "error"}, status=status.HTTP_400_BAD_REQUEST
            )


class SalesforceView(APIView):
    """
    An API view to handle interactions with Salesforce, including
    retrieving consumer keys and handling post requests.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            return Response(
                {
                    "consumer_key": settings.SALESFORCE_CONSUMER_KEY,
                    "consumer_secret": settings.SALESFORCE_CONSUMER_SECRET,
                },
                status=status.HTTP_200_OK,
                headers="",
            )
        except Exception as e:
            logging.error(e)
            return Response(
                {"status": "error"}, status=status.HTTP_400_BAD_REQUEST
            )

    # def post(self, *args, **kwargs):
    #     company_id = self.request.user.company.id
    #     try:
    #         company = Company.objects.get(id=company_id)
    #     except Company.DoesNotExist:
    #         logging.error(f"Company with id {company_id} does not exist.")
    #         return Response(
    #             {"status": "Company Error"},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )

    #     company.crm = "Salesforce"
    #     # code = request.data.get("code", "")
    #     # headers = {
    #     #     "Content-type": "application/x-www-form-urlencoded",
    #     # }

    def put(self, *args, **kwargs):
        company_id = self.request.user.company.id
        try:
            get_salesforce_clients.delay(company_id)
            return Response(
                {"status": "Success"},
                status=status.HTTP_200_OK,
                headers="",
            )
        except Exception as e:
            logging.error(e)
            return Response(
                {"status": "error"}, status=status.HTTP_400_BAD_REQUEST
            )


class CompanyDashboardView(APIView):
    """
    An API view to get the revenue and leads data for a company.
    It should be separated by month and the leads should be separated
    by status.
    """
    permission_classes = [IsAuthenticated]

    def _get_months_active(self, company_id):
        """
        Return the number of months a company has been active.
        """
        company = Company.objects.get(id=company_id)
        first_client = CustomUser.objects.filter(
            company=company).order_by("date_joined")[0]
        first_month = first_client.date_joined.month
        first_year = first_client.date_joined.year

        current_month = datetime.now().month
        current_year = datetime.now().year

        self.months_active = (current_year - first_year) * 12 + \
            (current_month - first_month) + 1

    def _get_month_dictionary(self):
        current_datetime = datetime.now()

        # Create a dictionary to store the last 6 months
        last_six_months_dict = {}

        # Loop to generate the keys for the last 6 months
        for i in range(6):
            # Calculate the first day of the current month
            first_day_of_current_month = current_datetime.replace(day=1)

            # Calculate the last day of the previous month
            last_day_of_last_month = first_day_of_current_month - \
                timedelta(days=1)

            # Calculate the first day of the previous month
            first_day_of_last_month = last_day_of_last_month.replace(day=1)

            # Get the name of the previous month as a string (full month name)
            previous_month_name = first_day_of_last_month.strftime("%B")

            # Add the key-value pair to the dictionary
            last_six_months_dict[previous_month_name] = 0

            # Move to the previous month for the next iteration
            current_datetime = first_day_of_last_month

        return last_six_months_dict

    def _get_leads(self, company_id):
        """
        Return a list of all the for sale
        leads for a company separated by each month.
        """
        self.recently_sold_by_month = self._get_month_dictionary()
        self.for_sale_by_month = self._get_month_dictionary()
        company = Company.objects.get(id=company_id)
        clients = Client.objects.filter(company=company)
        statuses = [
            "House For Sale",
            "House Recently Sold (6)",
        ]
        for listed_status in statuses:
            client_updates = ClientUpdate.objects.filter(
                client__in=clients, status=listed_status)
            today = datetime.today()
            first_day_of_month = today.replace(day=1)

            for i in range(6):
                last_day_of_month = first_day_of_month - timedelta(days=1)
                first_day_of_month = last_day_of_month.replace(day=1)

                # Query to get invoices that happened last month
                status_updates_last_month = client_updates.filter(
                    date__gte=first_day_of_month,
                    date__lte=last_day_of_month
                ).count()
                if listed_status == "House For Sale":
                    self.for_sale_by_month[last_day_of_month.strftime(
                        "%B")] = status_updates_last_month
                else:
                    self.recently_sold_by_month[last_day_of_month.strftime(
                        "%B")] = status_updates_last_month

    def _get_revenue(self, company_id):
        """
        Return a list of all the attributed revenue
        for a company separated by each month.
        """
        self.revenue_by_month = self._get_month_dictionary()
        company = Company.objects.get(id=company_id)
        clients = Client.objects.filter(company=company)
        invoices = ServiceTitanInvoice.objects.filter(
            client__in=clients, attributed=True)
        invoice_amounts = invoices.values_list("amount", flat=True)
        self.total_revenue = int(sum(invoice_amounts))

        today = datetime.today()
        first_day_of_month = today.replace(day=1)

        for i in range(6):
            last_day_of_month = first_day_of_month - timedelta(days=1)
            first_day_of_month = last_day_of_month.replace(day=1)

            # Query to get invoices that happened last month
            invoices_last_month = ServiceTitanInvoice.objects.filter(
                created_on__gte=first_day_of_month,
                created_on__lte=last_day_of_month,
                attributed=True
            ).values_list("amount", flat=True)
            self.revenue_by_month[last_day_of_month.strftime("%B")] = sum(
                invoices_last_month)

    def get(self, *args, **kwargs):
        company_id = self.request.user.company.id
        try:
            self._get_month_dictionary()
            self._get_revenue(company_id)
            self._get_months_active(company_id)
            self._get_leads(company_id)
            return Response(
                {
                    "totalRevenue": self.total_revenue,
                    "monthsActive": self.months_active,
                    "revenueByMonth": self.revenue_by_month,
                    "forSaleByMonth": self.for_sale_by_month,
                    "recentlySoldByMonth": self.recently_sold_by_month
                },
                status=status.HTTP_200_OK,
                headers="",
            )
        except Exception as e:
            logging.error(e)
            return Response(
                {"status": "error"}, status=status.HTTP_400_BAD_REQUEST
            )
