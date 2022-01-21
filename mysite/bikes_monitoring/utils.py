import re
import base64


class DataValidators:
    def is_code_valid(self, bike_code):

        if len(bike_code) != 0:
            try:
                data = {}
                rex = re.search("^[a-zA-Z0-9]{7,20}", str(bike_code))

                if rex != None:
                    if rex.group() == bike_code:
                        data.update({'rex_code': bike_code})
                        return data
                else:
                    raise Warning('The code may contains not code!')

            except Warning as w:
                data = {}
                code = base64.b64encode(bike_code.encode()).decode()
                data.update({'encode_code': str(code), 'warning': str(w)})

                return data

        else:
            return {'error': "Cannot get 'bike_code', from request!"}


    def is_w_valid(self, w_from, w_to):
        if (w_to != None or w_to != ''):
            try:
                str(w_to)
                if w_from != None or w_from != '':
                    str(w_from)
                return {'w_from': w_from, 'w_to': w_to}
            except Exception as e:
                return {'error': str(e)}

        else:
            return None


    def is_quantity_valid(self, quantity_to_transfer):

        valid_data = {'valid_quantity': quantity_to_transfer}

        try:
            if int(quantity_to_transfer) >= 0:
                valid_data.update({'valid_quantity': int(quantity_to_transfer)})
                return valid_data

            else:
                quantity_to_transfer = 0
                valid_data.update({'valid_quantity': quantity_to_transfer})
                return valid_data
        except:
            return {'error': 'Quantity must be positive!'}


    def is_comb_value_valid(self, comb_id):
        if comb_id is not None:
            if len(comb_id) >= 2 and len(comb_id) <= 5:
                return comb_id
        else:
            return None


    def is_phone_number_valid(self, phone_number):
        try:
            phone_num = len(str(phone_number))
            if phone_num >= 6 and phone_num <= 12:
                return phone_number
        
        except:
            return None

    
    def is_name_valid(self, username='') -> str:
        if username and not username.isalnum():
            new_username = ''.join(i for i in username if i.isalnum() or i == ' ')
            return new_username
        
        elif len(username) > 50:
            return ''

        else:
            return username


class Logging:
    def logging(self, log_name=None, **kwargs):

        if not log_name:
            log_name = "PRLog.txt"

        param_dict = kwargs.get('kwargs')

        try:
            with open(log_name, 'a') as f:
                for i in param_dict.items():
                    print(str(i[0]) + ': ' + str(i[1]), file=f)

        except:
            with open(log_name) as f:
                for i in param_dict.items():
                    print(str(i[0]) + ': ' + str(i[1]), file=f)
