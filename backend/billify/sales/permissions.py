from rest_framework.permissions import IsAuthenticated, BasePermission
from django.db.models import Q

class IsOwner(BasePermission):
	def has_object_permission(self, request, view, obj):
		return obj.owner == request.user #automatically resolves authentication

class IsCompanyOwnerOrStaff(BasePermission):
	def has_permission(self, request, view):
		staff_company = request.user.staff_company
		if staff_company and staff_company.id:
			return (request.user.is_authenticated and (request.user.staff_company.is_staff or request.user.staff_company.is_owner))#.filter(Q(company__id=company_id), (Q(is_staff=True) | Q(is_owner=True))).exists())
		return False

class IsAuthenticated(BasePermission):
    def has_object_permission(self, request, view, obj):
	    return request.user.is_authenticated