from payments.models import Product
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
