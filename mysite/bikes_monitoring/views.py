from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login

from django.http import HttpResponse
from requests.api import delete
from .PrestaRequest.mainp.PrestaRequest import PrestaRequest
from .utils import DataValidators
from .product_mooving import *
from .presta_reset import *


from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt



import os.path
import datetime
import json

try:
    from .PrestaRequest.mainp.api_secret_key import api_secret_key
except:
    ImportError("Cannot import API key!")



# import access token from file

def get_token():
    try:
        with open(os.path.dirname(__file__) + "/token/token.txt", "r") as f:
            token = f.readline().strip()
        return token

    except:
        return None


class BikeCheck(View):
# ==========================================
# |         Works only on kross.pl         |
# ==========================================

    # login_url = '/accounts/login/'

    def options(self, request):
        return cors_headers_options(origin="https://24.kross.pl", to_json=['TEST', 'TEST'])


    def get(self, request):
        if request.GET:
            if request.GET.get('token') and request.GET.get('token') == get_token():
                if request.GET.get('phone_number') is not None:
                    return remove_with_reservation(request)
                else:
                    return product_mooving(request)
            else:
                return JsonResponse({'Error': "Invalid token! Access deny!"})
        
        else:
            return JsonResponse({'Error': "Invalid request data!"})



# ==========================================
# |         Works only on kross.pl         |
# ==========================================



# Handler for prestashop
class PrestaExt(View):
    
    # login_url = '/accounts/login/'
    def options(self, request):
        return cors_headers_options(origin="https://3gravity.pl", to_json=['TEST', 'TEST'])

    def get(self, request):
        if request.GET:
            if request.GET.get('token') and request.GET.get('token') == get_token():
                return get_warehouses_value(request.GET)

            else:
                return JsonResponse({'Error': "Invalid token! Access deny!"})
        
            
        else:
            return JsonResponse({'Error': 'Looks like quantity is undefined..'})


class PrestaReserve(View):
    def options(self, request):
        return cors_headers_options(origin="https://3gravity.pl", to_json=['TEST', 'TEST'])

    def get(self, request):
        if request.GET:
            if request.GET.get('token') and request.GET.get('token') == get_token():
                return reserve_product(request.GET)
            
            else:
                return JsonResponse({'Error': "Invalid token! Access deny!"})
        else:
            return JsonResponse({'error': 'Produtc undefined on the stock!'})


# Post using for application

@method_decorator(csrf_exempt, name="dispatch")
class ProductMGMT(View):
    def post(self, request):
        print(request.POST)

        if request.POST:
            validator = DataValidators()
            try:
                w_from = request.POST.get('w_from')
                w_to = request.POST.get('w_to')

                print(w_to)

                validate_warehouse = validator.is_w_valid(w_from, w_to)

                if validate_warehouse:
                    w_from = validate_warehouse.get('w_from')
                    w_to = validate_warehouse.get('w_to')

                if (w_from is None or w_from == '') and (w_to is None or w_to == ''):
                    raise Exception

            except:
                return JsonResponse({'error': 'Warehouse <TO> must be fill!'})

            if w_from == '' or w_from is None:
                return app_management_inc(request, w_to)
            
            elif w_from == w_to:
                return JsonResponse({'error': 'Cannot transfer product between same warehouses!'})

            else:
                return app_management(request, w_from, w_to)
            
        return JsonResponse({'error': 'Data required!'})


# Init button in the app
@method_decorator(csrf_exempt, name="dispatch")
class AppInitProduct(View):
    def post(self, request):
        if request.POST:
            vd = DataValidators()
            code = vd.is_code_valid(str(request.POST.get("code")))

            if code:
                init_with_code = init_stocks_with_code(code.get("rex_code"))

            return JsonResponse(init_with_code)
        
        return JsonResponse({'error': 'Invalid data!'})


# Init button in the extension
class PrestaInit(View):
    def options(self, request):
        return cors_headers_options(origin="https://3gravity.pl", to_json=['TEST', 'TEST'])


    # In post params: product_id, comb_dict
    def post(self, request):
        if request.POST:
            
            if request.POST.get('token') and request.POST.get('token') == get_token():
                product_id = str(request.POST.get("product_id"))
                try:
                    comb_list = json.loads(request.POST.get("comb_list"))

                    if not isinstance(comb_list, list) or len(product_id) > 5:
                        return JsonResponse({
                            "error": "Invalid params was given!"
                        })
                
                except Exception as e:
                    return JsonResponse({"error": "Combinations invalid!"})

                else:
                    # Calling the init main thread
                    init_all = init_product(product_id, comb_list)
                    return JsonResponse(init_all)

            else:
                return JsonResponse({"error": "Invalid token! Access deny!"})
        
        else:
            return JsonResponse({"error": "Data required!"})



@method_decorator(csrf_exempt, name="dispatch")
class AppPrestaRestore(View):
    def post(self, request):
        # Change to POST after commit
        if request.POST:
            restore_token = request.POST.get("restore_token")
            restore_action = cancel_action(restore_token)

            if restore_action.get('success'):
                return JsonResponse({"success": "OK"})

        return JsonResponse({"error": "Impossible to restore or session doesn't exist!"})



class  PrestaReset(View):
    def get(self, request):
        if request.GET:
            pr = PrestaResetHandler()
            return pr.presta_reset(request.GET)
        else:
            return JsonResponse({'error': 'Reset option is unvailable now!'})