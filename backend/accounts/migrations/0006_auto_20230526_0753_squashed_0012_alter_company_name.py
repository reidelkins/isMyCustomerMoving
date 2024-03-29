# Generated by Django 3.2.8 on 2023-07-08 22:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('accounts', '0006_auto_20230526_0753'), ('accounts', '0007_company_servicetitancustomersyncoption'), ('accounts', '0008_company_zapier_recentlysold'),
                ('accounts', '0009_company_product'), ('accounts', '0010_auto_20230622_1758'), ('accounts', '0011_company_for_sale_purchased'), ('accounts', '0012_alter_company_name')]

    dependencies = [
        ('data', '0013_auto_20230526_0753'),
        ('accounts', '0005_auto_20230526_0753'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Franchise',
        ),
        migrations.AddField(
            model_name='company',
            name='enterprise',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='companies', to='accounts.enterprise'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='enterprise',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='users', to='accounts.enterprise'),
        ),
        migrations.AddField(
            model_name='company',
            name='product',
            field=models.ForeignKey(blank=True, default=None, null=True,
                                    on_delete=django.db.models.deletion.SET_NULL, to='accounts.enterprise'),
        ),
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
        migrations.AddField(
            model_name='company',
            name='service_titan_customer_sync_option',
            field=models.CharField(choices=[('option1', 'option1'), ('option2', 'option2'), (
                'option3', 'option3')], default='option1', max_length=100),
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
        migrations.AddField(
            model_name='company',
            name='zapier_recently_sold',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='isVerified',
            new_name='is_verified',
        ),
        migrations.AddField(
            model_name='company',
            name='for_sale_purchased',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
