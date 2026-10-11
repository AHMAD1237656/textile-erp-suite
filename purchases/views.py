"""
Purchases app views – Supplier purchase orders, import shipments, customs & payments
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone

SAMPLE_PURCHASES = [
    {
        'id': 201, 'po_number': 'PO-2024-0412', 'supplier_name': 'Shenzhen TopTech Electronics Co.',
        'country': 'China', 'date': '2024-10-02', 'eta': '2024-10-24',
        'total_usd': 18500, 'total_pkr': 5180000, 'status': 'in_transit',
        'items_count': 1200, 'container': 'MSCU-782194', 'customs_status': 'Under Clearance',
    },
    {
        'id': 202, 'po_number': 'PO-2024-0398', 'supplier_name': 'Ningbo GreatLink Hardware Ltd.',
        'country': 'China', 'date': '2024-09-28', 'eta': '2024-10-18',
        'total_usd': 14200, 'total_pkr': 3976000, 'status': 'at_port',
        'items_count': 850, 'container': 'OOLU-441892', 'customs_status': 'Customs Duty Paid',
    },
    {
        'id': 203, 'po_number': 'PO-2024-0370', 'supplier_name': 'HuiZhou Battery King Power Tech',
        'country': 'China', 'date': '2024-09-15', 'eta': '2024-10-05',
        'total_usd': 29400, 'total_pkr': 8232000, 'status': 'received',
        'items_count': 2500, 'container': 'EGLV-112048', 'customs_status': 'Cleared & Warehoused',
    },
    {
        'id': 204, 'po_number': 'PO-2024-0430', 'supplier_name': 'Shenzhen FastGaN Tech Ltd',
        'country': 'China', 'date': '2024-10-05', 'eta': '2024-11-02',
        'total_usd': 9600, 'total_pkr': 2688000, 'status': 'ordered',
        'items_count': 600, 'container': 'Pending Shipment', 'customs_status': 'Documents Sent',
    },
]

def purchase_list(request):
    """List of all purchase orders and import shipments"""
    status_filter = request.GET.get('status', 'all')
    search_q = request.GET.get('q', '').lower()

    pos = SAMPLE_PURCHASES
    if status_filter != 'all':
        pos = [p for p in pos if p['status'] == status_filter]
    if search_q:
        pos = [
            p for p in pos
            if search_q in p['po_number'].lower() or search_q in p['supplier_name'].lower()
        ]

    total_pkr = sum(p['total_pkr'] for p in SAMPLE_PURCHASES)
    total_usd = sum(p['total_usd'] for p in SAMPLE_PURCHASES)

    context = {
        'purchases': pos,
        'selected_status': status_filter,
        'search_q': search_q,
        'stats': {
            'total_pkr': total_pkr,
            'total_usd': total_usd,
            'in_transit_count': sum(1 for p in SAMPLE_PURCHASES if p['status'] in ('in_transit', 'at_port')),
            'total_pos': len(SAMPLE_PURCHASES),
        },
        'breadcrumbs': [('Home', '/'), ('Purchases', None)],
    }
    return render(request, 'purchases/list.html', context)

def purchase_create(request):
    """Create a new purchase order"""
    if request.method == 'POST':
        return redirect('purchases:list')
    context = {
        'next_po_number': 'PO-2024-0435',
        'today': timezone.now().date(),
        'breadcrumbs': [('Home', '/'), ('Purchases', '/purchases/'), ('New Purchase Order', None)],
    }
    return render(request, 'purchases/create.html', context)

def purchase_detail(request, pk):
    """Detail view for a purchase order"""
    po = next((p for p in SAMPLE_PURCHASES if p['id'] == pk), SAMPLE_PURCHASES[0])
    return render(request, 'purchases/detail.html', {'purchase': po})
