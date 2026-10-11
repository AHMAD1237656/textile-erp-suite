from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from io import BytesIO
import csv
from openpyxl import Workbook

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


class ProductImportTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='importer',
            password='test-password',
        )
        self.client.force_login(self.user)

    def test_sample_template_has_required_columns(self):
        response = self.client.get(reverse('products:import_sample'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('attachment;', response['Content-Disposition'])
        rows = list(csv.reader(response.content.decode('utf-8').splitlines()))
        self.assertEqual(rows[0], [
            'Name', 'SKU', 'Category', 'Stock/Quantity', 'Reorder Level', 'Unit Price',
        ])

    def test_csv_import_saves_valid_rows_and_skips_invalid_rows(self):
        content = (
            'Name,SKU,Category,Stock/Quantity,Reorder Level,Unit Price\n'
            'Cotton Roll,FAB-100,Cotton,20,5,125.50\n'
            'Invalid Roll,FAB-101,Cotton,not-a-number,5,99\n'
            'Duplicate Roll,FAB-100,Cotton,10,2,90\n'
        )
        upload = SimpleUploadedFile(
            'products.csv',
            content.encode('utf-8'),
            content_type='text/csv',
        )

        response = self.client.post(
            reverse('products:import'),
            {'file': upload},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Product.objects.filter(sku='FAB-100').count(), 1)
        product = Product.objects.get(sku='FAB-100')
        self.assertEqual(product.current_stock, 20)
        self.assertEqual(product.selling_price, 125.50)
        self.assertContains(response, 'Successfully imported 1 products.')
        self.assertContains(response, '2 row(s) skipped.')

    def test_xlsx_import_creates_product(self):
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.append([
            'Name', 'SKU', 'Category', 'Stock/Quantity', 'Reorder Level', 'Unit Price',
        ])
        worksheet.append(['Linen Roll', 'LIN-200', 'Linen', 8, 3, 450.75])
        output = BytesIO()
        workbook.save(output)
        upload = SimpleUploadedFile(
            'products.xlsx',
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

        response = self.client.post(reverse('products:import'), {'file': upload})

        self.assertRedirects(response, reverse('products:list'))
        self.assertTrue(Product.objects.filter(sku='LIN-200', name='Linen Roll').exists())
