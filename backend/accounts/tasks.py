from celery import shared_task
from time import sleep

@shared_task
def add(x, y):
    for i in range(30):
        print(i)
        sleep(2)
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)