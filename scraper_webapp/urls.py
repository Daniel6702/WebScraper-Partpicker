from django.urls import path
from . import views

urlpatterns = [
    path('', views.pc_builder, name='pc_builder'),
    # add your other paths here
]