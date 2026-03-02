from rest_framework import permissions
from .models import Product
from .serializers import ProductSerializer
from sales.permissions import *
from sales.views import *

class ProductModel:
	model = Product

class ProductListView(ProductModel, ItemListView):
	serializer_class = ProductSerializer

class PrivateProductListView(ProductModel, PrivateItemListView):
	serializer_class = ProductSerializer

class ProductCreateView(ProductModel, ItemCreateView):
	serializer_class = ProductSerializer

		
class ProductDetailView(ProductModel, ItemDetailView):
	serializer_class = ProductSerializer

