from django.urls import path
from .views import *

urlpatterns = [
    
    path('dashboard/', EventDashboard.as_view()),
    path('delete/', EventDelete.as_view())

]