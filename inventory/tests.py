from django.test import TestCase

from products.models import Product, Unit


class DashboardInventoryApiTests(TestCase):
    def test_dashboard_uses_inventory_api_and_refresh_control(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="inventory-widget"')
        self.assertContains(response, 'data-url="/inventory/api/dashboard/"')
        self.assertContains(response, 'id="inventory-widget-refresh"')

    def test_returns_product_stock_for_dashboard(self):
        unit = Unit.objects.create(name='Piece', abbreviation='pcs')
        Product.objects.create(
            sku='FAB-001',
            name='Cotton Fabric',
            current_stock='4.5',
            minimum_stock='10',
            unit=unit,
        )

        response = self.client.get('/inventory/api/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'items': [{
                'sku': 'FAB-001',
                'name': 'Cotton Fabric',
                'qty': '4.50',
                'reorder': '10.00',
                'unit': 'pcs',
                'status': 'low_stock',
            }],
        })

    def test_returns_empty_list_when_no_inventory_exists(self):
        response = self.client.get('/inventory/api/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'items': []})


class LowStockAlertApiTests(TestCase):
    def test_returns_only_active_products_at_or_below_minimum(self):
        Product.objects.create(
            sku='LOW-1',
            name='Low Stock Fabric',
            current_stock='5',
            minimum_stock='5',
            status='active',
        )
        Product.objects.create(
            sku='HEALTHY-1',
            name='Healthy Fabric',
            current_stock='6',
            minimum_stock='5',
            status='active',
        )
        Product.objects.create(
            sku='INACTIVE-1',
            name='Inactive Fabric',
            current_stock='0',
            minimum_stock='5',
            status='inactive',
        )

        response = self.client.get('/inventory/api/low-stock-alerts/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['items'][0]['sku'], 'LOW-1')
        self.assertEqual(data['items'][0]['url'], '/products/1/')

# Create your tests here.
