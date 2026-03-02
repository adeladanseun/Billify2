from rest_framework import serializers
from sales.serializers import *
from .models import *

class ProductCategorySerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='get_category_display')

    class Meta:
        model = ProductCategory
        fields = '__all__'

class ProductSerializer(DefaultSerializer):
    categories = ProductCategorySerializer(many=True)
    class Meta:
        model = Product
        fields = '__all__'

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['__all__']