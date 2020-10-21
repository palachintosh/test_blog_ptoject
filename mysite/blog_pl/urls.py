from django.urls import path
from .views import *


urlpatterns = [
    path('', PostListPL.as_view(), name="pl_home_blog_page"),
    path('about_pl_blog/', AboutBlogPL.as_view(), name="about_blog_url_pl"),
    path('change_language/pl/', ChangeLGPL.as_view(), name="change_lang_ajax_url_pl"),
]