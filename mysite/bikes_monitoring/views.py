from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse

from .PrestaRequest.mainp.PrestaRequest import PrestaRequest

from .utils import CodeValidators

try:
    from .PrestaRequest.mainp.api_secret_key import api_secret_key
except:
    ImportError("Cannot import API key!")

# Create your views here.

class BikeCheck(View):
    def get(self, request):
        number_validator = CodeValidators()
        filter_code = number_validator.is_code_valid(request)

        if filter_code.get('rex_code') != None:
            request_url = "https://3gravity.pl/api/combinations/&filter[reference]={}".format(filter_code.get('rex_code'))
            presta_get = PrestaRequest(api_secret_key=api_secret_key, request_url=request_url)
            
            # Get total quantity from stock_availables
            try:
                del_bike = presta_get.stock_parser()
                print("DELETE BIKE BY STOCK", del_bike)

                if del_bike != None:
                    # Delete one from stocks_availables
                    apply_changes = presta_get.presta_put()
                    
                    print(apply_changes)
                    if apply_changes == 'All data has been updated!':
                        del_from_warehouse = presta_get.warehouse_quantity_mgmt(warehouse='SHOP', reference=filter_code.get('rex_code'))

                        print(del_from_warehouse)

                        if del_from_warehouse != None:
                            presta_get.presta_put(request_url=del_from_warehouse)
                            data = {
                                'success': 'All data has been updated',
                            }
                            return JsonResponse(data)


            except Exception as e:
                return JsonResponse({'Error': e})
            
        data = {
            'TypeError': 'Invalid code!',
        }

        return JsonResponse(data)



    def post(self, request):
        if request.POST:
            return HttpResponse("Frame number is required!")