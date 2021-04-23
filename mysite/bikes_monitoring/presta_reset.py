from django.http import JsonResponse
import requests
from .utils import DataValidators
from .PrestaRequest.mainp.PrestaRequest import PrestaRequest
from .PrestaRequest.mainp.api_secret_key import api_secret_key
from .utils import Logging
import datetime


# The module for reset selected warehouse
# Need password for activate
# Use this with careful!

class PrestaResetHandler:
    def presta_reset(self):
        pass