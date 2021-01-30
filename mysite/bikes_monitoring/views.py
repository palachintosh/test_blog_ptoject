from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from .PrestaRequest.mainp.PrestaRequest import PrestaRequest
from .utils import CodeValidators
from .product_mooving import product_mooving
from .product_mooving import cors_headers_options
from .product_mooving import app_management


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

    print("HERE=============")

    def get(self, request):
        
        print(request.POST)
        for i in request:
            print(i)

        if request.POST:
            return app_management(request)
        
        return JsonResponse({'error': 'Data required!'})
