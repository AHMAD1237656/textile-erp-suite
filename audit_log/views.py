from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render

from .models import ActivityLog


@login_required
def activity_list(request):
    page = Paginator(
        ActivityLog.objects.select_related('user').all(),
        25,
    ).get_page(request.GET.get('page', 1))
    return render(request, 'audit_log/activity_list.html', {
        'page_obj': page,
        'breadcrumbs': [('Home', '/'), ('Audit Trail', None)],
    })
