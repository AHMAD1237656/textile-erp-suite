"""Roles app URLs"""
from django.urls import path
from . import views

app_name = 'roles'

urlpatterns = [
    path('', views.roles_matrix, name='matrix'),
    path('api/save/', views.api_save_permissions, name='api_save'),
]
