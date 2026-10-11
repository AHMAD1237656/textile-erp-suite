"""Inventory app URLs"""
from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list, name='list'),
    path('add-stock/', views.add_stock, name='add_stock'),
    path('transfers/', views.stock_transfer, name='transfers'),
    path('api/dashboard/', views.api_dashboard_inventory, name='dashboard_api'),
    path('api/low-stock-alerts/', views.api_low_stock_alerts, name='low_stock_alerts'),
]
