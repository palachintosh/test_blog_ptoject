from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from .PrestaRequest.mainp.PrestaRequest import PrestaRequest
from .utils import CodeValidators

import os.path
import datetime

try:
    from .PrestaRequest.mainp.api_secret_key import api_secret_key
except:
    ImportError("Cannot import API key!")


# Create your views here.

def logging(log_name=None, **kwargs):

    if not log_name:
        log_name = "PRLog.txt"

    param_dict = kwargs.get('kwargs')
    
    try:
        with open(log_name, 'a') as f:
            for i in param_dict.items():
                print(i[0] + ': ' + i[1], file=f)
    
    except:
        with open(log_name) as f:
            for i in param_dict.items():
                print(i[0] + ': ' + i[1], file=f)




class BikeCheck(View):
# ==========================================
# |         Works only on kross.pl         |
# ==========================================

    def options(self, request):
        def cors_headers_add(to_json=[]):
            data = JsonResponse(
                {to_json[0]: to_json[1]}
            )

            data["Access-Control-Allow-Origin"] = "http://my.kross.pl"
            data["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            data["Access-Control-Allow-Credentials"] = "true"
            data["Vary"] = "Origin"
            data["Access-Control-Allow-Headers"] = "Origin, Access-Control-Allow-Origin, Accept, X-Requested-With, Content-Type"

            return data
        
        return cors_headers_add(to_json=['TEST', 'TEST'])

    def get(self, request):

        def cors_headers_add(to_json=[]):
            data = JsonResponse(
                {to_json[0]: to_json[1]}
            )

            data["Access-Control-Allow-Origin"] = "https://24.kross.pl"
            data["Vary"] = "Origin"
            data["Access-Control-Allow-Credentials"] = "true"
            data["Access-Control-Allow-Headers"] = "Origin, Access-Control-Allow-Origin, Accept, X-Requested-With, Content-Type"

            return data

        with open('log_method.txt', 'w') as f:
            print(request.method + str(datetime.datetime.now()), file=f)

        number_validator = CodeValidators()
        filter_code = number_validator.is_code_valid(request)

        if filter_code.get('rex_code') != None:
            request_url = "https://3gravity.pl/api/combinations/&filter[reference]={}".format(filter_code.get('rex_code'))
            presta_get = PrestaRequest(api_secret_key=api_secret_key, request_url=request_url)
            
            # Get total quantity from stock_availables
            try:
                del_bike = presta_get.stock_parser()
                # print("DELETE BIKE BY STOCK", del_bike)

                if del_bike != None:

                    # Delete one from stocks_availables
                    apply_changes = presta_get.presta_put()
                    print(apply_changes.get('success'))

                    if apply_changes.get('success') != None:
                        del_from_warehouse = presta_get.warehouse_quantity_mgmt(warehouse='SHOP', reference=filter_code.get('rex_code'))

                        # print(del_from_warehouse)

                        if del_from_warehouse != None:
                            put_data = presta_get.presta_put(request_url=del_from_warehouse)
                            
                            kwargs_data = {
                                'DATE': str(datetime.datetime.now()),
                                'DELETE_BIKE': del_bike,
                                'SA_PUT_STATUS': str(apply_changes),
                                'PUT_STATUS': str(put_data),
                                'REQUEST_WAREHOUSE_URL': del_from_warehouse,
                            }

                            logging(kwargs=kwargs_data)
                            return cors_headers_add(to_json=['success', filter_code.get('rex_code')])

                        else:
                            pass


            except Exception as e:
                kwargs_data = {
                    'DATE': str(datetime.datetime.now()),
                    'ERROR': str(e),
                }

                logging(kwargs=kwargs_data)
                return cors_headers_add(to_json=['error', str(e)])

        return cors_headers_add(to_json=['typeError', 'Invalid code!'])

# ==========================================
# |         Works only on kross.pl         |
# ==========================================


# Post using for application

    def post(self, request):
        if request.POST:
            return JsonResponse({'error': 'Post is not allow!'})