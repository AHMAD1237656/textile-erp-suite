from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.urls import reverse

from .models import ActivityLog
from .utils import log_activity


class ActivityLogTests(TestCase):
    def test_helper_records_authenticated_user_and_request_ip(self):
        user = get_user_model().objects.create_user(username='audited')
        request = self.client.request().wsgi_request
        request.user = user
        request.META['REMOTE_ADDR'] = '192.0.2.10'

        entry = log_activity(request, 'UPDATE', 'Products', 'Updated a product.')

        self.assertIsNotNone(entry)
        self.assertEqual(entry.user, user)
        self.assertEqual(entry.ip_address, '192.0.2.10')

    def test_unauthenticated_events_can_be_logged(self):
        request = self.client.request().wsgi_request
        request.user = AnonymousUser()

        entry = log_activity(request, 'EXPORT', 'Reports', 'Downloaded report.')

        self.assertIsNotNone(entry)
        self.assertIsNone(entry.user)

    def test_activity_list_requires_login_and_displays_entries(self):
        user = get_user_model().objects.create_user(username='reader')
        ActivityLog.objects.create(
            user=user,
            action='IMPORT',
            module='Products',
            description='Imported two products.',
        )
        url = reverse('audit_log:activity_list')

        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Imported two products.')
