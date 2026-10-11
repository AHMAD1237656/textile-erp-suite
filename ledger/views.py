"""
Ledger app views – Customer & Supplier running accounts, debits, credits and aging balance
"""
from django.shortcuts import render

SAMPLE_LEDGER_ENTRIES = [
    {'date': '2024-09-01', 'ref': 'OB-2024', 'description': 'Opening Balance', 'debit': 0, 'credit': 0, 'balance': 500000},
    {'date': '2024-09-12', 'ref': 'INV-2024-0820', 'description': 'Sales Invoice – Chargers & Cables', 'debit': 450000, 'credit': 0, 'balance': 950000},
    {'date': '2024-09-18', 'ref': 'RCV-2024-0712', 'description': 'Bank Transfer via Meezan Bank', 'debit': 0, 'credit': 500000, 'balance': 450000},
    {'date': '2024-09-25', 'ref': 'INV-2024-0865', 'description': 'Sales Invoice – DDR4 RAM Modules', 'debit': 620000, 'credit': 0, 'balance': 1070000},
    {'date': '2024-10-02', 'ref': 'RCV-2024-0801', 'description': 'HBL Cheque #882194 Realized', 'debit': 0, 'credit': 600000, 'balance': 470000},
    {'date': '2024-10-07', 'ref': 'INV-2024-0921', 'description': 'Sales Invoice – 65W GaN Chargers & SSDs', 'debit': 420000, 'credit': 0, 'balance': 890000},
]

CLIENTS = [
    {'id': 1, 'name': 'TechMart Pvt Ltd', 'city': 'Karachi', 'credit_limit': 1500000, 'current_balance': 890000, 'status': 'Normal'},
    {'id': 2, 'name': 'Digital World', 'city': 'Lahore', 'credit_limit': 1000000, 'current_balance': 200000, 'status': 'Normal'},
    {'id': 3, 'name': 'ByteHouse Corp', 'city': 'Islamabad', 'credit_limit': 500000, 'current_balance': 185000, 'status': 'Normal'},
    {'id': 4, 'name': 'MicroHub Technologies', 'city': 'Rawalpindi', 'credit_limit': 200000, 'current_balance': 270000, 'status': 'Exceeded'},
]

from sales.models import Client

def ledger_list(request):
    """Client ledger statement view with running balance"""
    clients_qs = Client.objects.all()
    if clients_qs.exists():
        clients = clients_qs
        selected_client_id = request.GET.get('client')
        try:
            client = Client.objects.get(id=int(selected_client_id)) if selected_client_id else clients_qs.first()
        except (ValueError, TypeError, Client.DoesNotExist):
            client = clients_qs.first()
    else:
        clients = CLIENTS
        selected_client_id = int(request.GET.get('client', 1))
        client = next((c for c in CLIENTS if c['id'] == selected_client_id), CLIENTS[0])

    total_debit = sum(e['debit'] for e in SAMPLE_LEDGER_ENTRIES)
    total_credit = sum(e['credit'] for e in SAMPLE_LEDGER_ENTRIES)

    context = {
        'clients': CLIENTS,
        'client': client,
        'entries': SAMPLE_LEDGER_ENTRIES,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'closing_balance': SAMPLE_LEDGER_ENTRIES[-1]['balance'],
        'breadcrumbs': [('Home', '/'), ('Client Ledger', None)],
    }
    return render(request, 'ledger/list.html', context)

def ledger_detail(request, client_id):
    return ledger_list(request)
