from django.urls import path
from .views import *

urlpatterns = [
    path('', BikeCheck.as_view(), name="bike_check_url"),
    
]