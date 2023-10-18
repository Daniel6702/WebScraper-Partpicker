from django.urls import path
from .views import scraper_view

urlpatterns = [
    path('', scraper_view, name='scraper_view'),
]