from django.db import models
from django.contrib.auth.models import User
import json
from collections import defaultdict
from decimal import Decimal
# Create your models here.
class Default(models.Model):
    date_created = models.DateTimeField(auto_now=True)
    last_modified = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True

class CompanyStaff(Default):
    staff = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_company')
    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name='staff_companies')
    is_staff = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.staff.username}{'(owner)' if self.is_owner else ''} in {self.company.name}"
    

class Company(Default):
    USD = 0
    NGN = 1
    JPY = 2
    CHF = 3
    GBP = 4
    EUR = 5
    CURRENCIES = (
        (USD, 'USD'),
        (NGN, 'NGN'),
        (JPY, 'JPY'),
        (CHF, 'CHF'),
        (GBP, 'GBP'),
        (EUR, 'EUR'),
    )
    
    name = models.CharField(max_length=40)
    address = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=254, null=True)
    zip = models.CharField(max_length=9, null=True, blank=True)
    currency = models.IntegerField(choices=CURRENCIES, default=USD)
    #owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies')
    staffs = models.ManyToManyField(User, through=CompanyStaff)
    show_address_on_receipt = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    def return_model_type(self, order, name=False):
        event = order.get('event', None)
        product = order.get('product', None)
        if name:
            return event.__class__.__name__.lower() if event else product.__class__.__name__.lower()
        return event if event else product


    def validate_company(self, data):
        """Checks if the model instance or id in the data all belong to the same company.

        """
        company = False
        for order in data['orders']:
            if self.return_model_type(order).owner.id != self.id:
                raise ValueError(f'Order {order} Company owner does not match the other orders evaluated before')
            else:
                company = self.return_model_type(order).owner
        return company

    def purchase(self, data):
        """Groups the individual orders (of same origin e.g only Events or Products, never both) 
        into a common model and all orders must be under the same company product or event for database association and receipt generation

        Args:
            data (dict):   {
                'company': id or instance, #must be same as the class instance it is called on
                'orders': [
                        ...,
                        {
                            'model':instance,
                            'membership':instance,
                            'amount': int,
                        }, ...
                    ]
                }

        Raises:
            TypeError: _description_
            ValueError: _description_

        Returns:
            Class MultiInstance: Event or Product Instance class containing data of sale by user to the company
        """
        
        order_list = []
        grouped_orders = defaultdict(lambda: {'instance': None, 'orders': []})

        company = self.validate_company(data) #all orders belong to the same company
        
        for order in data['orders']:
            #order[f'{self.__class__.__name__.lower()}'] = data[f'{self.__class__.__name__.lower()}']
            order = self.return_model_type(order).purchase_validation(order)
            status, order = self.return_model_type(order).purchase_amount_validation(order)
            if not status:
                raise ValueError('Data is invalid')
            order_list.append(order)
            
            model_id = self.return_model_type(order).id
            grouped_orders[model_id]['orders'].append(order)
            grouped_orders[model_id]['instance'] = self.return_model_type(order)

            #grouped_orders[model_id]['total_amount'] += order['amount']
            #grouped_orders[model_id]['total_price'] += order['price'] * order['amount']
            #company = order[f'{self.__class__.__name__.lower()}'].owner

        multi_purchase_instance = self.return_model_type(order_list[0]).individual_purchase_class.multi_purchase_class.objects.create(
            company = company
        )
        
        for order_id, group in grouped_orders.items():
            group['instance'].purchase(group, multi_purchase_instance)
            
    
class MainObjectDefaultManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        """Accepts to keyword argument, company and type
        for anything other than all public instances, a requesting user must be specified
        if a requesting user is specified, then only the user(as owner) models will be returned

        types are public, private, all - private and all require the requesting user to be the owner or a staff
        """
        types = ('public', 'private', 'all')#order is important
        qs = super().get_queryset(*args, **kwargs)
        company = kwargs.get('user', None)
        if company and not isinstance(company, Company):
            raise ValueError('company argument is not a django model User instance')
        
        visibility = kwargs.get('type', types[0])
        if visibility not in types:
            raise ValueError('visibility value is invalid')
        
        filters = models.Q()
        if visibility == types[0]: #get public
            filters &= models.Q(available_for_purchase=True)
            if company:
                filters &= models.Q(owner=company)#any user can be attached to get the public modle instance of that individual
        else:
            if ((not company) or (not isinstance(company, Company))):
                raise ValueError('requesting company argument must be valid for |private and all| filters')
            filters &= models.Q(owner=company) #requesting user must be attached to get private model instance
            if visibility == types[1]: #get private
                filters &= models.Q(available_for_purchase=False)
            else: #get all
                pass
        return qs.filter(filters)

    
