"""
Users app views – System staff user management, role assignments, and branch locations
"""
from django.shortcuts import render, redirect

SAMPLE_USERS = [
    {
        'id': 1, 'username': 'admin', 'name': 'Adnan Qureshi (Director)', 'email': 'adnan@techimport.pk',
        'role': 'Admin', 'branch': 'Head Office – Karachi', 'status': 'Active', 'last_login': '10 mins ago',
    },
    {
        'id': 2, 'username': 'kamran.m', 'name': 'Kamran Malik', 'email': 'kamran@techimport.pk',
        'role': 'Manager', 'branch': 'Lahore Branch', 'status': 'Active', 'last_login': '2 hours ago',
    },
    {
        'id': 3, 'username': 'faisal.acc', 'name': 'Faisal Ahmed', 'email': 'faisal@techimport.pk',
        'role': 'Accountant', 'branch': 'Head Office – Karachi', 'status': 'Active', 'last_login': 'Yesterday',
    },
    {
        'id': 4, 'username': 'bilal.wh', 'name': 'Bilal Shah', 'email': 'bilal@techimport.pk',
        'role': 'Storekeeper', 'branch': 'Main Warehouse – Port Qasim', 'status': 'Active', 'last_login': '3 hours ago',
    },
    {
        'id': 5, 'username': 'usman.sales', 'name': 'Usman Raza', 'email': 'usman@techimport.pk',
        'role': 'Salesman', 'branch': 'Islamabad Hub', 'status': 'Inactive', 'last_login': '5 days ago',
    },
]

def user_list(request):
    """User & staff administration page"""
    context = {
        'users': SAMPLE_USERS,
        'stats': {
            'total_users': len(SAMPLE_USERS),
            'active_users': sum(1 for u in SAMPLE_USERS if u['status'] == 'Active'),
            'admin_count': sum(1 for u in SAMPLE_USERS if u['role'] == 'Admin'),
        },
        'breadcrumbs': [('Home', '/'), ('Users & Roles', None)],
    }
    return render(request, 'users_app/list.html', context)

def user_create(request):
    if request.method == 'POST':
        return redirect('users_app:list')
    return redirect('users_app:list')
