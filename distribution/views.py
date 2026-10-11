"""
Distribution app views – Logistics, dispatch delivery challans, container tracking
"""
from django.shortcuts import render, redirect

SAMPLE_DISPATCHES = [
    {
        'id': 1, 'dc_no': 'DC-2024-0312', 'client_name': 'TechMart Pvt Ltd',
        'destination': 'Saddar, Karachi', 'driver': 'Tariq Mehmood (Van KHI-8821)',
        'date': '2024-10-07', 'boxes': 18, 'status': 'delivered',
    },
    {
        'id': 2, 'dc_no': 'DC-2024-0313', 'client_name': 'Digital World',
        'destination': 'Hafeez Centre, Lahore', 'driver': 'TCS Overland Cargo #TC-9912',
        'date': '2024-10-07', 'boxes': 42, 'status': 'out_for_delivery',
    },
    {
        'id': 3, 'dc_no': 'DC-2024-0314', 'client_name': 'ByteHouse Corp',
        'destination': 'Blue Area, Islamabad', 'driver': 'Leopard Courier #LEO-4019',
        'date': '2024-10-06', 'boxes': 12, 'status': 'in_transit',
    },
    {
        'id': 4, 'dc_no': 'DC-2024-0315', 'client_name': 'MicroHub Technologies',
        'destination': 'Saddar, Rawalpindi', 'driver': 'Pending Driver Assignment',
        'date': '2024-10-08', 'boxes': 25, 'status': 'preparing',
    },
]

def distribution_list(request):
    """Distribution & delivery challans tracker"""
    context = {
        'dispatches': SAMPLE_DISPATCHES,
        'stats': {
            'out_for_delivery': sum(1 for d in SAMPLE_DISPATCHES if d['status'] in ('out_for_delivery', 'in_transit')),
            'delivered_today': sum(1 for d in SAMPLE_DISPATCHES if d['status'] == 'delivered'),
            'total_boxes': sum(d['boxes'] for d in SAMPLE_DISPATCHES),
        },
        'breadcrumbs': [('Home', '/'), ('Distribution', None)],
    }
    return render(request, 'distribution/list.html', context)

def distribution_create(request):
    return redirect('distribution:list')
