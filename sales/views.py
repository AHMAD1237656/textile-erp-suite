"""
Sales app views – Sales invoice management, new sale entry, and JSON APIs
"""
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.db import models

SAMPLE_SALES = [
    {
        'id': 101, 'number': 'INV-2024-0921', 'client_name': 'TechMart Pvt Ltd',
        'client_city': 'Karachi', 'date': '2024-10-07', 'due_date': '2024-10-21',
        'total_amount': 420000, 'paid_amount': 420000, 'balance': 0,
        'status': 'paid', 'items_count': 4, 'warehouse': 'Main Warehouse – Karachi',
    },
    {
        'id': 102, 'number': 'INV-2024-0920', 'client_name': 'Digital World',
        'client_city': 'Lahore', 'date': '2024-10-06', 'due_date': '2024-10-20',
        'total_amount': 650000, 'paid_amount': 450000, 'balance': 200000,
        'status': 'partial', 'items_count': 6, 'warehouse': 'Lahore Branch',
    },
    {
        'id': 103, 'number': 'INV-2024-0919', 'client_name': 'ByteHouse Corp',
        'client_city': 'Islamabad', 'date': '2024-10-05', 'due_date': '2024-10-12',
        'total_amount': 185000, 'paid_amount': 0, 'balance': 185000,
        'status': 'unpaid', 'items_count': 3, 'warehouse': 'Islamabad Hub',
    },
    {
        'id': 104, 'number': 'INV-2024-0891', 'client_name': 'MicroHub Technologies',
        'client_city': 'Rawalpindi', 'date': '2024-09-22', 'due_date': '2024-10-01',
        'total_amount': 320000, 'paid_amount': 50000, 'balance': 270000,
        'status': 'overdue', 'items_count': 5, 'warehouse': 'Main Warehouse – Karachi',
    },
    {
        'id': 105, 'number': 'INV-2024-0888', 'client_name': 'Lahore Gadgets',
        'client_city': 'Lahore', 'date': '2024-09-20', 'due_date': '2024-10-04',
        'total_amount': 890000, 'paid_amount': 890000, 'balance': 0,
        'status': 'paid', 'items_count': 8, 'warehouse': 'Lahore Branch',
    },
]

def sales_list(request):
    """List of all sales invoices with search and filter tabs"""
    status_filter = request.GET.get('status', 'all')
    search_q = request.GET.get('q', '').lower()

    filtered_sales = SAMPLE_SALES
    if status_filter != 'all':
        filtered_sales = [s for s in filtered_sales if s['status'] == status_filter]
    if search_q:
        filtered_sales = [
            s for s in filtered_sales
            if search_q in s['number'].lower() or search_q in s['client_name'].lower()
        ]

    total_sales_val = sum(s['total_amount'] for s in SAMPLE_SALES)
    total_received = sum(s['paid_amount'] for s in SAMPLE_SALES)
    total_balance = sum(s['balance'] for s in SAMPLE_SALES)

    context = {
        'sales': filtered_sales,
        'selected_status': status_filter,
        'search_q': search_q,
        'stats': {
            'total_sales': total_sales_val,
            'total_received': total_received,
            'total_balance': total_balance,
            'count': len(SAMPLE_SALES),
        },
        'breadcrumbs': [('Home', '/'), ('Sales', None)],
    }
    return render(request, 'sales/list.html', context)

def sales_create(request):
    """Create a new sales invoice with interactive line items"""
    if request.method == 'POST':
        # Accept AJAX or form submission
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json'
        if is_ajax:
            return JsonResponse({'success': True, 'invoice_number': 'INV-2024-0922', 'message': 'Invoice created successfully'})
        return redirect('sales:list')

    context = {
        'next_invoice_number': 'INV-2024-0922',
        'today': timezone.now().date(),
        'breadcrumbs': [('Home', '/'), ('Sales', '/sales/'), ('New Invoice', None)],
    }
    return render(request, 'sales/create.html', context)

