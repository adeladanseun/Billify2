from itertools import chain
import json
import http

from django.db.models import Prefetch

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializers import *
from sales.permissions import *
from sales.views import *

class EventModel:
	model = Event

class EventListView(EventModel, ItemListView):
	serializer_class = EventSerializer

class EventDashboard(APIView):

	permission_classes = [IsCompanyOwnerOrStaff]

	def get(self, request):
		user = request.user
		company = user.staff_company.company
		events = Event.objects.prefetch_related(
			Prefetch("individual_purchases", queryset=EventIndividualPurchase.objects.select_related('multi_purchase__ticket')),
			Prefetch('categories')
			).filter(owner__id=company.id)
		all_unique_purchases = set([ind_pur.multi_purchase for ind_pur in chain(*[event.individual_purchases.all() for event in events])])
		tickets = []#set([m_pur.ticket for m_pur in all_unique_purchases if m_pur.ticket and m_pur.ticket.pdf])
		
		return Response(EventDashboardSerializer({
			"user": user,
			"company": company,
			"owner": user.staff_company.is_owner,
			"events": events,
			"tickets": tickets,
			"purchases": all_unique_purchases,
			"categories": EventCategory.objects.all(),
			}).data)

class EventDelete(APIView):

	permission_classes = [IsCompanyOwnerOrStaff]

	def post(self, request):
		id = json.loads(request.body.decode('utf-8')).get('id')
		if not isinstance(id, type([])):
			id = [id]
		events = Event.objects.filter(owner=request.user.staff_company.company, id__in=id)#requester must be a staff in the company
		deleted_id = []
		if events:
			for event in events:
				deleted_id.append(event.id)
				event.delete()
			return Response({"details": f'id {deleted_id} deleted successfully', "ids": deleted_id})
		return Response({"details": f'id {id}: Encountered error deleting'}, status=http.HTTPStatus.METHOD_NOT_ALLOWED)

class PrivateEventListView(EventModel, PrivateItemListView):
	serializer_class = EventSerializer

class EventCreateView(EventModel, ItemCreateView):
	serializer_class = EventSerializer

class EventDetailView(EventModel, ItemDetailView):
	serializer_class = EventSerializer

	

# Create your views here.
