import re
import base64


class DataValidators:
    def is_code_valid(self, bike_code):
        
        bike_code = str(bike_code)

        if len(bike_code) != 0:
            try:
                data = {}
                rex = re.search("^[a-zA-Z0-9]{7,20}", bike_code)

                print("REX: ", rex)
                
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
        if w_from != None or w_from != '':
            if len(w_from) <= 5 and len(w_to) <= 5:
                try:
                    str(w_from)
                    str(w_to)
                    return {'w_from': w_from, 'w_to': w_to}
        
                except Exception as e:
                    return {'error': str(e)}
        else:
            return None
    

    def is_quantity_valid(self, quantity_to_transfer):
        if quantity_to_transfer >= 0:
            return {'valid_quantity': quantity_to_transfer}

        return {'error': 'Quantity must be positive!'}






class Logging:
    def logging(self, log_name=None, **kwargs):

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
