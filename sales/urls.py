"""Sales app URLs"""
from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sales_list, name='list'),
    path('new/', views.sales_create, name='create'),
    path('<int:pk>/', views.sales_detail, name='detail'),
    path('api/', views.api_sales, name='api_list'),

    # Client Management
    path('clients/', views.clients_list, name='clients'),
    path('clients/create/', views.clients_create, name='clients_create'),
    path('api/clients/', views.api_clients, name='api_clients'),
]
