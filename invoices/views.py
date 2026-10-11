"""
Invoices app views – Invoice registry, printing templates, and custom format builder
"""
from django.shortcuts import render

SAMPLE_INVOICES = [
    {'number': 'INV-2024-0921', 'client': 'TechMart Pvt Ltd', 'type': 'Sales Invoice', 'date': '2024-10-07', 'amount': 420000, 'status': 'Paid'},
    {'number': 'INV-2024-0920', 'client': 'Digital World', 'type': 'Sales Invoice', 'date': '2024-10-06', 'amount': 650000, 'status': 'Partial'},
    {'number': 'INV-2024-0919', 'client': 'ByteHouse Corp', 'type': 'Sales Invoice', 'date': '2024-10-05', 'amount': 185000, 'status': 'Unpaid'},
    {'number': 'PI-2024-0104', 'client': 'Shenzhen TopTech Electronics', 'type': 'Commercial Invoice', 'date': '2024-10-02', 'amount': 5180000, 'status': 'Customs Verified'},
    {'number': 'INV-2024-0891', 'client': 'MicroHub Technologies', 'type': 'Sales Invoice', 'date': '2024-09-22', 'amount': 320000, 'status': 'Overdue'},
]

def invoice_list(request):
    """List of all invoices across system"""
    context = {
        'invoices': SAMPLE_INVOICES,
        'breadcrumbs': [('Home', '/'), ('Invoices', None)],
    }
    return render(request, 'invoices/list.html', context)

def invoice_builder(request):
    """Visual drag & drop invoice template designer"""
    return render(request, 'invoices/builder.html', {
        'breadcrumbs': [('Home', '/'), ('Invoice Builder', None)],
    })
