from accounts.models import Company
from data.models import Client, ZipCode
from payments.models import Product, ServiceTitanInvoice
from django.test import TestCase


class TestProductModel(TestCase):
    def test_product_creation(self):
        """
        Test the creation of a Product object.
        """
        product = Product.objects.create(
            id="123", amount=150.0, interval="month", name="Product1"
        )
        self.assertEqual(product.id, "123")
        self.assertEqual(product.amount, 150.0)
        self.assertEqual(product.interval, "month")
        self.assertEqual(product.name, "Product1")

    def test_product_default_values(self):
        """
        Test the default values for the amount and interval fields in a Product object.
        """
        product = Product.objects.create(id="123", name="Product1")
        self.assertEqual(product.amount, 0)
        self.assertEqual(product.interval, "month")


class TestServiceTitanInvoiceModel(TestCase):
    """
    Setup test environment.
    """

    def setUp(self):
        self.client_object = Client.objects.create(
            name="Test Client",
            address="123 Test Street",
            zip_code=ZipCode.objects.create(zip_code="12345"),
            company=Company.objects.create(name="Test Company"),
            status="No Change",
        )

    def test_service_titan_invoice_creation(self):
        """
        Test the creation of a ServiceTitanInvoice object.
        """
        invoice = ServiceTitanInvoice.objects.create(
            invoice_id="123", amount=150.0, created_on="2020-01-01", client=self.client_object
        )
        self.assertEqual(invoice.invoice_id, "123")
        self.assertEqual(invoice.amount, 150.0)
        self.assertEqual(invoice.created_on, "2020-01-01")
        self.assertEqual(invoice.client, self.client_object)

    def test_service_titan_invoice_default_values(self):
        """
        Test the default values for the street and created_on fields in a ServiceTitanInvoice object.
        """
        invoice = ServiceTitanInvoice.objects.create(
            invoice_id="123", client=self.client_object)
        self.assertEqual(invoice.created_on, None)
        self.assertEqual(invoice.amount, 0)
