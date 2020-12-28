from django.urls import path
from .views import Notes


urlpatterns = [
    path('', Notes.as_view(), name="notes_page_url"),
]