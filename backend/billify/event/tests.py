from django.test import TestCase
from event.models import *
from django.contrib.auth.models import User
from decimal import Decimal
# Create your tests here.
class EventTest(TestCase):
    def setUp(self):
        self.username = 'test_user'
        self.password = 'test_password'
        user = User.objects.create_user(username=self.username, 
                                             password=self.password)
        self.model_instance_name = 'Test Event'
        self.owner = self.return_company()
        self.location = 'Test City'
        self.date = '2022-02-23'
        self.model = Event
        model = self.model.objects.create(name=self.model_instance_name, owner=self.owner, location=self.location, date=self.date)
    
    def return_company(self):
        return Company.objects.create(name='Seun Corp', phone_number='3863827')
    
    def return_user(self):
        return User.objects.get(username=self.username)
    
    def return_model(self):
        return self.model.objects.get(name=self.model_instance_name, owner=self.owner)
    
    def test_validate_event_existence(self):
        model = self.return_model()
        self.assertIsInstance(model, self.model)
    
        
    def test_event_default_membership_not_exists(self):
        model = self.return_model()
        self.assertFalse(model.memberships.first())
    
    def test_model_purchase_validation_with_id(self):
        model = self.return_model()
        model.membership_class.objects.create(
            name = 'default',
            price = 100,
            quantity_available = 18,
            **{
                f'{self.model.__name__.lower()}': model
            }
        )
        test_membership = model.memberships.first()
        data = {
            f'{self.model.__name__.lower()}': model.id,
            'amount': 1,
            'membership': test_membership.id, 
        }
        validatedData = model.purchase_validation(data)
        self.assertTrue(validatedData)
        
    def test_model_purchase_validation_with_model_instance(self):
        model = self.return_model()
        model.membership_class.objects.create(
            name = 'default',
            price = 100,
            quantity_available = 18,
            **{
                f'{self.model.__name__.lower()}': model
            }
        )
        test_membership = model.memberships.first()
        data = {
            f'{self.model.__name__.lower()}': model,
            'amount': 1,
            'membership': test_membership,
        }
        validatedData = model.purchase_validation(data)
        self.assertTrue(validatedData)
        
    def test_model_purchase_amount_validation(self):
        membership_amount = 3
        membership_price = 100
        
        model = self.return_model()
        model.membership_class.objects.create(
            name = 'default',
            price = 100,
            quantity_available = 18,
            **{
                f'{self.model.__name__.lower()}': model
            }
        )
        first_membership = model.memberships.first()
        first_membership.quantity_available = membership_amount
        first_membership.price = membership_price
        first_membership.save()
        
        data = {
            f'{self.model.__name__.lower()}': model,
            'amount': membership_amount - 1,
            'membership': first_membership,
        }
        status, data = model.purchase_amount_validation(data)
        self.assertTrue(status)
        
    def test_model_purchase_amount_validation_fail(self):
        membership_amount = 3
        membership_price = 100
        
        model = self.return_model()
        model.membership_class.objects.create(
            name = 'default',
            price = 100,
            quantity_available = 18,
            **{
                f'{self.model.__name__.lower()}': model
            }
        )
        first_membership = model.memberships.first()
        first_membership.quantity_available = membership_amount
        first_membership.price = membership_price
        first_membership.save()
        
        data = {
            f'{self.model.__name__.lower()}': model,
            'amount': membership_amount + 1,
            'membership': first_membership,    
        }
        status, data = model.purchase_amount_validation(data)
        self.assertFalse(status)
        
    def test_model_purchase_amount_subtraction(self):
        membership_amount = 3
        membership_price = 100
        
        model = self.return_model()
        model.membership_class.objects.create(
            name = 'default',
            price = 100,
            quantity_available = 18,
            **{
                f'{self.model.__name__.lower()}': model
            }
        )
        first_membership = model.memberships.first()
        first_membership.quantity_available = membership_amount
        first_membership.price = membership_price
        first_membership.save()
        
        data = {
            f'{self.model.__name__.lower()}': model,
            'amount': membership_amount - 1,
            'membership': first_membership,
        }
        model.purchase_amount_subtraction(data)
        first_membership = model.membership_class.objects.get(id=first_membership.id)
        self.assertEquals(first_membership.quantity_available, 1)
    
    def test_model_purchase_valid(self):
        membership_amount = 3
        membership_price = 100
        
        model = self.return_model()
        model.membership_class.objects.create(
            name = 'default',
            price = 100,
            quantity_available = 18,
            **{
                f'{self.model.__name__.lower()}': model
            }
        )
        first_membership = model.memberships.first()
        first_membership.quantity_available = membership_amount
        first_membership.price = membership_price
        first_membership.save()
        
        data = {
            #f'{self.model.__name__.lower()}': model,
            'orders': [{
            'amount': membership_amount - 1,
            'membership': first_membership,
            f'{self.model.__name__.lower()}': model,
            }]
        }
        result = model.purchase(data)
        self.assertTrue(((result.amount == membership_amount-1) and (result.price == membership_price * result.amount)))
    
    def test_model_multiple_purchase_valid(self):
        membership_amount = 3
        membership_price = 100
        
        model = self.return_model()
        model.membership_class.objects.create(
            name = 'default',
            price = 100,
            quantity_available = 18,
            **{
                f'{self.model.__name__.lower()}': model
            }
        )
        first_membership = model.memberships.first()
        first_membership.quantity_available = membership_amount
        first_membership.price = membership_price
        first_membership.save()
        
        data = {
            #f'{self.model.__name__.lower()}': model,
            'orders': [{
            'amount': 1,
            'membership': first_membership,
            f'{self.model.__name__.lower()}': model,
            } for i in range(membership_amount)]
        }
        result = model.purchase(data)
        self.assertTrue(((result.amount == membership_amount) and (result.price == membership_price*membership_amount)))
    
    def test_model_purchase_invalid(self):
        """Trying to buy more than what is available to sell"""
        membership_amount = 3
        membership_price = 100
        
        model = self.return_model()
        model.membership_class.objects.create(
            name = 'default',
            price = 100,
            quantity_available = 18,
            **{
                f'{self.model.__name__.lower()}': model
            }
        )
        first_membership = model.memberships.first()
        first_membership.quantity_available = membership_amount
        first_membership.price = membership_price
        first_membership.save()
        
        data = {
            #f'{self.model.__name__.lower()}': model,
            'orders': [{
                'amount': membership_amount + 1,
                'membership': first_membership,
                f'{self.model.__name__.lower()}': model,
                }]
        }
        self.assertRaises(ValueError, lambda: model.purchase(data))
    
    def test_model_purchase_multiple_invalid(self):
        """Buying multiple times with second pruchase amount exceeding what exists"""
        membership_amount = 3
        membership_price = 100
        
        model = self.return_model()
        model.membership_class.objects.create(
            name = 'default',
            price = 100,
            quantity_available = 18,
            **{
                f'{self.model.__name__.lower()}': model
            }
        )
        first_membership = model.memberships.first()
        first_membership.quantity_available = membership_amount
        first_membership.price = membership_price
        first_membership.save()
        
        data = {
            
            'orders': [
                        {'amount': membership_amount - 1,
                        'membership': first_membership,
                        f'{self.model.__name__.lower()}': model,},
                        {'amount': membership_amount - 1,
                         'membership': first_membership,
                        f'{self.model.__name__.lower()}': model,},
                     ]
        }
        #print(model.purchase(data))
        self.assertRaises(ValueError, lambda: model.purchase(data))
    
    def test_model_single_purchase_single_amount_based_discount(self):
        membership_amount = 3
        membership_price = 100
        discount_value = 0.40
        
        model = self.return_model()
        model.membership_class.objects.create(
            name = 'default',
            price = 100,
            quantity_available = 18,
            **{
                f'{self.model.__name__.lower()}': model
            }
        )
        first_membership = model.memberships.first()
        first_membership.quantity_available = membership_amount
        first_membership.price = membership_price
        first_membership.save()
        
        #creator = self.return_company(),
        discount = model.discount_class.objects.create(
            value = membership_amount,
            _discount = discount_value,
            discount_based_on = model.discount_class.AMOUNT,
            **{
                f'{self.model.__name__.lower()}': model
            }
        )
        data = {
            #f'{self.model.__name__.lower()}': model,
            'orders': [{
                'amount': membership_amount,
                'membership': first_membership,
                f'{self.model.__name__.lower()}': model,
                }]
        }
        result = model.purchase(data)
        self.assertTrue(result.price == membership_price * membership_amount * (1 - discount_value))
   
    def test_model_single_purchase_single_inactive_amount_based_discount(self):
        membership_amount = 3
        membership_price = 100
        discount_value = 0.40
        
        model = self.return_model()
        model.membership_class.objects.create(
            name = 'default',
            price = 100,
            quantity_available = 18,
            **{
                f'{self.model.__name__.lower()}': model
            }
        )
        first_membership = model.memberships.first()
        first_membership.quantity_available = membership_amount
        first_membership.price = membership_price
        first_membership.save()
        
        #creator = self.return_company(),
        discount = model.discount_class.objects.create(
            value = membership_amount,
            _discount = discount_value,
            discount_based_on = model.discount_class.AMOUNT,
            is_active = False,
            **{
                f'{self.model.__name__.lower()}': model
            }
        )
        data = {
            #f'{self.model.__name__.lower()}': model,
            'orders': [{
                'amount': membership_amount,
                'membership': first_membership,
                f'{self.model.__name__.lower()}': model,
                }]
        }
        result = model.purchase(data)
        self.assertTrue(result.price == membership_price * membership_amount)
    
    def test_model_single_purchase_two_active_amount_based_discount(self):
        membership_amount = 3
        membership_price = 100
        discount_value = Decimal(str(0.40))
        discount_extension = Decimal(str(0.20))
        discount_value2 = discount_value + discount_extension
        
        model = self.return_model()
        model.membership_class.objects.create(
            name = 'default',
            price = 100,
            quantity_available = 18,
            **{
                f'{self.model.__name__.lower()}': model
            }
        )
        first_membership = model.memberships.first()
        first_membership.quantity_available = membership_amount
        first_membership.price = membership_price
        first_membership.save()
        
        #creator = self.return_company(),
        discount1 = model.discount_class.objects.create(
            value = membership_amount - 1,
            _discount = discount_value,
            discount_based_on = model.discount_class.AMOUNT,
            is_active = True,
            **{
                f'{self.model.__name__.lower()}': model
            }
        )
        #creator = self.return_company(),
        discount2 = model.discount_class.objects.create(
            value = membership_amount,
            _discount = discount_value2,
            discount_based_on = model.discount_class.AMOUNT,
            is_active = True,
            ** {
                f'{self.model.__name__.lower()}': model
            }
        )
        data = {
            #f'{self.model.__name__.lower()}': model,
            'orders': [{
                'amount': membership_amount,
                'membership': first_membership,
                f'{self.model.__name__.lower()}': model,
                }]
        }    
        result = model.purchase(data)
        self.assertTrue(result.price == membership_price * membership_amount *  (1 - discount_value2))

    def test_model_mulitple_membership_multiple_active_discount_valid_purchase(self):
        discount1 = Decimal(str(0.30)) #amount based
        discount2 = Decimal(str(0.50)) #price based

        membership1_amount = 300
        membership2_amount = 200

        membership1_price = 1
        membership2_price = 40
        
        model = self.return_model()
        model.membership_class.objects.create(
            name = 'default',
            price = 100,
            quantity_available = 18,
            **{
                f'{self.model.__name__.lower()}': model
            }
        )
        first_membership = model.memberships.first()
        first_membership.quantity_available = membership1_amount
        first_membership.price = membership1_price
        first_membership.save()

        second_membership = model.membership_class.objects.create(
                name = 'VIP',
                price = membership2_price,
                quantity_available = membership2_amount,
                **{
                    f'{self.model.__name__.lower()}': model,
                }
            )
        
        #based on amount
        #creator = self.return_company(),
        discount1 = model.discount_class.objects.create(
            value = membership1_amount,
            _discount = discount1,
            discount_based_on = model.discount_class.AMOUNT,
            is_active = True,
            **{
                f'{self.model.__name__.lower()}': model,
            }
        )

        #based on price
        #creator = self.return_company(),
        discount2 = model.discount_class.objects.create(
            value = membership2_price,
            _discount = discount2,
            discount_based_on = model.discount_class.PRICE,
            is_active = True,
            **{
                f'{self.model.__name__.lower()}': model,
            }
        )
        data = {
            'orders': [
                {
                    'amount': membership1_amount,
                    'membership': first_membership,
                    f'{self.model.__name__.lower()}': model,
                },
                {
                    'amount': membership2_amount,
                    'membership': second_membership,
                    f'{self.model.__name__.lower()}': model,
                }
            ]
        }
        result = model.purchase(data)
        self.assertTrue(result.price == ((membership1_price * membership1_amount) + (membership2_price * membership2_amount)) *  (1 - discount2._discount))

   