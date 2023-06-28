# Generated by Django 3.2.8 on 2023-06-22 17:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_company_product'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='accessToken',
            new_name='access_token',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='clientID',
            new_name='client_id',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='clientSecret',
            new_name='client_secret',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='recentlySoldPurchased',
            new_name='recently_sold_purchased',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='serviceTitanAppVersion',
            new_name='service_titan_app_version',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='serviceTitanCustomerSyncOption',
            new_name='service_titan_customer_sync_option',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='serviceTitanForRentTagID',
            new_name='service_titan_for_rent_tag_id',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='serviceTitanForSaleContactedTagID',
            new_name='service_titan_for_sale_contacted_tag_id',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='serviceTitanForSaleTagID',
            new_name='service_titan_for_sale_tag_id',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='serviceTitanRecentlySoldContactedTagID',
            new_name='service_titan_recently_sold_contacted_tag_id',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='serviceTitanRecentlySoldTagID',
            new_name='service_titan_recently_sold_tag_id',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='sfAccessToken',
            new_name='sf_access_token',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='sfRefreshToken',
            new_name='sf_refresh_token',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='stripeID',
            new_name='stripe_id',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='tenantID',
            new_name='tenant_id',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='zapier_forSale',
            new_name='zapier_for_sale',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='zapier_recentlySold',
            new_name='zapier_recently_sold',
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='isVerified',
            new_name='is_verified',
        ),
    ]