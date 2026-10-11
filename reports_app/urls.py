"""Reports app URLs"""
from django.urls import path
from . import views

app_name = 'reports_app'

urlpatterns = [
    path('', views.reports_index, name='index'),
    path('api/data/', views.api_report_data, name='api_data'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('export/excel/', views.export_excel, name='export_excel'),
]
