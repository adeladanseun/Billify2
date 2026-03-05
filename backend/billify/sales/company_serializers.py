from rest_framework import serializers
from .models import *

class CompanySerializer(serializers.ModelSerializer):
    currency = serializers.CharField(source='get_currency_display')
    class Meta:
        model = Company
        fields = ['id', 'name', 'address', 'currency']

class CompanyStaffSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name')
    company_id = serializers.IntegerField(source='company.id')
    currency = serializers.CharField(source='company.get_currency_display')
    phone_number = serializers.CharField(source='company.phone_number')
    address = serializers.CharField(source='company.address')
    zip = serializers.CharField(source='company.zip')

    class Meta:
        model = CompanyStaff
        fields = [
            'company_id', 'company_name', 'is_owner', 'is_staff',
            'currency', 'phone_number', 'address', 'zip'
        ]
