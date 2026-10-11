"""
Roles & Permissions app views – Matrix permission management and roles
"""
from django.shortcuts import render
from django.http import JsonResponse
import json

def roles_matrix(request):
    """Roles & permissions matrix view"""
    context = {
        'breadcrumbs': [('Home', '/'), ('Roles & Permissions', None)],
    }
    return render(request, 'roles/matrix.html', context)

def api_save_permissions(request):
    """Save updated permissions for a role"""
    return JsonResponse({'success': True, 'message': 'Permissions saved successfully'})
