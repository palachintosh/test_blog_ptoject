from django.http import HttpResponse
from django.shortcuts import redirect

def based_blog(request):
    return redirect('home_blog_page', permanent=True)
