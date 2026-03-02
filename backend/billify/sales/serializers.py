from rest_framework import serializers
from event.models import Event, EventMultiPurchase
from product.models import Product, ProductMultiPurchase
from sales.user_serializers import CompanySerializer, UserSerializer

class DefaultSerializer(serializers.ModelSerializer):
    """Default serializer for Product and Event Class to handle currency integer to string conversion and inclusion of owner username and any other information common to both model as the application develops
    """
    currency = serializers.CharField(source='get_currency_display', read_only=True)
    owner_username = serializers.CharField(source='owner.name', read_only=True)

class TransactionSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')

class EventTransactionSerializer(TransactionSerializer):
    amount = serializers.IntegerField()
    price = serializers.DecimalField(decimal_places=2, max_digits=20)

    class Meta:
        model = EventMultiPurchase
        fields = '__all__'

class ProductTransactionSerializer(TransactionSerializer):
    class Meta:
        model = ProductMultiPurchase
        fields = '__all__'

class UpcomingEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['name', 'date', 'location', 'interestedPeople', 'available_for_purchase']
    

class DefaultDashboardSerializer(serializers.Serializer):
    user = UserSerializer()
    company = CompanySerializer()
    owner = serializers.BooleanField()

class DashboardSerializer(DefaultDashboardSerializer):
    event_transactions = EventTransactionSerializer(many=True)
    product_transactions = ProductTransactionSerializer(many=True)
    upcoming_event = UpcomingEventSerializer(many=True)
    receipt_ticket_count = serializers.IntegerField()
    events_count = serializers.IntegerField()
    products_count = serializers.IntegerField()