"""Products app URLs"""
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('',                  views.product_list,   name='list'),
    path('import/',           views.product_import, name='import'),
    path('import/sample/',    views.product_import_sample, name='import_sample'),
    path('add/',              views.product_create,  name='create'),
    path('<int:pk>/',         views.product_detail,  name='detail'),
    path('<int:pk>/qrcode/',  views.product_qr_code, name='product_qr_code'),
    path('<int:pk>/edit/',    views.product_edit,    name='edit'),
    path('<int:pk>/delete/',  views.product_delete,  name='delete'),
    # JSON API
    path('api/',              views.api_products,       name='api_list'),
    path('api/search/',       views.api_product_search, name='api_search'),
]
