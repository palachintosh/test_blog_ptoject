from django.urls import path
from .views import BikeCheck
from .views import ProductMGMT
from .views import PrestaExt
from .views import PrestaReserve
from .views import PrestaReset

urlpatterns = [
    path('mobile_app/api/', ProductMGMT.as_view(), name="product_mgmt_url"),
    path('kross_api/', BikeCheck.as_view(), name="bike_check_url"),
    path('presta_extension/', PrestaExt.as_view(), name="presta_ext_url"),
    path('presta_extension/reserve/', PrestaReserve.as_view(), name="presta_reserve_url"),
    path('presta_reset/reset/', PrestaReset.as_view(), name="presta_reset_url"),
    # path('mobile_app/api/', ProductMGMT.as_view(), name="product_mgmt_url")
]