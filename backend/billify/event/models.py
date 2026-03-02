from django.db import models
from django.contrib.auth.models import User
from django.core.files import File
from django.conf import settings
from sales.models import Default, Company, MultiPurchase, MainObjectDefault, MainObjectDefaultManager, Membership, Image, Discount, IndividualPurchase, Receipt
import json
from random import randint
from .event_ticket_generator import EventTicketGenerator

# Create your models here.
class EventCategoryManager(models.Manager):
    def create(self, *args, **kwargs):
        model = EventCategory.objects.filter(**kwargs)
        if not model:
            return super().create(*args, **kwargs)
        return model[0]
    
class EventCategory(models.Model):
    objects = EventCategoryManager()

    FINANCE = 0
    MUSIC = 1
    ART = 2
    TECHNOLOGY = 3
    CELEBRATION = 4
    RELIGIOUS = 5
    CONFERENCE = 6
    
    CATEGORY = (
        (FINANCE, 'finance'),
        (MUSIC, 'music'),
        (ART, 'art'),
        (TECHNOLOGY, 'technology'),
        (CELEBRATION, 'celebration'),
        (RELIGIOUS, 'religious'),
        (CONFERENCE, 'conference')
    )

    category = models.IntegerField(choices=CATEGORY, default=CONFERENCE, unique=True)

class EventMembership(Membership):
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='memberships')

class EventMultiPurchase(MultiPurchase):
    
    @property
    def event(self):
        return self.purchases.all()  
    
    @property
    def owner(self):
        if self.purchases.count():
            return self.purchases.first().owner
        else:
            return None

class EventIndividualPurchase(IndividualPurchase):
    multi_purchase_class = EventMultiPurchase
    
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='individual_purchases')
    multi_purchase = models.ForeignKey(multi_purchase_class, on_delete=models.SET_NULL, null=True, related_name='purchases')

    def __str__(self):
        return f'Id {self.id} Price {self.price}'

    def ticket_format(self, id):
        string_length = 8
        id_string = str(id)
        if len(id_string) < string_length:
            return f'0'*(string_length - len(id_string)) + id_string
        return id_string

    @property
    def owner(self):
        return self.event.owner
    
    def generate_ticket(self, new=False):
        try: 
            ticket = self.ticket.pdf
        except:
            ticket = None
        
        if not (ticket and not new):

            filename = f'Ticket_{self.id}_{randint(1000, 10000)}.pdf'
            ticket_gen = EventTicketGenerator()

            ticket_gen.set_event_data(**{
                'event_name': self.event.name,
                'organizers': self.event.owner,
                'location': self.event.location,
                'event_date': self.event.date,
                'event_time': f"{self.event.start_time} - {self.event.end_time}",
                'ticket_type': self.membership_name,
                'ticket_id': self.ticket_format(self.id),
                'price': self.price,
                }
            )

            background_image = self.event.images.filter(ticket_background=True)
            background_image_path = None
            if background_image:
                background_image_path = background_image[randint(0, len(background_image)-1)].path
            pdf_data = ticket_gen.generate_ticket(background_image_path=background_image_path)#events with ticket image should be put here as background_image_path=""

            
            with open(filename, 'wb') as f:
                f.write(pdf_data)
            with open(filename, 'rb') as f:
                ticket = Ticket.objects.create(pdf=File(f), purchase=self)

        return (self, ticket)


class EventDiscount(Discount):
    #event can come with memberships and so the discount for different vary ...
    #either with number of tickets bought or the price of the ticket bought ...
    #therefore, value represents both price and quantity depending on the primary object
    
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='discounts')
       
class EventManager(MainObjectDefaultManager):
    pass
    
class Event(MainObjectDefault):
    owner = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='events')
    location = models.TextField(default='Unknown')
    date = models.DateTimeField(null=True)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    #conditions = models.TextField(null=True, help_text='Text of newline separated conditions')
    interestedPeople = models.IntegerField(default=0)
    ticket_expiration = models.DateTimeField(null=True)
    age_group = models.CharField(null=True, help_text='format [lower age - upper age]')
    #default_ticket_template = models.FileField(null=True)
    categories = models.ManyToManyField(EventCategory)
    
    objects = EventManager()
    membership_class = EventMembership
    individual_purchase_class = EventIndividualPurchase
    discount_class = EventDiscount
    
    @property
    def organiser(self):
        return self.owner

    @property
    def time(self):
        return self.start_time
    

class EventImage(Image):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to="events/images/", max_length=100)
    ticket_background = models.BooleanField(default=False) 

    @property
    def owner(self):
        return self.event.owner 
    
class Ticket(Receipt):
    pdf = models.FileField(upload_to="events/tickets/", max_length=100)
    multi_purchase = models.OneToOneField(EventMultiPurchase, on_delete=models.SET_NULL, related_name='ticket', null=True)

    def __str__(self):
        return f"Company {self.multi_purchase.event.owner} -> P_Id {self.multi_purchase.id} -> {self.pdf.name.split('/')[-1]}"
