"""
Dashboard app views – Executive KPI metrics & chart data endpoints
"""
from collections import defaultdict
from datetime import date
from decimal import Decimal

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum

from products.models import Product

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


def api_analytics(request):
    """Return monthly sales/dispatch trends and live stock totals by category."""
    from distribution.views import SAMPLE_DISPATCHES
    from sales.views import SAMPLE_SALES

    monthly = defaultdict(lambda: {
        'sales': Decimal('0'),
        'dispatches': 0,
    })
    for sale in SAMPLE_SALES:
        sale_date = date.fromisoformat(str(sale['date'])[:10])
        monthly[sale_date.strftime('%Y-%m')]['sales'] += Decimal(
            str(sale['total_amount'])
        )
    for dispatch in SAMPLE_DISPATCHES:
        if dispatch.get('status') not in {
            'in_transit', 'out_for_delivery', 'delivered',
        }:
            continue
        dispatch_date = date.fromisoformat(str(dispatch['date'])[:10])
        monthly[dispatch_date.strftime('%Y-%m')]['dispatches'] += int(
            dispatch.get('boxes', 0)
        )

    months = sorted(monthly)
    category_stock = (
        Product.objects.filter(is_deleted=False, status='active')
        .values('category__name')
        .annotate(stock=Sum('current_stock'), products=Count('pk'))
        .order_by('category__name')
    )
    categories = [
        {
            'name': entry['category__name'] or 'Uncategorized',
            'stock': float(entry['stock'] or 0),
            'products': entry['products'],
        }
        for entry in category_stock
    ]

    return JsonResponse({
        'monthly': {
            'labels': [
                date.fromisoformat(f'{month}-01').strftime('%b %Y')
                for month in months
            ],
            'sales': [float(monthly[month]['sales']) for month in months],
            'dispatches': [monthly[month]['dispatches'] for month in months],
        },
        'inventory_categories': categories,
    })
