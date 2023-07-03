# import pytest
# import json
# # from django.urls import reverse
# from djstripe import models as djstripe_models

# from accounts.utils import makeCompany
# from .views import completed_checkout, cancel_subscription

# @pytest.fixture
# def company():
#     with open("webhook_examples/checkout_session_completed.json", "r") as f:
#         data = json.loads(f)
#     company, userList = completed_checkout(data)
#     return (company, userList)

# @pytest.fixture
# def canceled_company(company):
#     with open("webhook_examples/customer_subscription_deleted.json", "r") as f:
#         data = json.loads(f)
#     company, userList = cancel_subscription(data)
#     return company, userList


# @pytest.mark.django_db
# def test_checkout_session_completed(company):
#     company, userList = company
#     # product = djstripe_models.Plan.objects.get(id="")
#     # assert company.product == product
#     for user in userList:
#         assert user.isVerified == True
    

# @pytest.mark.django_db
# def test_subscription_canceled(canceled_company):
#     company, userList = canceled_company
#     product = djstripe_models.Plan.objects.get(id="price_1MhxfPAkLES5P4qQbu8O45xy")
#     assert company.product == product
#     for user in userList:
#         assert user.isVerified == False

    

