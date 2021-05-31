from django.contrib import admin
from django import forms
from django.forms import fields
from .models import Product, Warehouses


# Register your models here.


class WarehouseAdminForm(forms.ModelForm):
    class Meta:
        model = Warehouses
        fields = "__all__"


@admin.register(Warehouses)
class WarehouseAdmin(admin.ModelAdmin):
    form = WarehouseAdminForm


class ProductsAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"


@admin.register(Product)
class ProductsAdmin(admin.ModelAdmin):
    form = ProductsAdminForm