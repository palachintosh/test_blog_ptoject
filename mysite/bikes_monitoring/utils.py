import re
import base64


class CodeValidators:
    def is_code_valid(self, request):

        if len(request.GET) != 0:
            try:
                data = {}
                bike_code = str(request.GET.get('code'))
                rex = re.search("^[a-zA-Z0-9]{7,20}", bike_code)

                print("REX: ", rex)

                if rex.group() == bike_code:
                    data.update({'rex_code': bike_code})
                    return data
                else:
                    raise Warning('The code may contains not code!')

            except:
                data = {}
                bike_code = str(request.GET.get('code'))
                code = base64.b64encode(bike_code.encode())
                data.update({'encode_code': str(code)})

                return data

        else: 
            return "Cannot get 'bike_code', from request!"



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
