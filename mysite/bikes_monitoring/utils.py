import re
import base64


class CodeValidators:
    def is_code_valid(self, bike_code):
        
        bike_code = str(bike_code)

        if len(bike_code) != 0:
            try:
                data = {}
                rex = re.search("^[a-zA-Z0-9]{7,20}", bike_code)

                print("REX: ", rex)

                if rex.group() == bike_code:
                    data.update({'rex_code': bike_code})
                    return data
                else:
                    raise Warning('The code may contains not code!')

            except:
                data = {}
                code = base64.b64encode(bike_code.encode())
                data.update({'encode_code': str(code)})

                return data

        else: 
            return {'error': "Cannot get 'bike_code', from request!"}



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