class MainObjectDefault(Default):
    #problem with catching the keyname event and product for assignment as variables here
    
    name = models.CharField(blank=False, max_length=100, null=False)
    available_for_purchase = models.BooleanField(default=True)
    #owner = models.ForeignKey(Company, on_delete=models.CASCADE)


    class Meta:
        abstract = True
    @property
    def currency(self):
        return self.owner.currency

    @property
    def is_public(self):
        return self.available_for_purchase
    
    @is_public.setter
    def is_public(self, value):
        """Sets the value of available using alternate name (is_public)"""
        if (value and not self.available_for_purchase) \
        or (not value and self.available_for_purchase):
            self.available_for_purchase = value
            self.save()

    @property
    def price(self):
        prices = [{
            'name': membership.name, 
            'price': membership.price
            } for membership in self.memberships.all()]
        if not prices:
            return 0
        return prices
    
    @property
    def amount_available(self):
        return sum([value.quantity_available for value in self.memberships.all()])
    
    @property
    def total_slot(self):
        return sum([value.initial_quantity_available for value in self.memberships.all()])
    
    def __str__(self):
        return self.name
    
    def purchase_validation(self, data: dict | str):
        """Takes a manadatory data argument and validates it by checking putting the data 
        in dictionary form if not already in it, changing the event id to the actual event if not already supplied
        

        Args:
            data (dict | str): {
                'model': id | model_instance,
                'membership': id | model_instance,
                'amount': int,
            }

        Raises:
            TypeError: raised if data type did not match
            ValueError: raised if no valid Event was found from the data information

        Returns:
            _type_: Boolean True if successful purchase made and False otherwise
        """
        model_object = self.__class__
        if self.available_for_purchase and data:
            if isinstance(data, str):
                data = json.loads(data)
            if not isinstance(data, dict):
                raise TypeError("The data passed is not a dict object or not the valid string format")
            #create individual purchase element
            if isinstance(data[f'{model_object.__name__.lower()}'], int):
                data[f'{model_object.__name__.lower()}'] = model_object.objects.filter(id=data[f'{model_object.__name__.lower()}']).first()
            if not isinstance(data[f'{model_object.__name__.lower()}'], model_object):
                raise ValueError(f'{model_object.__name__} object not found make')
            if not data[f'{model_object.__name__.lower()}'].available_for_purchase:
                raise ValueError(f'{data[f"{model_object.__name__.lower()}"]} not available to be purchased')
            
            if not data.get('amount', None): 
                data['amount'] = 1 

            data['amount'] = Decimal(str(data['amount']))
            
            data = self.purchase_membership_validation(data)
            #data = self.purchase_discount_evaluation(data)
                
            return data
        
        else:
            return None

 
    def purchase_membership_validation(self, data: dict):
        if not data.get('membership', None): 
            raise ValueError('membership id not specified in request')
        else:
            membership = data['membership']
            if isinstance(membership, int):
                membership = self.memberships.filter(id=int(data['membership'])).first()
            
            if not membership: raise ValueError('membership not found')
            
            data['membership'] = membership
            data['price'] = membership.price #sets the price to avoid changing code to access data['membership'].price
            return data
    
    def purchase_amount_validation(self, data: dict):
        """Ensure the membership has enough products or event slot to accommodate the purchase"""
        #if data['membership'].quantity_available >= data['amount']:
        if (self.membership_class.objects.get(id=data['membership'].id).quantity_available >= data['amount']):
            status = True
        else: 
            status = False
        return (status, data)
    
    def purchase_amount_subtraction(self, data: dict):
        membership = self.membership_class.objects.get(id=data['membership'].id)
        if membership and (membership.quantity_available >= data['amount']):
            membership.quantity_available -= data['amount']
            membership.save()
            return True
        return False
    
    def purchase(self, data: dict, multi_purchase_instance=None):
        """Takes the neccessary information to make a purchase

        Args:
            multiple_data(dict | str): {
                'orders': [..., {
                            'model_name_lower': id | model_instance,
                            'membership': id | model_instance,
                            'amount': int 
                          }, ...]
            }
            
        Raises:
            ValueError: Raised if amount of membership to be bought is less than amount of membership available

        Returns:
            Class: Respective MultiPurchase class if successful
            None: if purchase unsuccessful but this hasn't been defined as ValueError is raised
        """
        order_list = []
        company = None
        grouped_orders = defaultdict(lambda: {'orders': [], 'total_amount': Decimal(str(0)), 'total_price': Decimal(str(0.0))})
        
        for order in data['orders']:
            #order[f'{self.__class__.__name__.lower()}'] = data[f'{self.__class__.__name__.lower()}']
            order = self.purchase_validation(order)
            status, order = self.purchase_amount_validation(order)
            if not status:
                raise ValueError('Data is invalid')
            order_list.append(order)
            
            model_id = order[f'{self.__class__.__name__.lower()}'].id
            grouped_orders[model_id]['orders'].append(order)
            grouped_orders[model_id]['total_amount'] += order['amount']
            grouped_orders[model_id]['total_price'] += order['price'] * order['amount']
            company = order[f'{self.__class__.__name__.lower()}'].owner

        
        for order_id, group in grouped_orders.items():
            total_order_id_amount = group['total_amount']
            total_order_id_price = group['total_price']
            #find the discount that matches for the case presented
            discounts = self.__class__.objects.get(id=order_id).discounts.filter(is_active=True).order_by('-_discount')
            discount = 0
            for individual_discount in discounts:
                if individual_discount.discount_based_on == self.discount_class.AMOUNT:
                    if individual_discount.value <= total_order_id_amount: 
                        discount = individual_discount
                        break
                
                elif individual_discount.discount_based_on == self.discount_class.PRICE:
                    if individual_discount.value <= total_order_id_price:
                        discount = individual_discount
                        break
            if not multi_purchase_instance:
                multi_purchase_instance = self.individual_purchase_class.multi_purchase_class.objects.create(
                    company = group['orders'][0][f'{self.__class__.__name__.lower()}'].owner
                )
            for order in group['orders']:
                if order[f'{self.__class__.__name__.lower()}'].available_for_purchase:
                    data_purchase = self.individual_purchase_class.objects.create(
                        discount = discount.discount if discount else 0,
                        amount = order['amount'],
                        price = order['price'],
                        multi_purchase = multi_purchase_instance,
                        membership_name = f"{order[f'{self.__class__.__name__.lower()}'].name} : {order['membership'].name}",
                        #instance_id = data[f'{self.__class__.__name__.lower()}'].id
                        **{
                            f'{self.__class__.__name__.lower()}': self,
                        }
                    )
                    #subtract amount bought
                    status = self.purchase_amount_subtraction(order)
                    if status:
                        continue
                    else:
                        data_purchase.delete()
                        multi_purchase_instance.delete()
                        raise ValueError('Invalid data operated on')
        return multi_purchase_instance
    
