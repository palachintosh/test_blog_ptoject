from django.contrib.auth import login
from django.http import FileResponse, JsonResponse

from bikes_monitoring.PrestaRequest.mainp.db.db_writer import ReserveBikes
from .utils import DataValidators
from .PrestaRequest.mainp.PrestaRequest import PrestaRequest
from .PrestaRequest.AP.AP_main import *
from .PrestaRequest.mainp.api_secret_key import api_secret_key
from .PrestaRequest.AP.auth_data import AUTH_DATA
from .PrestaRequest.mainp.warehouse_values import GetWarehousesValues
from .PrestaRequest.mainp.reserver import Reserve
from .utils import Logging
import datetime
import logging
import os
from mysite.celery import app
from .tasks import auto_delete_reserve
from .PrestaRequest.OrdersPrint.orders_print import OrdersPrint
from bikes_monitoring.products_create_api.create_products_api import ProductCreate



formatter = logging.Formatter("%(levelname)s: %(asctime)s - %(message)s")
tasks_base_dir = os.path.dirname(os.path.abspath(__file__))
file_handler = logging.FileHandler(tasks_base_dir + "/log/celery_tasks.log")
celery_logger = logging.getLogger('celery_tasks')
celery_logger.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
celery_logger.addHandler(file_handler)


# Main transactions handler
def product_mooving(request):
    def cors_headers_add(to_json=[]):
        data = JsonResponse({to_json[0]: to_json[1]})

        data["Access-Control-Allow-Origin"] = "https://24.kross.pl"
        data["Vary"] = "Origin"
        data["Access-Control-Allow-Credentials"] = "true"
        data[
            "Access-Control-Allow-Headers"] = "Origin, Access-Control-Allow-Origin, Accept, X-Requested-With, Content-Type"
        data["pragma"] = "no-cache"
        data["Cache-Control"] = "no-cache, no-store"

        return data

    l = Logging()

    validator = DataValidators()
    code = request.GET.get('code')

    if code is not None:
        filter_code = validator.is_code_valid(code)
    
    else: return JsonResponse({'error': 'Code must be fill!'})


    if filter_code.get('rex_code') is not None:
        request_url = "https://3gravity.pl/api/combinations/?filter[reference]=%[{}]%".format(
            filter_code.get('rex_code'))
        presta_get = PrestaRequest(api_secret_key=api_secret_key,
                                   request_url=request_url)


        # Get total quantity from stock_availables
        try:
            del_bike = presta_get.stock_parser(quantity_to_transfer=1)

            if isinstance(del_bike, dict):
                return cors_headers_add(to_json=['error', del_bike.get('error')])

            if del_bike is not None:

                # Delete one from stocks_availables
                apply_changes = presta_get.presta_put()

                if apply_changes.get('success') is not None:
                    del_from_warehouse = presta_get.warehouse_quantity_mgmt(
                        warehouse='SHOP',
                        reference=filter_code.get('rex_code'))

                    if isinstance(del_from_warehouse, dict):
                        return cors_headers_add(to_json=['error', del_from_warehouse.get('error')])

                    if del_from_warehouse is not None:
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

        except Exception as e:
            kwargs_data = {
                'DATE': str(datetime.datetime.now()),
                'ERROR': str(e),
            }

            l.logging(kwargs=kwargs_data)
            return cors_headers_add(to_json=['error', str(e)])

    return cors_headers_add(to_json=['typeError', 'Invalid code!'])


def reserve_check(phone_number, comb_url):
    comb_url = comb_url[-4:]
    pr = Reserve(api_secret_key=api_secret_key)
    check_data = {}
    check_data["comb_id"] = comb_url
    check_data["phone_number"] = phone_number
    pr.db_data = check_data

    add_reserve = pr.reserve_check()

    if add_reserve is not None:
        if add_reserve.get('Warning'):
            return add_reserve

        return comb_url
    else:
        return None


def cancel_reserve_task(task_id):
    # This construction discarding task in the worker
    revoke_task = app.control.revoke(task_id, terminate=True)

    return revoke_task




