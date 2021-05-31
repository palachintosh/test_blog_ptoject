from django.db.models.query_utils import FilteredRelation
from django.shortcuts import get_object_or_404, render
from django.views.generic import View
from django.db.models import Q
from .models import *
from django.utils import timezone
from .forms import ProductEditForm, WarehouseForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import *


# Create your views here.


class MyWarehouse(LoginRequiredMixin, View):
    model = Warehouses
    # raise_exception = True

    def get(self, request):
        warehouse = self.model.objects.filter(date_pub__lte=timezone.now()).order_by('-date_pub')
        
        return render(request, 'warehouse/warehouse_home.html', context={
            self.model.__name__.lower(): warehouse
            })


class SelectWarehouse(LoginRequiredMixin, View):
    model = Warehouses
    product_model = Product
    template = 'warehouse/warehouse_home.html'

    def get(self, request, slug):
        get_object = get_object_or_404(self.model, slug__iexact=slug)
        get_products = get_object.related_products.all()

        warehouse = self.model.objects.filter(date_pub__lte=timezone.now()).order_by('-date_pub')

        return render(request, self.template, context={
                                self.model.__name__.lower(): warehouse,
                                'general_warehouses': get_object,
                                'products': get_products,
                                })


class CreateWarehouse(LoginRequiredMixin, ObjectCreateMixin, View):
    model = Warehouses
    model_form = WarehouseForm
    template = 'warehouse/create_warehouse.html'


class UpdateWarehouse(LoginRequiredMixin, ObjectUpdateMixin, View):
    model = Warehouses
    model_form = WarehouseForm
    template = 'warehouse/warehouse_config.html'


class Products(LoginRequiredMixin, View):
    model = Product
    product_form = ProductEditForm
    war_model = Warehouses
    template = 'warehouse/product.html'

    def get(self, request, slug):
        product = get_object_or_404(self.model, slug__iexact=slug)
        bound_form = self.product_form(instance=product)
        warehouses = self.war_model.objects.filter(date_pub__lte=timezone.now()).order_by('-date_pub')


        return render(request, self.template, context={
            self.model.__name__.lower(): product,
            'product_form': bound_form,
            'warehouses': warehouses
        })



class AddProduct(LoginRequiredMixin, ObjectCreateMixin, View):
    model = Product
    model_form = ProductEditForm
    template = 'warehouse/product_create.html'



class UpdateProduct(LoginRequiredMixin, View):
    model = Product
    model_form = ProductEditForm


    def post(self, request, slug):
        old_object = self.model.objects.get(slug__iexact=slug)
        bound_form = self.model_form(request.POST, instance=old_object)

        if bound_form.is_valid():
            new_object = bound_form.save()

            return redirect(new_object)


        return reverse('related_products_url', kwargs={'slug': slug, 'request': request})


class SearchingFilter(LoginRequiredMixin, View):
    model = Product
    war_model = Warehouses
    template = 'warehouse/warehouse_home.html'

    def get(self, request):
        search_query = request.GET

        if search_query:
            title = slugify(str(search_query.get('p_keyword')))
            loc_products = None
            get_object = self.war_model.objects.get(title=search_query.get('p_warehouse'))


            if title != None:
                loc_products = self.model.objects.filter(
                    Q(title__icontains=title) |
                    Q(description__icontains=title) |
                    Q(barcode__icontains=title)
                    )

                # loc_products = get_object.products.annotate(
                #     r_products = FilteredRelation(
                #         'title', condition=Q(title__icontains=title),
                #     ),
                # )

                if search_query.get('p_available') == 'on':
                    loc_products = loc_products.filter(active_stamp=True)
                
                if search_query.get('p_olx_available') == 'on':
                    loc_products = loc_products.filter(olx_stamp=True)
        

        warehouse = self.war_model.objects.filter(date_pub__lte=timezone.now()).order_by('-date_pub')

        return render(request, self.template, context={
                                self.war_model.__name__.lower(): warehouse,
                                'products': loc_products,
                                'general_warehouses': get_object,
                                'filter': True
                                })