from .models import Client

def sales_detail(request, pk):
    """Detail view for a sales invoice"""
    sale = next((s for s in SAMPLE_SALES if s['id'] == pk), SAMPLE_SALES[0])
    return render(request, 'sales/detail.html', {'invoice': sale})

def api_sales(request):
    """JSON API endpoint for sales records"""
    return JsonResponse({'data': SAMPLE_SALES, 'total': len(SAMPLE_SALES)})

def clients_list(request):
    """Client / Customer directory and management view"""
    status_filter = request.GET.get('status', 'all')
    city_filter = request.GET.get('city', 'all')
    search_q = request.GET.get('q', '').strip()

    qs = Client.objects.all()

    if status_filter != 'all':
        qs = qs.filter(status=status_filter)
    if city_filter != 'all':
        qs = qs.filter(city__iexact=city_filter)
    if search_q:
        qs = qs.filter(
            models.Q(name__icontains=search_q) |
            models.Q(company_name__icontains=search_q) |
            models.Q(phone__icontains=search_q) |
            models.Q(email__icontains=search_q) |
            models.Q(city__icontains=search_q)
        )

    all_clients = Client.objects.all()
    total_clients = all_clients.count()
    active_clients = all_clients.filter(status='Active').count()
    exceeded_clients = all_clients.filter(status='Exceeded').count()
    total_balance = sum(float(c.current_balance) for c in all_clients)

    cities = sorted(list(set(c.city for c in all_clients if c.city)))

    context = {
        'clients': qs,
        'cities': cities,
        'selected_status': status_filter,
        'selected_city': city_filter,
        'search_q': search_q,
        'stats': {
            'total': total_clients,
            'active': active_clients,
            'exceeded': exceeded_clients,
            'total_receivables': total_balance,
        },
        'breadcrumbs': [('Home', '/'), ('Sales', '/sales/'), ('Clients Directory', None)],
    }
    return render(request, 'sales/clients.html', context)

@require_http_methods(["POST"])
def clients_create(request):
    """Create a new client via modal AJAX or standard form POST"""
    is_ajax = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
        request.content_type == 'application/json' or
        request.GET.get('format') == 'json'
    )

    data = request.POST
    if request.content_type == 'application/json' and request.body:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            pass

    name = data.get('name', '').strip()
    if not name:
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'Client name is required.'}, status=400)
        return redirect('sales:clients')

    company_name = data.get('company_name', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()
    city = data.get('city', 'Karachi').strip()
    address = data.get('address', '').strip()
    ntn_tax_id = data.get('ntn_tax_id', '').strip()

    try:
        credit_limit = float(data.get('credit_limit', 500000))
    except (ValueError, TypeError):
        credit_limit = 500000.00

    try:
        opening_balance = float(data.get('opening_balance', data.get('current_balance', 0)))
    except (ValueError, TypeError):
        opening_balance = 0.00

    status = data.get('status', 'Active')
    notes = data.get('notes', '').strip()

    client = Client.objects.create(
        name=name,
        company_name=company_name,
        phone=phone,
        email=email,
        city=city,
        address=address,
        ntn_tax_id=ntn_tax_id,
        credit_limit=credit_limit,
        current_balance=opening_balance,
        status=status,
        notes=notes,
    )

    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': f'Client "{client.name}" registered successfully.',
            'client': client.to_dict(),
        })

    return redirect('sales:clients')

def api_clients(request):
    """JSON API endpoint returning active client records for dropdowns and search"""
    q = request.GET.get('q', '').strip()
    qs = Client.objects.all()
    if q:
        qs = qs.filter(
            models.Q(name__icontains=q) |
            models.Q(company_name__icontains=q) |
            models.Q(city__icontains=q)
        )
    return JsonResponse({
        'data': [c.to_dict() for c in qs],
        'total': qs.count(),
    })
