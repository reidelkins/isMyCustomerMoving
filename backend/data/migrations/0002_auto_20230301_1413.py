# Generated by Django 4.0 on 2023-03-01 14:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL("""
            INSERT INTO data_zipCode (
                zipCode,
                lastUpdated
            )
            SELECT
                zipCode,
                lastUpdated
                
            FROM
                accounts_zipCode;
        """, reverse_sql="""
            INSERT INTO accounts_zipCode (
                zipCode,
                lastUpdated
            )
            SELECT
                zipCode,
                lastUpdated
            FROM
                data_zipCode;
        """),
        migrations.RunSQL("""
            INSERT INTO data_client (
                id,
                name,
                address,
                status,
                zipCode_id,
                company_id,
                city,
                state,
                contacted,
                note,
                servTitanID,
                phoneNumber
            )
            SELECT
                id,
                name,
                address,
                status,
                zipCode_id,
                company_id,
                city,
                state,
                contacted,
                note,
                servTitanID,
                phoneNumber
            FROM
                accounts_client;
        """, reverse_sql="""
            INSERT INTO accounts_client (
                id,
                name,
                address,
                status,
                zipCode_id,
                company_id,
                city,
                state,
                contacted,
                note,
                servTitanID,
                phoneNumber
            )
            SELECT
                id,
                name,
                address,
                status,
                zipCode_id,
                company_id,
                city,
                state,
                contacted,
                note,
                servTitanID,
                phoneNumber
            FROM
                data_client;
        """),
        migrations.RunSQL("""
            INSERT INTO data_scraperesponse (
                id,
                date,
                response,
                zip,
                status,
                url
            )
            SELECT
                id,
                date,
                response,
                zip,
                status,
                url
            FROM
                accounts_scraperesponse;
        """, reverse_sql="""
            INSERT INTO accounts_scraperesponse (
                id,
                date,
                response,
                zip,
                status,
                url
            )
            SELECT
                id,
                date,
                response,
                zip,
                status,
                url
            FROM
                data_scraperesponse;
        """),
        migrations.RunSQL("""
            INSERT INTO data_clientupdate (
                id,
                client_id,
                date,
                status,
                listed,
                note,
                contacted
            )
            SELECT
                id,
                client_id,
                date,
                status,
                listed,
                note,
                contacted
            FROM
                accounts_clientupdate;
        """, reverse_sql="""
            INSERT INTO accounts_clientupdate (
                id,
                client_id,
                date,
                status,
                listed,
                note,
                contacted
            )
            SELECT
                id,
                client_id,
                date,
                status,
                listed,
                note,
                contacted
            FROM
                data_clientupdate;
        """),
        migrations.RunSQL("""
            INSERT INTO data_task (
                id,
                completed,
                deletedclients
            )
            SELECT
                id,
                completed,
                deletedclients
            FROM
                accounts_task;
        """, reverse_sql="""
            INSERT INTO accounts_task (
                id,
                completed,
                deletedclients
            )
            SELECT
                id,
                completed,
                deletedclients
            FROM
                data_task;
        """),
        migrations.RunSQL("""
            INSERT INTO data_homelisting (
                id,
                zipCode_id,
                address,
                status,
                listed,
                scraperesponse_id
            )
            SELECT
                id,
                zipCode_id,
                address,
                status,
                listed,
                scraperesponse_id
            FROM
                accounts_homelisting;
        """, reverse_sql="""
            INSERT INTO accounts_homelisting (
                id,
                zipCode_id,
                address,
                status,
                listed,
                scraperesponse_id
            )
            SELECT
                id,
                zipCode_id,
                address,
                status,
                listed,
                scraperesponse_id
            FROM
                data_homelisting;
        """)
    ]
