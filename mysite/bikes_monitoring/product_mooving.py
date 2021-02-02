from django.http import JsonResponse
from .utils import DataValidators
from .PrestaRequest.mainp.PrestaRequest import PrestaRequest
from .PrestaRequest.mainp.api_secret_key import api_secret_key
from .utils import Logging
import datetime


def product_mooving(request):

    def cors_headers_add(to_json=[]):
        data = JsonResponse({to_json[0]: to_json[1]})

        data["Access-Control-Allow-Origin"] = "https://24.kross.pl"
        data["Vary"] = "Origin"
        data["Access-Control-Allow-Credentials"] = "true"
        data[
            "Access-Control-Allow-Headers"] = "Origin, Access-Control-Allow-Origin, Accept, X-Requested-With, Content-Type"

        return data

    l = Logging()

    with open('log_method.txt', 'w') as f:
        print(request.method + str(datetime.datetime.now()), file=f)

    number_validator = DataValidators()
    filter_code = number_validator.is_code_valid(request.GET.get('code'))

    if filter_code.get('rex_code') != None:
        request_url = "https://3gravity.pl/api/combinations/&filter[reference]={}".format(
            filter_code.get('rex_code'))
        presta_get = PrestaRequest(api_secret_key=api_secret_key,
                                   request_url=request_url)

        # Get total quantity from stock_availables
        try:
            del_bike = presta_get.stock_parser(quantity_to_transfer=0)
            # print("DELETE BIKE BY STOCK", del_bike)

            if del_bike != None:

                # Delete one from stocks_availables
                apply_changes = presta_get.presta_put()
                print(apply_changes.get('success'))

                if apply_changes.get('success') != None:
                    del_from_warehouse = presta_get.warehouse_quantity_mgmt(
                        warehouse='SHOP',
                        reference=filter_code.get('rex_code'))

                    # print(del_from_warehouse)

                    if del_from_warehouse != None:
                        put_data = presta_get.presta_put(
                            request_url=del_from_warehouse)

                        kwargs_data = {
                            'DATE': str(datetime.datetime.now()),
                            'DELETE_BIKE': str(del_bike),
                            'SA_PUT_STATUS': str(apply_changes),
                            'PUT_STATUS': str(put_data),
                            'REQUEST_WAREHOUSE_URL': str(del_from_warehouse),
                        }

                        l.logging(kwargs=kwargs_data)
                        return cors_headers_add(
                            to_json=['success',
                                     filter_code.get('rex_code')])

                    else:
                        pass

        except Exception as e:
            kwargs_data = {
                'DATE': str(datetime.datetime.now()),
                'ERROR': str(e),
            }

            l.logging(kwargs=kwargs_data)
            return cors_headers_add(to_json=['error', str(e)])

    return cors_headers_add(to_json=['typeError', 'Invalid code!'])


def cors_headers_options(to_json=[]):
    data = JsonResponse(
            {to_json[0]: to_json[1]}
        )

    data["Access-Control-Allow-Origin"] = "http://24.kross.pl"
    data["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    data["Access-Control-Allow-Credentials"] = "true"
    data["Vary"] = "Origin"
    data["Access-Control-Allow-Headers"] = "Origin, Access-Control-Allow-Origin, Accept, X-Requested-With, Content-Type"

    return data


def app_management(request):
    l = Logging()

    validator = DataValidators()
    code_u = request.POST.get('code')
    valid_code = validator.is_code_valid(code_u)

    quantity_to_transfer = int(request.POST.get('quantity_to_transfer'))

    validate_quantity = validator.is_quantity_valid(quantity_to_transfer)
    if validate_quantity.get('valid_quantity'):
        quantity_to_transfer = validate_quantity.get('valid_quantity')
    else:
        return {'error': validate_quantity.get('error')}

    w_from = request.POST.get('w_from')
    w_to = request.POST.get('w_to')

    with open("POST.txt", "w") as f:
        print(w_from, w_to, code_u, valid_code.get('rex_code'), valid_code, quantity_to_transfer, file=f)

    print(quantity_to_transfer, w_from, w_to)

    if valid_code != None:
        try:
            if valid_code.get('rex_code') != None:
                code_u = valid_code.get('rex_code')
            
            else:
                return JsonResponse({'error': str(valid_code)})




            presta_get = PrestaRequest(api_secret_key=api_secret_key)
            moove = presta_get.product_transfer(
                quantity_to_transfer=quantity_to_transfer,
                w_from=w_from,
                w_to=w_to,
                code=code_u
            )

            if moove != None:
                print(moove.get('error'))
                if moove.get('error') == None:
                    data = {
                        'success': 'YES',
                        'delivery_on_warehouse': 'YES',
                        'DATE': str(datetime.datetime.now())
                    }

                    l.logging(log_name='app_log.txt', kwargs=data)
                
                    return JsonResponse(moove)
                else:
                    return JsonResponse({'error': 'Check product code and try again!'})

        except Exception as e:
            kwargs_data = {
                'DATE': str(datetime.datetime.now()),
                'ERROR': str(e),
            }

            l.logging(kwargs=kwargs_data)
            return JsonResponse({'error', str(e)})

    return JsonResponse({'typeError', 'Invalid code!'})


def app_management_inc(request):

    l = Logging()
    validator = DataValidators()

    code_u = request.POST.get('code')
    valid_code = validator.is_code_valid(code_u)

    quantity_to_transfer = int(request.POST.get('quantity_to_transfer'))
    w_from = request.POST.get('w_from')
    w_to = request.POST.get('w_to')

    validate_warehouse = validator.is_w_valid(w_from, w_to)
    validate_quantity = validator.is_quantity_valid(quantity_to_transfer)


    if validate_quantity.get('valid_quantity'):
        quantity_to_transfer = validate_quantity.get('valid_quantity')
    else:
        return {'error': validate_quantity.get('error')}

    if validate_warehouse:
        w_from = validate_warehouse.get('w_from')
        w_to = validate_warehouse.get('w_to')

    print(quantity_to_transfer, w_from, code_u, w_to)

    if valid_code != None:
        try:
            if valid_code.get('rex_code') != None:
                code_u = valid_code.get('rex_code')
            else:
                return JsonResponse({'error': str(valid_code)})

            presta_get = PrestaRequest(api_secret_key=api_secret_key)
            moove = presta_get.to_w_transfer(
                quantity_to_transfer=quantity_to_transfer,
                w_to=w_to,
                # code=filter_code.get('rex_code')
                code=code_u
            )

            if moove != None:
                print(moove.get('error'))
                if moove.get('error') == None:
                    data = {
                        'success': 'YES',
                        'delivery_on_warehouse': 'YES',
                        'DATE': str(datetime.datetime.now())
                    }

                    l.logging(log_name='app_log.txt', kwargs=data)
                
                    return JsonResponse(moove)
                else:
                    return JsonResponse({'error': 'Check product code and try again!'})

        except Exception as e:
            kwargs_data = {
                'DATE': str(datetime.datetime.now()),
                'ERROR': str(e),
            }

            l.logging(kwargs=kwargs_data)
            return JsonResponse({'error', str(e)})
    else:
        return JsonResponse({'typeError', 'Invalid code!'})

