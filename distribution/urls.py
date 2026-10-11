"""Distribution app URLs"""
from django.urls import path
from . import views

app_name = 'distribution'

urlpatterns = [
    path('', views.distribution_list, name='list'),
    path('dispatch/', views.distribution_create, name='create'),
]
