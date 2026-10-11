"""Invoices app URLs"""
from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    path('', views.invoice_list, name='list'),
    path('builder/', views.invoice_builder, name='builder'),
]
