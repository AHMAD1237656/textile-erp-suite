"""
Dashboard app views – Executive KPI metrics & chart data endpoints
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

SAMPLE_KPIS = {
    'today_sales': 2840000,
    'today_sales_trend': '+12.4%',
    'today_sales_trend_up': True,
    'receivables': 18450000,
    'receivables_trend': '+3.2%',
    'payables': 9200000,
    'payables_trend': '-5.1%',
    'stock_value': 42800000,
    'stock_trend': '+1.8%',
    'incoming_containers': 4,
    'cash_balance': 6350000,
    'low_stock_count': 7,
    'overdue_invoices_count': 12,
}

SAMPLE_CONTAINERS = [
    {'number': 'MSCU-782194', 'origin': 'Shenzhen, CN', 'eta': '2024-10-14', 'status': 'Customs', 'items': '65W Chargers, HDMI Cables', 'badge': 'warning'},
    {'number': 'OOLU-441892', 'origin': 'Ningbo, CN', 'eta': '2024-10-18', 'status': 'At Sea', 'items': 'DDR4 RAM, NVMe SSDs', 'badge': 'info'},
    {'number': 'CMAU-992140', 'origin': 'Shanghai, CN', 'eta': '2024-10-22', 'status': 'Dispatched', 'items': 'Ethernet Switches, Hubs', 'badge': 'secondary'},
    {'number': 'EGLV-112048', 'origin': 'Hong Kong', 'eta': '2024-10-28', 'status': 'Port Clearance', 'items': 'Power Banks, Type-C Cables', 'badge': 'primary'},
]

SAMPLE_LOW_STOCK = [
    {'sku': 'RAM-DDR4-16G', 'name': 'DDR4 16GB 3200MHz RAM', 'stock': 8, 'min_stock': 50, 'unit': 'Pcs'},
    {'sku': 'CBL-TYCA-001', 'name': 'Type-C to A Cable 1m 3A', 'stock': 12, 'min_stock': 100, 'unit': 'Pcs'},
    {'sku': 'SW-ETH-8P', 'name': 'Ethernet Switch 8-Port', 'stock': 28, 'min_stock': 40, 'unit': 'Pcs'},
    {'sku': 'SSD-1TB-NVM', 'name': 'NVMe SSD 1TB Gen4', 'stock': 42, 'min_stock': 60, 'unit': 'Pcs'},
]

def index(request):
    """Dashboard executive overview page"""
    context = {
        'kpis': SAMPLE_KPIS,
        'containers': SAMPLE_CONTAINERS,
        'low_stock_items': SAMPLE_LOW_STOCK,
        'today_sales': '₨ 2,840,000',
        'receivables': '₨ 18,450,000',
        'stock_value': '₨ 42,800,000',
        'containers_count': 4,
    }
    return render(request, 'dashboard/index.html', context)

def api_kpis(request):
    """JSON API endpoint returning real-time KPI metrics"""
    return JsonResponse(SAMPLE_KPIS)

def api_charts(request):
    """JSON API endpoint returning chart data for charts"""
    period = request.GET.get('period', 'daily')
    data = {
        'period': period,
        'sales_trend': [1200000, 1850000, 1320000, 2400000, 2840000, 1900000, 1100000],
        'purchase_trend': [900000, 1100000, 800000, 1600000, 1200000, 1400000, 700000],
        'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    }
    return JsonResponse(data)
