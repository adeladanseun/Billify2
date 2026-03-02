from django.contrib.auth.models import User
from event.models import *
from sales.models import Company
from random import randint

def generate_event_data():
    event_data = []
    for i in range(20):
        event_item = {}
        event_item["name"] = f'event_{i}'
        event_item["available_for_purchase"] = bool(randint(0,1))
        event_item["owner"] = Company.objects.get_or_create(name="Seun Company")[0]
        event_item["location"] = f"location_{i}"
        event_item["interestedPeople"] = randint(0, 100)

        event_data.append(event_item)
    
    return event_data

def run(*args):
    my_objects = Event.objects.all()
    my_objects.delete()

    for items in generate_event_data():
        event = Event.objects.create(**items)
        multi_purchase = EventMultiPurchase.objects.create(company=Company.objects.first(), name=f'event_multi_purchase{randint(1,1000)}')
        for i in range(randint(1,6)):
            EventIndividualPurchase.objects.create(event=event, amount=randint(1,60), price=randint(2,800), discount=0.0, multi_purchase=multi_purchase)

    