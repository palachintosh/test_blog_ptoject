from django.views.generic import View
from django.http import JsonResponse


#class add cookie node with theme identificator

class ChangeTheme(View):
    def get(self, request):
        get_theme_key = request.session.get('theme_key') #from session
        get_current_theme = request.GET.get('current_theme') #from ajax request
        data = {
            'response_theme_key': get_theme_key,
        }
        print(get_current_theme)


        if get_theme_key:
            if get_current_theme == 'original-theme' and get_theme_key == 'original_theme':
                request.session['theme_key'] = 'dark_theme'
            
            elif get_current_theme == 'dark-theme' and get_theme_key == 'dark_theme':
                request.session['theme_key'] = 'original_theme'
            
            else:
                return JsonResponse(data)

            request.session.modified = True
            get_theme_key = request.session.get('theme_key')
            data.update({'response_theme_key': get_theme_key})

            return JsonResponse(data)

        else:
            request.session['theme_key'] = 'dark_theme'
            request.session.modified = True
            get_theme_key = request.session.get('theme_key')
            data.update({'response_theme_key': get_theme_key})

            return JsonResponse(data)