from django.shortcuts import render
from blog.views import *
from django.views.generic import View
from blog.models import Post
from django.http import JsonResponse

# Create your views here.


class PostListPL(View):
    model = Post

    def get(self, request):
        language_var = 1
        posts = self.model.objects.filter(lang_filter="PL")
        return render(request, 'blog_pl/index_pl.html', locals())


class AboutBlogPL(View):
    def get(self, request):
        return render(request, 'blog_pl/about_blog_pl.html')

class ChangeLGPL(View):
    def get(self, request):
        checkbox_status = request.GET.get('checkbox_status')
        geoip_country_code = request.session.get('geoip2')
        checkbox_country_code = request.GET.get('checkbox_country_code')
        check_change = None

        if checkbox_country_code == geoip_country_code.get('country_code'):
            redirect_url = 'None'
            data = {
                'redirect': redirect_url,
                'check_change': check_change,
            }

            return JsonResponse(data)

        elif checkbox_country_code == 'PL' and geoip_country_code.get('country_code') == 'RU':
            redirect_url = redirect('pl_home_blog_page')
            geoip_country_code.update({'country_code': checkbox_country_code})
            check_change = 'ON'

        elif checkbox_country_code == 'RU' and geoip_country_code.get('country_code') == 'PL':
            redirect_url = redirect('home_blog_page')
            geoip_country_code.update({'country_code': checkbox_country_code})
            check_change = 'OFF'

        else:
            redirect_url = redirect('home_blog_page')

        data = {
            'redirect': redirect_url.url,
            'check_change': check_change,
        }

        return JsonResponse(data)
