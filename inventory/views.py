"""
Inventory app views – Warehouse stocks, batch movements, adjustments and reorders
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import models
from django.views.decorators.http import require_GET

from products.models import Product

SAMPLE_INVENTORY = [
    {
        'id': 1, 'sku': 'CHG-65W-001', 'name': 'USB-C 65W GaN Charger',
        'category': 'Chargers', 'warehouse': 'Main Warehouse – Karachi',
        'current_stock': 340, 'reserved_stock': 40, 'available_stock': 300,
        'min_stock': 50, 'unit': 'Pcs', 'status': 'in_stock', 'valuation': 289000,
    },
    {
        'id': 2, 'sku': 'RAM-DDR4-16G', 'name': 'DDR4 16GB 3200MHz RAM',
        'category': 'Memory', 'warehouse': 'Lahore Branch',
        'current_stock': 8, 'reserved_stock': 0, 'available_stock': 8,
        'min_stock': 50, 'unit': 'Pcs', 'status': 'low_stock', 'valuation': 33600,
    },
    {
        'id': 3, 'sku': 'CBL-HDMI-4K', 'name': 'HDMI 2.1 Cable 4K 2m',
        'category': 'Cables', 'warehouse': 'Main Warehouse – Karachi',
        'current_stock': 520, 'reserved_stock': 50, 'available_stock': 470,
        'min_stock': 100, 'unit': 'Pcs', 'status': 'in_stock', 'valuation': 166400,
    },
    {
        'id': 4, 'sku': 'HUB-USB7-001', 'name': 'USB 3.0 Hub 7-Port',
        'category': 'Hubs', 'warehouse': 'Islamabad Hub',
        'current_stock': 85, 'reserved_stock': 10, 'available_stock': 75,
        'min_stock': 30, 'unit': 'Pcs', 'status': 'in_stock', 'valuation': 93500,
    },
    {
        'id': 5, 'sku': 'SSD-1TB-NVM', 'name': 'NVMe SSD 1TB Gen4',
        'category': 'Storage', 'warehouse': 'Main Warehouse – Karachi',
        'current_stock': 42, 'reserved_stock': 5, 'available_stock': 37,
        'min_stock': 20, 'unit': 'Pcs', 'status': 'in_stock', 'valuation': 399000,
    },
    {
        'id': 6, 'sku': 'CBL-TYCA-001', 'name': 'Type-C to A Cable 1m 3A',
        'category': 'Cables', 'warehouse': 'Lahore Branch',
        'current_stock': 12, 'reserved_stock': 0, 'available_stock': 12,
        'min_stock': 100, 'unit': 'Pcs', 'status': 'low_stock', 'valuation': 1440,
    },
]

def inventory_list(request):
    """List of all warehouse stock levels, alert thresholds, and locations"""
    warehouse_filter = request.GET.get('warehouse', 'all')
    status_filter = request.GET.get('status', 'all')
    search_q = request.GET.get('q', '').lower()

    items = SAMPLE_INVENTORY
    if warehouse_filter != 'all':
        items = [i for i in items if warehouse_filter in i['warehouse'].lower()]
    if status_filter == 'low':
        items = [i for i in items if i['status'] == 'low_stock']
    if search_q:
        items = [i for i in items if search_q in i['name'].lower() or search_q in i['sku'].lower()]

    total_val = sum(i['valuation'] for i in SAMPLE_INVENTORY)
    total_qty = sum(i['current_stock'] for i in SAMPLE_INVENTORY)
    low_qty = sum(1 for i in SAMPLE_INVENTORY if i['status'] == 'low_stock')

    context = {
        'items': items,
        'selected_warehouse': warehouse_filter,
        'selected_status': status_filter,
        'search_q': search_q,
        'stats': {
            'total_value': total_val,
            'total_qty': total_qty,
            'low_stock_count': low_qty,
            'warehouse_count': 3,
        },
        'breadcrumbs': [('Home', '/'), ('Inventory', None)],
    }
    return render(request, 'inventory/list.html', context)

def add_stock(request):
    """Stock adjustment / received stock entry form"""
    if request.method == 'POST':
        return redirect('inventory:list')
    return render(request, 'inventory/add_stock.html', {
        'breadcrumbs': [('Home', '/'), ('Inventory', '/inventory/'), ('Add Stock', None)],
    })

def stock_transfer(request):
    """Inter-warehouse stock transfer view"""
    return redirect('inventory:list')


@require_GET
def api_dashboard_inventory(request):
    """Return active inventory for the dashboard widget, with low stock first."""
    products = (
        Product.objects.filter(is_deleted=False, status='active')
        .select_related('unit')
        .order_by('current_stock', 'name')[:6]
    )
    items = [
        {
            'sku': product.sku,
            'name': product.name,
            'qty': str(product.current_stock),
            'reorder': str(product.minimum_stock),
            'unit': product.unit.abbreviation if product.unit else '',
            'status': (
                'low_stock'
                if product.current_stock <= product.minimum_stock
                else 'in_stock'
            ),
        }
        for product in products
    ]
    return JsonResponse({'items': items})


@require_GET
def api_low_stock_alerts(request):
    """Return live low-stock items for the global navigation alert menu."""
    products = (
        Product.objects.filter(
            is_deleted=False,
            status='active',
            current_stock__lte=models.F('minimum_stock'),
        )
        .select_related('category')
        .order_by('current_stock', 'name')
    )
    items = [{
        'id': product.pk,
        'name': product.name,
        'sku': product.sku,
        'current_stock': str(product.current_stock),
        'reorder_level': str(product.minimum_stock),
        'url': f'/products/{product.pk}/',
    } for product in products]
    return JsonResponse({'count': len(items), 'items': items})
