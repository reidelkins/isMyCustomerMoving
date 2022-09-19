from celery import shared_task
from time import sleep

@shared_task
def add(x, y):
    print("add")
    for i in range(30):
        print(i)
        sleep(2)
    return x + y
