"""
Manufacturing app views – Bill of Materials (BOM), Assembly work orders, and batches
"""
from django.shortcuts import render, redirect

SAMPLE_ORDERS = [
    {
        'id': 1, 'order_no': 'MO-2024-0042', 'product_name': 'Custom Gaming PC Build #A',
        'target_qty': 20, 'completed_qty': 15, 'start_date': '2024-10-01', 'due_date': '2024-10-15',
        'status': 'in_progress', 'progress': 75, 'line': 'Assembly Line 1 – Karachi',
    },
    {
        'id': 2, 'order_no': 'MO-2024-0041', 'product_name': 'Packaged USB-C Cable 3-Pack',
        'target_qty': 500, 'completed_qty': 500, 'start_date': '2024-09-26', 'due_date': '2024-10-04',
        'status': 'completed', 'progress': 100, 'line': 'Packaging Unit 2',
    },
    {
        'id': 3, 'order_no': 'MO-2024-0043', 'product_name': 'Office Mini PC Intel i5 Bundle',
        'target_qty': 50, 'completed_qty': 10, 'start_date': '2024-10-06', 'due_date': '2024-10-22',
        'status': 'in_progress', 'progress': 20, 'line': 'Assembly Line 2 – Karachi',
    },
    {
        'id': 4, 'order_no': 'MO-2024-0044', 'product_name': 'Custom Power Adapter 12V 5A',
        'target_qty': 1000, 'completed_qty': 0, 'start_date': '2024-10-12', 'due_date': '2024-10-28',
        'status': 'planned', 'progress': 0, 'line': 'SMT Line 1',
    },
]

def manufacturing_list(request):
    """List of all manufacturing/assembly work orders"""
    context = {
        'orders': SAMPLE_ORDERS,
        'stats': {
            'active_orders': sum(1 for o in SAMPLE_ORDERS if o['status'] == 'in_progress'),
            'completed_orders': sum(1 for o in SAMPLE_ORDERS if o['status'] == 'completed'),
            'total_target_units': sum(o['target_qty'] for o in SAMPLE_ORDERS),
        },
        'breadcrumbs': [('Home', '/'), ('Manufacturing', None)],
    }
    return render(request, 'manufacturing/list.html', context)

def manufacturing_create(request):
    """Create manufacturing order"""
    if request.method == 'POST':
        return redirect('manufacturing:list')
    return redirect('manufacturing:list')
