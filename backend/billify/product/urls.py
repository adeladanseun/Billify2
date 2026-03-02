from django.urls import path
from .views import *

urlpatterns = [
    path('api/list/', ProductListView.as_view()),
    path('api/detail/<int:pk>/', ProductDetailView.as_view()),
]