# delete from kross.pl site
def remove_with_reservation(request_get):
    def cors_headers_add(to_json=[]):
        data = JsonResponse({to_json[0]: to_json[1]})

        data["Access-Control-Allow-Origin"] = "https://24.kross.pl"
        data["Vary"] = "Origin"
        data["Access-Control-Allow-Credentials"] = "true"
        data[
            "Access-Control-Allow-Headers"] = "Origin, Access-Control-Allow-Origin, Accept, X-Requested-With, Content-Type"
        data["pragma"] = "no-cache"
        data["Cache-Control"] = "no-cache, no-store"
        return data
    
    l = Logging()
    validator = DataValidators()
    reference = validator.is_code_valid(request_get.GET.get('code'))
    r_check = str(request_get.GET.get('r_check'))
    phone_number = validator.is_phone_number_valid(request_get.GET.get('phone_number'))
    code = reference.get('rex_code')

    if r_check and code:
        request_url = "https://3gravity.pl/api/combinations/&filter[reference]=%[{}]%".format(code)
        presta_get = PrestaRequest(api_secret_key=api_secret_key,
                                   request_url=request_url)
        
        comb_url = presta_get.get_combination_url()

        if comb_url is None:
            return cors_headers_add([
                'Warning', 'UWAGA: Błędny kod produktu!'])


        check = reserve_check(phone_number, comb_url)
        
        if isinstance(check, dict):
            del_from_warehouse = presta_get.warehouse_quantity_mgmt(
                warehouse='SHOP',
                reference=code)


            if del_from_warehouse is not None and not isinstance(del_from_warehouse, dict):
                put_data = presta_get.presta_put(
                        request_url=del_from_warehouse)
                
                r = Reserve(api_secret_key=api_secret_key)
                r.db_data = {
                    'comb_id': comb_url[-4:],
                    'phone_number': phone_number
                }

                od = r.only_deactivate()

                if isinstance(od, dict):
                    if od.get('Success'):
                       cancel_reserve_task(r.r_check[3])
                    
                    if od.get('Warning'):
                        return cors_headers_add([
                'Warning', 'Rezerwacja dla klienta zamknieta albo jej nie bylo!'])


                kwargs_data = {
                    'DATE': str(datetime.datetime.now()),
                    'DELETE_BIKE': str(''),
                    'SA_PUT_STATUS': str(put_data),
                    'PUT_STATUS': str(put_data),
                    'REQUEST_WAREHOUSE_URL': str(del_from_warehouse),
                    }

                l.logging(kwargs=kwargs_data)
                return cors_headers_add(
                        to_json=['success',
                        'Rezerwacja zamknieta!'])

            else:
                return cors_headers_add([
                    'Error', 'Rezerwacja zamknieta ale wybranego produktu nie ma na stanach!'])
        else:
            return cors_headers_add([
                'Warning', 'Rezerwacja dla klienta zamknieta albo jej nie bylo!'])


