from django.shortcuts import render
from django.http import HttpResponse
import os.path

# Create your views here.

def post_list(request):
	FILENAME = open(os.path.abspath('webexample/index.html'))
	return HttpResponse(FILENAME)