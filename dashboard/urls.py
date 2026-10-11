"""Dashboard app URLs"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/kpis/', views.api_kpis, name='api_kpis'),
    path('api/dashboard/kpis/', views.api_kpis, name='api_dashboard_kpis'),
    path('api/charts/', views.api_charts, name='api_charts'),
    path('api/analytics/', views.api_analytics, name='api_analytics'),
    path('dashboard/api/analytics/', views.api_analytics, name='api_analytics_alias'),
]
