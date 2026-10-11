"""Purchases app URLs"""
from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    path('', views.purchase_list, name='list'),
    path('new/', views.purchase_create, name='create'),
    path('<int:pk>/', views.purchase_detail, name='detail'),
]
