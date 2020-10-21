# Check user region

# If region is .ru or .ua, then redirect to app /ru
# Else redirect to .pl zone

from django.contrib.gis.geoip2 import GeoIP2
from django.shortcuts import redirect


class RedirectToPage:
    def __init__(self, user_ip=None, switcher_status=1, request=None):
        self.user_ip = user_ip
        self.switcher_status = switcher_status
        self.request = request

    def return_user_zone(self):
        g = GeoIP2()

        try:
            get_user_ip_zone = g.country_code(self.user_ip)
            return get_user_ip_zone
        except:
            return 'RU'