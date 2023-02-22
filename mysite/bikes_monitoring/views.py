from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login

from django.http import HttpResponse
from .PrestaRequest.mainp.PrestaRequest import PrestaRequest
from .utils import DataValidators
from .product_mooving import *
from .presta_reset import *
from .statuses import *

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie


import os.path
import datetime
import json

try:
    from .PrestaRequest.mainp.api_secret_key import api_secret_key
except:
    ImportError("Cannot import API key!")

formatter = logging.Formatter("%(levelname)s: %(asctime)s - %(message)s")
views_base_dir = os.path.dirname(os.path.abspath(__file__))
file_handler = logging.FileHandler(views_base_dir + "/log/views.log")
views_logger = logging.getLogger('views_logger')
views_logger.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
views_logger.addHandler(file_handler)

# import access token from file

def get_token():
    try:
        with open(os.path.dirname(__file__) + "/token/token.txt", "r") as f:
            token = f.readline().strip()
        return token

    except:
        return None


# Cors politics
def cors_headers_add(to_json=[], origin=None):
    data = JsonResponse({to_json[0]: to_json[1]})

    if origin is None: 
        data["Access-Control-Allow-Origin"] = "https://3gravity.pl" 
    else:
        data["Access-Control-Allow-Origin"] = origin

    data["Vary"] = "Origin"
    data["Access-Control-Allow-Credentials"] = "true"
    data[
        "Access-Control-Allow-Headers"] = "Origin, Access-Control-Allow-Origin, Accept, X-Requested-With, Content-Type"
    data["pragma"] = "no-cache"
    data["Cache-Control"] = "no-cache, no-store"
    return data


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
            # if True:
                if request.GET.get('phone_number') is not None:
                    # return remove_with_reservation(request)
                    rwr = remove_with_reservation(request)
                    try:
                        if rwr is not None:
                            return rwr
                    
                    except:
                        return cors_headers_add(['error', 'Nispodziewany blad!'],
                        "https://24.kross.pl")
                else:
                    views_logger.info("TRANSACTION: KROSS, " + str(request.GET.get('code')))
                    return product_mooving(request)
            else:
                return cors_headers_add(
                    ['error', "Invalid token! Access deny!"],
                    "https://24.kross.pl")
        
        else:
            return cors_headers_add(['error', "Invalid request data!"],
            "https://24.kross.pl")



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

@method_decorator(csrf_exempt, name="dispatch")
class PrestaReserve(View):
    def options(self, request):
        return cors_headers_options(origin="https://3gravity.pl", to_json=['TEST', 'TEST'])

    # must be changed to POST and set token before commit!!
    def post(self, request):
        if request.POST:
            if request.POST.get('token') and request.POST.get('token') == get_token():
            # if True:
                return reserve_product(request.POST)
            
            else:
                return cors_headers_add(['error', "Invalid token! Access deny!"])
        else:
            return cors_headers_add(['error', 'Invalid request!'])


class PrestaGetReserve(View):
    def options(self, request):
        return cors_headers_options(origin="https://3gravity.pl", to_json=['TEST', 'TEST'])

    def get(self, request):
        if request.GET:
            if request.GET.get('token') and request.GET.get('token') == get_token():
            # if True:
                try:
                    comb_list = json.loads(request.GET.get('comb_list'))
                except:
                    comb_list = None

                if comb_list is not None and isinstance(comb_list, list):
                    get_reserves = get_all_reserves(comb_list=comb_list)

                    if get_reserves:
                        return cors_headers_add(['actives', get_reserves])

                    else:
                        return cors_headers_add(['actives', 'null'])

            else:
                return cors_headers_add(['error', "Invalid token! Access deny!"])
        
        return cors_headers_add(['error', 'Request is incorrect!'])

# Post using for application

@method_decorator(csrf_exempt, name="dispatch")
class ProductMGMT(View):
    def post(self, request):
        if request.POST:
            validator = DataValidators()
            try:
                w_from = request.POST.get('w_from')
                w_to = request.POST.get('w_to')

                validate_warehouse = validator.is_w_valid(w_from, w_to)

                if validate_warehouse:
                    w_from = validate_warehouse.get('w_from')
                    w_to = validate_warehouse.get('w_to')

                if (w_from is None or w_from == '') and (w_to is None or w_to == ''):
                    raise Exception

            except:
                return JsonResponse({'error': 'Warehouse <TO> must be fill!'})

            if w_from == '' or w_from is None:
                app_mgmt_inc = app_management_inc(request, w_to)

                # Log
                views_logger.info(
                    "TRANSACTION: APP, " +
                    str(request.POST.get('code')) +
                    " : " +
                    str(app_mgmt_inc))

                return app_mgmt_inc


            elif w_from == w_to:
                return JsonResponse({'error': 'Cannot transfer product between same warehouses!'})

            else:
                app_mgmt = app_management(request, w_from, w_to)

                # Log
                views_logger.info(
                    "TRANSACTION: APP, " + 
                    str(request.POST.get('code')) +
                    " : " + 
                    str(app_mgmt))

                return app_mgmt
            
        return JsonResponse({'error': 'Data required!'})


