from django.urls import path
from .views import *

urlpatterns = [
    path('search/filter/', SearchingFilter.as_view(), name="search_filter_url"),
    path('', MyWarehouse.as_view(), name="my_warehouse_url"),
    path('warehouse/create/', CreateWarehouse.as_view(), name="create_warehouse_url"),
    path('select_warehouse/<str:slug>/', SelectWarehouse.as_view(), name="select_warehouse_url"),
    path('update_warehouse/update/<str:slug>', UpdateWarehouse.as_view(), name="update_warehouse_url"),
    path('product/add_new/', AddProduct.as_view(), name="add_product_url"),
    path('product/<str:slug>', Products.as_view(), name="related_products_url"),
    path('products/<str:slug>/update/', UpdateProduct.as_view(), name="update_product_url")
]