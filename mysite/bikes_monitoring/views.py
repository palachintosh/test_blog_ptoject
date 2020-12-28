from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse

from .utils import *



# Create your views here.

class BikeCheck(LoginRequiredMixin, View):
    def get(self, request):
        return HttpResponse("None")
    
    def post(self, request):
        if request.POST:
            pass