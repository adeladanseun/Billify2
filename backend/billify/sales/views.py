from datetime import datetime
from itertools import chain

from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Prefetch

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from .permissions import *
from .models import Company
from .serializers import *

from event.models import EventMultiPurchase, Ticket
from product.models import ProductMultiPurchase, Invoice

# Create your views here.
class QueryClass:
    model = None
    is_public = 'public'
    def get_queryset(self, *args, **kwargs):
        if not self.model: raise AttributeError('No model attribute defined on view class')
        return self.model.objects.get_queryset(is_public=self.is_public)
    
class ItemListView(QueryClass, generics.ListAPIView):
    pass

class PrivateItemListView(ItemListView):
    is_public = 'all'
    permission_classes = [IsAuthenticated]
    def get_queryset(self, *args, **kwargs):
        #print(self.request)
        qs = super().get_queryset()
        #qs.filter(owner=self.request.body.get('company_id'))

class ItemCreateView(QueryClass, generics.CreateAPIView):
    permission_classes = [IsAuthenticated] #add ability to ban user from creating product or events

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class ItemDetailView(QueryClass, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []#IsOwner]

class DashboardView(APIView):

    permission_classes = [IsCompanyOwnerOrStaff]
    
    def get(self, request):
        company = Company.objects.prefetch_related(
            Prefetch('events', queryset=Event.objects.prefetch_related('individual_purchases__multi_purchase')),
            Prefetch('products', queryset=Product.objects.prefetch_related('individual_purchases__multi_purchase'))
            ).get(id=request.user.staff_company.company.id)
        
        events = company.events.all()
        events_count = events.count()
        
        products = company.products.all()
        products_count = products.count()
        
        event_multi_purchase = set([ind_pur.multi_purchase for ind_pur in chain(*[event.individual_purchases.all() for event in events])])

        product_multi_purchase = set([ind_pur.multi_purchase for ind_pur in chain(*[product.individual_purchases.all() for product in products])])

        upcoming_events = events.filter(Q(date__gte=datetime.now()))

        
        dashboard_details = DashboardSerializer({
            "user": self.request.user,
            "company": company,
            "event_transactions": event_multi_purchase,
            "product_transactions": product_multi_purchase,
            "upcoming_event": upcoming_events,
            "owner": company.staff_companies.get(staff=self.request.user).is_owner,
            "receipt_ticket_count": Invoice.objects.filter(multi_purchase__company=company).count() + Ticket.objects.filter(multi_purchase__company=company).count(), 
            "events_count": events_count,
            "products_count": products_count,
        })
        return Response(dashboard_details.data)
        #return Response(dashboard_details.errors)
    