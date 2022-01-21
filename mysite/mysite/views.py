from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.gis.geoip2 import GeoIP2

from .check_region import RedirectToPage



def based_blog(request):

    get_user_ip = request.META.get("REMOTE_ADDR")
    # get_user_ip = '194.28.49.250' #PL
    # get_user_ip = '185.61.92.228' #RU

    country = request.session.get('geoip2')

    if country is None:
        return redirect('home_blog_page', permanent=True)

    if country.get('country_code') == 'XX':
        r = RedirectToPage(user_ip=get_user_ip)
        user_region = r.return_user_zone()
        country.update({'country_code': user_region})

    # get_user_cookie = request.session.get('geoip2')
    
    if country.get('country_code') == "PL":
        return redirect('pl_home_blog_page', permanent=True)
    else:
        return redirect('home_blog_page', permanent=True)