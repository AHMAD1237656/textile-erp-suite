from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Category, Product
from .qr_utils import product_qr_payload


class ProductQrCodeTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='warehouse',
            password='test-password',
        )
        self.category = Category.objects.create(name='Cotton')
        self.product = Product.objects.create(
            sku='FAB-001',
            name='Cotton Twill',
            category=self.category,
            current_stock='125.50',
        )

    def test_qr_payload_contains_current_product_details(self):
        self.assertEqual(
            product_qr_payload(self.product),
            '{"name": "Cotton Twill", "sku": "FAB-001", "category": "Cotton", "current_stock": "125.50"}',
        )

    def test_qr_endpoint_returns_png_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('products:product_qr_code', args=[self.product.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertTrue(response.content.startswith(b'\x89PNG\r\n\x1a\n'))

    def test_qr_endpoint_keeps_deleted_products_unavailable(self):
        self.client.force_login(self.user)
        self.product.is_deleted = True
        self.product.save(update_fields=['is_deleted'])

        response = self.client.get(
            reverse('products:product_qr_code', args=[self.product.pk])
        )
        self.assertEqual(response.status_code, 404)