def cors_headers_options(origin, to_json=[], post=False):
    data = JsonResponse(
            {to_json[0]: to_json[1]}
        )
    
    if post:
        data["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    else:
        data["Access-Control-Allow-Methods"] = "GET, OPTIONS"

    data["Access-Control-Allow-Origin"] = origin
    data["Access-Control-Allow-Credentials"] = "true"
    data["Vary"] = "Origin"
    data["Access-Control-Allow-Headers"] = "Origin, Access-Control-Allow-Origin, Accept, X-Requested-With, Content-Type"

    return data


def validate_data(request):
    validator = DataValidators()

    quantity_to_transfer = request.POST.get('quantity_to_transfer')
    code_u = validator.is_code_valid(request.POST.get('code'))



    if code_u.get('rex_code') != None:
        q_tt = validator.is_quantity_valid(quantity_to_transfer)

        if q_tt.get('valid_quantity') != None:
            quantity_to_transfer = q_tt.get('valid_quantity')
    
        return {'code': code_u.get('rex_code'), 'quantity_to_transfer': quantity_to_transfer}

    return {} 


#Products transferring
def app_management(request, w_from, w_to):
    l = Logging()
    vd = validate_data(request)

    if vd.get('code') is not None:
        try:
            presta_get = PrestaRequest(api_secret_key=api_secret_key)
            moove = presta_get.product_transfer(
                quantity_to_transfer=vd.get('quantity_to_transfer'),
                w_from=w_from,
                w_to=w_to,
                code=vd.get('code')
            )

            if moove is not None:
                data = {
                        'success': 'YES',
                        'delivery_on_warehous': 'TAK',
                        'DATE': str(datetime.datetime.now()),
                        'name': moove.get("name"),
                        'quantity': moove.get("quantity"),
                        'restore_token': presta_get.restore_id
                    }
                
                if moove.get('error') is not None:
                    data = {
                            # 'success': 'NO',
                            'error': moove.get("error"),
                            }


                l.logging(log_name='prodct_m', kwargs=data)

                return JsonResponse(data)

        except Exception as e:
            kwargs_data = {
                'DATE': str(datetime.datetime.now()),
                'ERROR': str(e),
                'NAME': vd.get('code')
            }

            l.logging(kwargs=kwargs_data)
            return JsonResponse({'error', str(e)})

    return JsonResponse({'typeError': 'Invalid code!'})


# Add products on stocks
def app_management_inc(request, w_to):
    l = Logging()
    vd = validate_data(request)

    if vd.get('code') is not None:
        try:
            presta_get = PrestaRequest(api_secret_key=api_secret_key)
            moove = presta_get.to_w_transfer(
                quantity_to_transfer=vd.get('quantity_to_transfer'),
                w_to=w_to,
                code=vd.get('code'),
            )

            if moove is not None:
                data = {
                        'success': 'YES',
                        'delivery_on_warehous': 'TAK',
                        'DATE': str(datetime.datetime.now()),
                        'name': moove.get("name"),
                        'quantity': moove.get("quantity"),
                        'restore_token': presta_get.restore_id,
                    }
                
                if moove.get('error') != None:
                    data = {
                            # 'success': 'NO',
                            'error': moove.get('error'),
                            }
                    
                
                l.logging(log_name='prodct_m', kwargs=data)
    
                return JsonResponse(data)

        except Exception as e:
            kwargs_data = {
                'DATE': str(datetime.datetime.now()),
                'ERROR': str(e),
            }

            l.logging(kwargs=kwargs_data)
            return JsonResponse({'error', str(e)})
    else:
        return JsonResponse({'typeError': 'Invalid code!'})


# Get warehouses values and return a JSON with them
# to chromExtension.
def  get_warehouses_value(input_values_dict):
    def cors_headers_add(to_json=[]):
        data = JsonResponse({to_json[0]: to_json[1]})

        data["Access-Control-Allow-Origin"] = "https://3gravity.pl"
        data["Vary"] = "Origin"
        data["Access-Control-Allow-Credentials"] = "true"
        data[
            "Access-Control-Allow-Headers"] = "Origin, Access-Control-Allow-Origin, Accept, X-Requested-With, Content-Type"

        return data
    
    response_data = {}

    if input_values_dict != None:
        getp_warehouses_value = GetWarehousesValues(api_secret_key=api_secret_key)
        
        for value in input_values_dict:
            if value != None:
                request_url = "https://3gravity.pl/api/stocks/?filter[id_product_attribute]={}".format(value)
                vget = getp_warehouses_value.get_warehouses_links(request_url)

                if vget != None:
                    get_vals = getp_warehouses_value.get_warehouses_values(vget)

                    if get_vals != None:
                        response_data.update({value: get_vals})

        return cors_headers_add(to_json=['success', response_data])


def reserve_task_create(data):
    off_time = datetime.datetime.now() + datetime.timedelta(
        hours=data.get('off_hours'))
    # off_time = datetime.datetime.now() + datetime.timedelta(
    #     minutes=data['off_hours'])

    task = auto_delete_reserve.apply_async((
        data["comb_id"],
        data["phone_number"],
        data["request_url"],
        api_secret_key,),
        eta=off_time)
    
    celery_logger.info("TRANSACTION: KROSS, " + str(task.id) + str(task.status))
    celery_logger.info(str(data["comb_id"]) + str(data["phone_number"]) + data["request_url"] + str(data.get('permanent')))

    print("+----------------------------------+")
    print(task)
    print(task.state)
    print(task.status)
    print("+--------------------------------- +")

    return task.id


# works with PS extension
def reserve_product(request_get):
    """
    The function return JSON with next information:
    * Product, that was deleted from the stock;
    * Date, when product was delete;
    * Combination.

    As well as add a specific token on product in db

    The other functions check this token, while mooving products
    and, if some products has reservation token - delete them only from SHOP.

    """
    def cors_headers_add(to_json=[]):
        data = JsonResponse({to_json[0]: to_json[1]})

        data["Access-Control-Allow-Origin"] = "https://3gravity.pl"
        data["Vary"] = "Origin"
        data["Access-Control-Allow-Credentials"] = "true"
        data[
            "Access-Control-Allow-Headers"] = "Origin, Access-Control-Allow-Origin, Accept, X-Requested-With, Content-Type"

        return data

    
    if request_get:
        validator = DataValidators()
        comb_id = validator.is_comb_value_valid(comb_id=request_get.get('comb_id'))
        phone_number = validator.is_phone_number_valid(request_get.get('phone_number'))
        username = validator.is_name_valid(username=request_get.get('reference'))

        if phone_number is None:
            return cors_headers_add(['Warning', 'Niezbedny jest numer telefonu klienta!'])
        
        db_data = dict()
        db_data["comb_id"] = str(comb_id)
        db_data["phone_number"] = str(phone_number)
        db_data["reference"] = username
        db_data["active_stamp"] = request_get.get('active_stamp')

        if request_get.get('off_time'):
            db_data["off_hours"] = int(request_get.get('off_time'))
            db_data['permanent'] = 0

        else:
            db_data['off_hours'] = 0
            db_data['permanent'] = 1


        request_url = 'https://3gravity.pl/api/combinations/{}'.format(comb_id)

        pr = Reserve(api_secret_key=api_secret_key, request_url=request_url)
        pr.db_data = db_data
        pr.url_to_delete = request_url

        if db_data["active_stamp"] == '1':
            if comb_id is not None:
                add_reserve = pr.reserve_check()

                if add_reserve is None:
                    # Make reservation
                    add_new = pr.add_new()

                    if add_new is None:
                        return cors_headers_add(['error', 'Rezerwacja nie powiodla sie!'])

                    if isinstance(add_new, dict):
                        if add_new.get('success') is not None:
                            add_reserve =  add_new

                        else:
                            return cors_headers_add([
                                list(add_new.keys())[0], add_new.get(list(add_new.keys())[0])])

                celery_logger.info("AFTER SUCCESS " + str(db_data["comb_id"]) + " " + str(db_data["phone_number"]))
                if add_reserve is not None:
                    celery_logger.info("IN SUCCESS " + str(db_data["comb_id"]) + " " + str(db_data["phone_number"]))
                    if add_reserve.get('success'):
                        if db_data["permanent"] == 0:
                            db_data["request_url"] = request_url
                            task_id = reserve_task_create(db_data)
                            celery_logger.info("IN SUCCESS " + str(db_data["comb_id"]) + str(task_id))

                            if task_id:
                                a = pr.add_task_id(
                                    task_id=task_id,
                                    phone_number=phone_number,
                                    comb_id=comb_id)

                                celery_logger.info("IN TASK " + str(db_data["comb_id"]) + str(a))


                            return cors_headers_add(['success', add_reserve])

                    if add_reserve.get('Warning'):
                        return cors_headers_add(['warning', add_reserve.get('Warning')])
                    
                    if add_reserve.get('Error'):
                        return cors_headers_add(['error', add_reserve.get('Error')])
            else:
                return cors_headers_add(['error', 'Rezerwacja nie powiodla sie!'])

        else:
            if comb_id is not None:
                try:
                    cancel_reserve = pr.deactivate()

                    if cancel_reserve is not None:
                        if cancel_reserve.get('Success'):
                            cancel_reserve_task(pr.r_check[3])

                        return cors_headers_add(['success', cancel_reserve])

                    raise Exception
                except:
                    return cors_headers_add(['Warning', 'Rezerwacji z tym numerem nie istnieje albo jest juz nie aktywna!'])

        return cors_headers_add(to_json=['error', 'Nieprawidlowe dane!'])


# Get reservation for bike ordered by phone number
def get_all_reserves(comb_list):
    res_dict = {}
    rc = Reserve(api_secret_key=api_secret_key, request_url=None)

    if comb_list:
        for comb_id in comb_list:
            get_res = rc.get_active_reservation(comb_id)

            if get_res is not None:
                res_dict[str(comb_id)] = get_res

    print(res_dict)
    return res_dict


def init_product(product_id, comb_list):
    def cors_headers_add(to_json=[]):
        data = JsonResponse({to_json[0]: to_json[1]})

        data["Access-Control-Allow-Origin"] = "https://3gravity.pl"
        data["Vary"] = "Origin"
        data["Access-Control-Allow-Credentials"] = "true"
        data[
            "Access-Control-Allow-Headers"] = "Origin, Access-Control-Allow-Origin, Accept, X-Requested-With, Content-Type"

        return data

    ap = APStockWorker(login=AUTH_DATA[0], password=AUTH_DATA[1])
    ap.product_id = product_id
    init_all = ap.sw_main_cycle(product_id=product_id, comb_list=comb_list, force=True)
  
    return cors_headers_add(['success', init_all])


def init_stocks_with_code(code):
    pr = PrestaRequest(api_secret_key=api_secret_key)
    ap = APStockWorker(login=AUTH_DATA[0], password=AUTH_DATA[1])
    
    product_dict = pr.get_init_data(code)


    if isinstance(product_dict, dict):
        product_id = list(product_dict.keys())[0]
        comb_list = product_dict.get(product_id)

        if product_id is None or comb_list is None:
            return {"error": "Unable to detect product and/or combinations!"}

        init_all = ap.sw_main_cycle(
            product_id=product_id,
            comb_list=comb_list,
            force=True
        )

        if init_all is None:
            return {"error": "Unexpected error while init stocks!"}

        return init_all


    return {"error": 'Code \'{}\' is not associate with no one product!'.format(code)}

    # 1. Combination for code -> comb_list["comb_id"]
    # 2. Product id


def cancel_action(restore_token):
    pr = PrestaRequest(api_secret_key=api_secret_key)
    restore_action = pr.restore_last_action(restore_id=restore_token)

    return restore_action



# Make the pdf file with orders
def orders_print(request):
    ord = OrdersPrint(api_secret_key=api_secret_key)
    pdf_dict = []

    if request.GET.get('download_file') is not None:
        file_response = FileResponse(
            open(os.path.join(ord.base_dir, 'print/' + request.GET.get('download_file')), 'rb')
        )

        return file_response


    if request.GET.get('days_ago') is not None:
        int_days = 0
        try:
            int_days = int(request.GET.get('days_ago'))
        except:
            return {'error': 'Days range is incorrect!'}
        
        pdf_dict = ord.collect_orders_by_date(days_ago=int_days)
      
    
    elif request.GET.get('days_date') is not None:
        date_range = request.GET.get('days_date')

        try:
            to_date = datetime.datetime.strptime(date_range, '%Y-%m-%d').date()

            days_delta = datetime.datetime.today().date() - to_date
            int_days = days_delta.days

        except:
            return {'error': 'Date has an incorrect format!'}
        
        pdf_dict = ord.collect_orders_by_date(days_ago=int_days)
      
    
    elif request.GET.get('orders_range') is not None:
        orders_range = request.GET.get('orders_range').split(',')
        
        pdf_dict = ord.collect_by_limit_url(
            limit_id_start=orders_range[0],
            limit_id_end=orders_range[1])


    if pdf_dict:
        create_pdf = ord.to_pdf(pdf_dict, ord.total_bikes_to_pickup)
        return create_pdf

    else:
        return {'error': 'Kartka nie została wygenerowana!'}


def create_product_laucher(future_product_data):
    init_create = ProductCreate(api_secret_key=api_secret_key)
    create_prod = init_create.edit_blank_xml(future_product_data)

    return create_prod