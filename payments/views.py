"""
Payments app views – Customer receipts, supplier vouchers, bank reconciliation
"""
from django.shortcuts import render, redirect

SAMPLE_PAYMENTS = [
    {
        'id': 1, 'voucher_no': 'RCV-2024-0819', 'type': 'Receipt', 'party': 'TechMart Pvt Ltd',
        'account': 'Meezan Bank (Main A/C 0102)', 'reference': 'Online FT-99214',
        'date': '2024-10-07', 'amount': 420000, 'status': 'Cleared',
    },
    {
        'id': 2, 'voucher_no': 'RCV-2024-0818', 'type': 'Receipt', 'party': 'Digital World',
        'account': 'Habib Bank Ltd (HBL 9812)', 'reference': 'Cheque #881204',
        'date': '2024-10-06', 'amount': 450000, 'status': 'Cleared',
    },
    {
        'id': 3, 'voucher_no': 'PAY-2024-0410', 'type': 'Payment', 'party': 'Customs Duty & Clearance Agents',
        'account': 'Meezan Bank (Main A/C 0102)', 'reference': 'GD #PQ-11829',
        'date': '2024-10-04', 'amount': 850000, 'status': 'Cleared',
    },
    {
        'id': 4, 'voucher_no': 'PAY-2024-0409', 'type': 'Payment', 'party': 'Shenzhen TopTech Electronics',
        'account': 'LC / Foreign Remittance', 'reference': 'TT Ref #FX-9901',
        'date': '2024-10-02', 'amount': 5180000, 'status': 'Cleared',
    },
]

def payment_list(request):
    """List of all payment and receipt vouchers"""
    total_received = sum(p['amount'] for p in SAMPLE_PAYMENTS if p['type'] == 'Receipt')
    total_paid = sum(p['amount'] for p in SAMPLE_PAYMENTS if p['type'] == 'Payment')

    context = {
        'payments': SAMPLE_PAYMENTS,
        'stats': {
            'total_received': total_received,
            'total_paid': total_paid,
            'net_cashflow': total_received - total_paid,
        },
        'breadcrumbs': [('Home', '/'), ('Payments', None)],
    }
    return render(request, 'payments/list.html', context)

def payment_create(request):
    """Record receipt or payment"""
    if request.method == 'POST':
        return redirect('payments:list')
    return render(request, 'payments/create.html', {
        'breadcrumbs': [('Home', '/'), ('Payments', '/payments/'), ('New Voucher', None)],
    })