# Init button in the app
@method_decorator(csrf_exempt, name="dispatch")
class AppInitProduct(View):
    def post(self, request):
        if request.POST:
            vd = DataValidators()
            
            bike_code = request.POST.get("code")

            # if bike_code is None or bike_code == "":
            if not (len(bike_code) > 8 and len(bike_code) < 20):
                return JsonResponse({'error': 'Invalid data!'})
            

            if bike_code:
                init_with_code = init_stocks_with_code(bike_code)

                if init_with_code is not None:
                    views_logger.info(
                        "TRANSACTION: APP_INIT, " + 
                        str(request.POST.get('code')) + 
                        " : " + 
                        str(init_with_code.get("success")))


            return JsonResponse(init_with_code)
        
        return JsonResponse({'error': 'Invalid data!'})


# Init button in the extension
@method_decorator(csrf_exempt, name="dispatch")
class PrestaInit(View):
    def options(self, request):
        return cors_headers_options(origin="https://3gravity.pl", to_json=['TEST', 'TEST'], post=True)


    # In post params: product_id, comb_dict
    # @method_decorator(ensure_csrf_cookie, name="dispatch")
    def post(self, request):
        def cors_headers_add(to_json=[]):
            data = JsonResponse({to_json[0]: to_json[1]})

            data["Access-Control-Allow-Origin"] = "https://3gravity.pl"
            data["Vary"] = "Origin"
            data["Access-Control-Allow-Credentials"] = "true"
            data[
                "Access-Control-Allow-Headers"] = "Origin, Access-Control-Allow-Origin, Accept, X-Requested-With, Content-Type"

            return data

        if request.POST:
            
            if request.POST.get('token') and request.POST.get('token') == get_token():
                product_id = str(request.POST.get("product_id"))
                try:
                    comb_list = json.loads(request.POST.get("comb_list"))

                    if not isinstance(comb_list, list) or len(product_id) > 5:
                        # return JsonResponse({
                        #     "error": "Invalid params was given!"
                        # })
                        return cors_headers_add(['erorr', 'Invalid params were given!']) 
                
                except Exception as e:
                    # return JsonResponse({"error": "Combinations invalid!"})
                    return cors_headers_add(['error', 'Combinations invalid!'])

                else:
                    # Calling the init main thread
                    init_all = init_product(product_id, comb_list)
                    return init_all

            else:
                # return JsonResponse({"error": "Invalid token! Access deny!"})
                return cors_headers_add(['error', 'Invalid token! Access deny!'])
        
        else:
            # return JsonResponse({"error": "Data required!"})
            return cors_headers_add(['error', 'Data required!'])


#Restore button in the app
@method_decorator(csrf_exempt, name="dispatch")
class AppPrestaRestore(View):
    def post(self, request):
        # Change to POST after commit
        if request.POST:
            restore_token = request.POST.get("restore_token")

            restore_action = cancel_action(restore_token)

            views_logger.info(
                    "TRANSACTION: APP_RESTORE, " + 
                    str(request.POST.get('restore_token')) + 
                    " : " + 
                    str(restore_action))

            if restore_action.get('success'):
                return JsonResponse({"success": "OK"})

        return JsonResponse({"error": "Impossible to restore or session doesn't exist!"})



class PrestaReset(View):
    def get(self, request):
        if request.GET:
            pr = PrestaResetHandler()
            return pr.presta_reset(request.GET)
        else:
            return JsonResponse({'error': 'Reset option is unvailable now!'})



class PrestaPrint(View):
    def options(self, request):
        return cors_headers_options(origin="https://3gravity.pl", to_json=['pass', 'pass'])

    def get(self, request):
        if request.GET:
            if request.GET.get('token') and request.GET.get('token') == get_token():
                try:
                    temp_url = orders_print(request)
                except Exception as e:
                    return cors_headers_add(['error', 'Pobieranie danych nie powiodło się!'])

                if temp_url is not None:
                    if request.GET.get('download_file') is None:
                        return cors_headers_add(['Success', temp_url])
                    else:
                        return temp_url
                else:
                    return cors_headers_add(['error', 'Pobieranie danych nie powiodło się!'])

        else:
            return cors_headers_add(['error', 'Invalid request!'])


@method_decorator(csrf_exempt, name="dispatch")
class ProductCreate(View):
    def options(self, request):
        return cors_headers_options(
            origin="https://kross.eu",
            to_json=['TEST', 'TEST'],
            post=True)


    def post(self, request):
        def cors_headers_add(to_json=[]):
            data = JsonResponse({to_json[0]: to_json[1]})

            data["Access-Control-Allow-Origin"] = "https://kross.eu"
            data["Vary"] = "Origin"
            data["Access-Control-Allow-Credentials"] = "true"
            data[
                "Access-Control-Allow-Headers"] = "Origin, Access-Control-Allow-Origin, Accept, X-Requested-With, Content-Type"

            return data

        if request.method == 'POST':
            # Serialize body
            body_to_json = json.loads(request.body)

            if body_to_json.get('token') == get_token():
                try:
                    product_data_json = body_to_json.get('product_data_json')
                    create_prod = create_product_laucher(product_data_json)

                    if create_prod.get('success') is not None:
                        return cors_headers_add(['success', create_prod])

                    else:
                        return cors_headers_add(['error', create_prod])

                except Exception as e:
                    # return JsonResponse({"error": "Combinations invalid!"})
                    return cors_headers_add(['error', str(e)])
            return cors_headers_add(['error', 'Invalid token!'])
        return cors_headers_add(['error', 'Post data was not given!'])
                    
  
