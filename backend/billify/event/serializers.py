from rest_framework import serializers
from sales.serializers import *
from .models import *

class EventCategorySerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='get_category_display')
    class Meta:
        model = EventCategory
        fields = '__all__'

class EventMembershipSerializer(DefaultSerializer):
    class Meta:
        model = EventMembership
        fields = ['description', 'event', 'id', 'initial_quantity_available', 
                  'name', 'price', 'quantity_available']

class EventDiscountSerializer(DefaultSerializer):
    class Meta:
        model = EventDiscount
        fields = '__all__'

class EventSerializer(DefaultSerializer):
    amount_available = serializers.IntegerField()
    total_slot = serializers.IntegerField()
    categories = EventCategorySerializer(many=True)
    discounts = EventDiscountSerializer(many=True)
    memberships = EventMembershipSerializer(many=True)
    
    class Meta:
        model = Event
        fields = '__all__'

class EventTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        exclude = ['pdf']
        
class EventDashboardSerializer(DefaultDashboardSerializer):
    tickets = EventTicketSerializer(many=True)
    events = EventSerializer(many=True)
    purchases = EventTransactionSerializer(many=True)
    categories = EventCategorySerializer(many=True)