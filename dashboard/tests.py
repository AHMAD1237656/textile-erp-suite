from django.test import TestCase

from products.models import Category, Product


class DashboardAnalyticsApiTests(TestCase):
    def test_returns_monthly_sales_dispatch_and_database_inventory(self):
        category = Category.objects.create(name='Cotton')
        Product.objects.create(
            sku='FAB-001',
            name='Cotton Twill',
            category=category,
            current_stock='25.5',
        )

        response = self.client.get('/dashboard/api/analytics/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['monthly']['labels'], ['Sep 2024', 'Oct 2024'])
        self.assertEqual(data['monthly']['sales'], [1210000.0, 1255000.0])
        self.assertEqual(data['monthly']['dispatches'], [0, 72])
        self.assertEqual(data['inventory_categories'], [{
            'name': 'Cotton',
            'stock': 25.5,
            'products': 1,
        }])

    def test_returns_empty_inventory_when_no_products_exist(self):
        response = self.client.get('/dashboard/api/analytics/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['inventory_categories'], [])
        self.assertEqual(
            response.json()['monthly']['labels'],
            ['Sep 2024', 'Oct 2024'],
        )

# Create your tests here.