class MembershipManager(models.Manager):
    def create(self, *args, **kwargs):
        model = super().create(*args, **kwargs)
        if ((not model.initial_quantity_available) and model.quantity_available):
            model.initial_quantity_available = model.quantity_available
            model.save()
        return model
class Membership(Default):
    name = models.CharField(max_length=50, default='Regular')
    description = models.TextField(null=True)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    quantity_available = models.IntegerField(default=0)
    initial_quantity_available = models.IntegerField(default=0)
    
    objects = MembershipManager()
    
    class Meta:
        abstract = True
        
    def __str__(self):
        return self.name
    
class Image(Default):
    #image = models.ImageField(upload_to='images/%c/')
    pass
    
    class Meta: # type: ignore
        abstract = True
        
class Discount(Default):
    AMOUNT = 1
    PRICE = 2
    
    DISCOUNT_BASED = (
        (AMOUNT, f'amount'),
        (PRICE, f'price'),
    )
    
    value = models.DecimalField(decimal_places=2, max_digits=20)
    _discount = models.DecimalField(decimal_places=2, max_digits=6)
    is_active = models.BooleanField(default=True)
    #creator = models.ForeignKey(Company, on_delete=models.CASCADE)
    discount_based_on = models.IntegerField(choices=DISCOUNT_BASED, default=AMOUNT) #events based on price can only have one membership
    
    def __str__(self):
        return f'{self.get_discount_based_on_display()} => {self.value} => Discount {self._discount}'
    
    @property
    def discount(self):
        if self.is_active:
            return self._discount
        return 0
    
    class Meta: # type: ignore
        abstract = True

class MultiPurchase(Default):
    COMPLETED = 0
    PENDING = 1

    STATUS = (
        (COMPLETED, 'Completed'),
        (PENDING, 'Pending'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    generation_count = models.IntegerField(default=0)
    status = models.IntegerField(choices=STATUS, default=PENDING)

    class meta:
        abstract = True

    def __str__(self):
        return self.name
        
    @property
    def amount(self):
        value = 0
        for purchase in self.purchases.all():
            value += purchase.amount
        return value
    
    @property
    def price(self):
        value = Decimal(str(0))
        for purchase in self.purchases.all():
            value += purchase.price_given_discount
        return value
        
class IndividualPurchase(Default):
    amount = models.IntegerField()
    price = models.DecimalField(decimal_places=2, max_digits=20)
    discount = models.DecimalField(decimal_places=3, max_digits=6)
    membership_name = models.CharField(default='unset')    
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return f'{self.membership_name} quantity {self.amount} price {self.price}'

    @property
    def price_given_discount(self):
        return Decimal(str(self.amount * self.price)) * Decimal(1 - self.discount)
    
    @property
    def model(self):
        """Shortcut function to return the event or product connected to it"""
        try:
            return self.event
        except:
            try:
                return self.product
            except:
                return None

class ReceiptManager(models.Manager):
    def create(self, *args, **kwargs):
        model = super().create(*args, **kwargs)
        model.multi_purchase.generation_count += 1
        model.multi_purchase.save()
        return model
class Receipt(Default):
    owner = models.CharField(max_length=100, default='unnamed')
    date_purchased = models.DateTimeField(auto_now=True)
    email = models.EmailField(null=True)
    