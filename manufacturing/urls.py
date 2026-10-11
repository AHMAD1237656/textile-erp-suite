"""Manufacturing app URLs"""
from django.urls import path
from . import views

app_name = 'manufacturing'

urlpatterns = [
    path('', views.manufacturing_list, name='list'),
    path('new-order/', views.manufacturing_create, name='create'),
]
