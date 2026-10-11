import ipaddress
import logging

from .models import ActivityLog

logger = logging.getLogger(__name__)


def log_activity(request, action, module, description):
    """Record an audit event without allowing logging errors to break a workflow."""
    user = getattr(request, 'user', None)
    if not getattr(user, 'is_authenticated', False):
        user = None

    raw_ip = request.META.get('REMOTE_ADDR') if request else None
    try:
        ip_address = str(ipaddress.ip_address(raw_ip)) if raw_ip else None
    except ValueError:
        ip_address = None

    try:
        return ActivityLog.objects.create(
            user=user,
            action=action,
            module=module,
            description=description,
            ip_address=ip_address,
        )
    except Exception:
        logger.exception('Unable to write activity log for %s/%s', module, action)
        return None
