from django.db.models import Count, Case, When, Value, IntegerField
from django.core.mail import send_mail
from datetime import datetime
import pandas as pd
from accounts.models import Company
from data.models import Client, HomeListing, ClientUpdate
from payments.models import ServiceTitanInvoice, Product


def create_report():
    free_product = Product.objects.get(id="price_1MhxfPAkLES5P4qQbu8O45xy")

    companies_with_invoice_count = Company.objects.annotate(
        invoice_count=Count('client_company__servicetitaninvoice')
    ).filter(invoice_count__gt=0).exclude(product=free_product).values('id', 'name', 'invoice_count')

    companies_with_status_count = Company.objects.annotate(
        sold_6_count=Count(
            Case(
                When(client_company__status="House Recently Sold (6)", then=1),
                output_field=IntegerField(),
            )
        ),
        for_sale_count=Count(
            Case(
                When(client_company__status="House For Sale", then=1),
                output_field=IntegerField(),
            )
        ),
        pending_count=Count(
            Case(
                When(client_company__status="Pending", then=1),
                output_field=IntegerField(),
            )
        )
    ).exclude(product=free_product).values('id', 'name', 'sold_6_count', 'for_sale_count', 'pending_count')

    companies_with_invoice_count_df = pd.DataFrame(
        companies_with_invoice_count)
    companies_with_status_count_df = pd.DataFrame(companies_with_status_count)

    companies_with_invoice_count_df = companies_with_invoice_count_df.rename(
        columns={'invoice_count': 'invoice_count'})
    companies_with_status_count_df = companies_with_status_count_df.rename(columns={'sold_6_count': 'sold_6_count',
                                                                                    'for_sale_count': 'for_sale_count',
                                                                                    'pending_count': 'pending_count'})

    companies_with_invoice_count_df = companies_with_invoice_count_df.set_index(
        'id')
    companies_with_status_count_df = companies_with_status_count_df.set_index(
        'id')

    companies_with_invoice_count_df = companies_with_invoice_count_df.join(
        companies_with_status_count_df)
    companies_with_invoice_count_df = companies_with_invoice_count_df.fillna(0)
    companies_with_invoice_count_df = companies_with_invoice_count_df.astype(
        int)
    companies_with_invoice_count_df = companies_with_invoice_count_df.reset_index()
    companies_with_invoice_count_df = companies_with_invoice_count_df.rename(
        columns={'id': 'company_id'})

    companies_with_invoice_count_df.to_csv(
        'companies_with_invoice_count.csv', index=False)

    # send csv to email
    send_mail(
        f'Report - {datetime.today().strftime("%Y-%m-%d")}',
        'Here is the daily report.',
        '',
        ['reid@ismycustomermoving.com'],
        fail_silently=False,
        attachments=['companies_with_invoice_count.csv']
    )


# HomeListing.objects.all().count()
# ClientUpdate.objects.filter(status__in=["House Recently Sold (6)", "House For Sale", "Pending"]).count()

# for company in companies_with_invoice_count:
#     print(f"Company: {company['name']}, Invoice Count: {company['invoice_count']}")


# for company in companies_with_status_count:
#     print(f"Company: {company['name']}")
#     print(f"House Recently Sold (6) Clients: {company['sold_6_count']}")
#     print(f"House For Sale Clients: {company['for_sale_count']}")
#     print(f"Pending Clients: {company['pending_count']}")
#     print("-" * 50)
