"""Users app URLs"""
from django.urls import path
from . import views

app_name = 'users_app'

urlpatterns = [
    path('', views.user_list, name='list'),
    path('add/', views.user_create, name='create'),
]
