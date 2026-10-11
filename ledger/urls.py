"""Ledger app URLs"""
from django.urls import path
from . import views

app_name = 'ledger'

urlpatterns = [
    path('', views.ledger_list, name='list'),
    path('<int:client_id>/', views.ledger_detail, name='detail'),
]
