from django.urls import path
from .views import LikeResponse
from .views import LikeCheck

urlpatterns = [
    path('like_response/', LikeResponse.as_view(), name="like_response_url"),
    path('like_check/', LikeCheck.as_view(), name="like_check_url"),
]