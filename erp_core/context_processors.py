"""
ERP Context Processors – injects user permissions, warehouses, and global config
into every template context automatically.
"""


import json

def erp_context(request):
    """
    Inject global ERP context into every template.
    In production this would query the DB; here we use realistic sample data.
    """
    # Sample permissions – in production, load from request.user's role
    permissions = {
        'can_view_dashboard': True,
        'can_manage_products': True,
        'can_manage_sales': True,
        'can_manage_purchases': True,
        'can_manage_inventory': True,
        'can_manage_manufacturing': True,
        'can_manage_distribution': True,
        'can_manage_invoices': True,
        'can_manage_payments': True,
        'can_view_ledger': True,
        'can_view_reports': True,
        'can_manage_users': True,
        'can_manage_roles': True,
        'can_manage_settings': True,
    }

    warehouses = [
        {'id': 1, 'name': 'Main Warehouse – Karachi'},
        {'id': 2, 'name': 'Lahore Branch'},
        {'id': 3, 'name': 'Islamabad Hub'},
    ]

    notifications = [
        {'id': 1, 'type': 'warning', 'icon': 'exclamation-triangle',
         'message': 'Stock below minimum: USB-C Cables (12 units left)',
         'time': '5 min ago', 'read': False},
        {'id': 2, 'type': 'danger', 'icon': 'credit-card',
         'message': 'Credit limit exceeded: TechMart Pvt Ltd (PKR 2.3M)',
         'time': '18 min ago', 'read': False},
        {'id': 3, 'type': 'info', 'icon': 'box-seam',
         'message': 'Container #MSCU-7821 arrived at Port Qasim',
         'time': '1 hr ago', 'read': False},
        {'id': 4, 'type': 'warning', 'icon': 'clock-history',
         'message': 'Invoice INV-2024-0891 overdue by 15 days',
         'time': '2 hrs ago', 'read': True},
        {'id': 5, 'type': 'success', 'icon': 'check-circle',
         'message': 'Payment received: PKR 450,000 from Digital World',
         'time': '3 hrs ago', 'read': True},
    ]

    return {
        'erp_permissions': permissions,
        'erp_permissions_json': json.dumps(permissions),
        'erp_warehouses': warehouses,
        'erp_notifications': notifications,
        'erp_unread_count': sum(1 for n in notifications if not n['read']),
        'erp_version': '2.4.1',
        'erp_company': 'TechImport ERP',
        'erp_user_role': 'Admin',
    }

