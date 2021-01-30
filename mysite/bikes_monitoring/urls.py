from django.urls import path
from .views import BikeCheck
from .views import ProductMGMT

urlpatterns = [
    path('mobile_app/api/', ProductMGMT.as_view(), name="product_mgmt_url"),
    path('kross_api/', BikeCheck.as_view(), name="bike_check_url"),
    # path('mobile_app/api/', ProductMGMT.as_view(), name="product_mgmt_url")
    
]