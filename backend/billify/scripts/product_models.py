from django.contrib.auth.models import User
from product.models import *
from sales.models import Company
from random import randint

def generate_product_data():
    product_data = []
    for i in range(20):
        product_item = {}
        product_item["name"] = f'product_{i}'
        product_item["available_for_purchase"] = bool(randint(0,1))
        product_item["owner"] = Company.objects.get_or_create(name="Seun Company")[0]

        product_data.append(product_item)
    
    return product_data

def run(*args):
    my_objects = Product.objects.all()
    my_objects.delete()

    for items in generate_product_data():
        Product.objects.create(**items)

    