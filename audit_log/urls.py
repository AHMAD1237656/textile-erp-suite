from django.urls import path

from . import views

app_name = 'audit_log'

urlpatterns = [
    path('', views.activity_list, name='activity_list'),
]
