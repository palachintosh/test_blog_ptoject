from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from .PrestaRequest.mainp.PrestaRequest import PrestaRequest
from .utils import DataValidators
from .product_mooving import product_mooving
from .product_mooving import cors_headers_options
from .product_mooving import app_management
from .product_mooving import app_management_inc


from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt



import os.path
import datetime

try:
    from .PrestaRequest.mainp.api_secret_key import api_secret_key
except:
    ImportError("Cannot import API key!")


# Create your views here.



class BikeCheck(View):
# ==========================================
# |         Works only on kross.pl         |
# ==========================================

    def options(self, request):
        return cors_headers_options(to_json=['TEST', 'TEST'])


    def get(self, request):
        if request.GET:
            return product_mooving(request)


# ==========================================
# |         Works only on kross.pl         |
# ==========================================



# Post using for application

@method_decorator(csrf_exempt, name="dispatch")
class ProductMGMT(View):
    def post(self, request):

        # print(request.POST)

        if request.POST:
            validator = DataValidators()
            try:
                w_from = request.POST.get('w_from')
                w_to = request.POST.get('w_to')

                validate_warehouse = validator.is_w_valid(w_from, w_to)

                if validate_warehouse:
                    w_from = validate_warehouse.get('w_from')
                    w_to = validate_warehouse.get('w_to')

                if (w_from == None or w_from == '') and (w_to == None or w_to == ''):
                    raise Exception

            except:
                return JsonResponse({'error': 'Warehouse <TO> must be filled!'})

            if w_from == '' or w_from == None:
                return app_management_inc(request, w_to)

            elif w_from == w_to:
                return JsonResponse({'error': 'Cannot rm product from same warehouse!'})

            else:
                return app_management(request, w_from, w_to)
            
        return JsonResponse({'error': 'Data required!'})