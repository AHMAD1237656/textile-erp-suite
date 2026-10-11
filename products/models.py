"""
Products app models – TechImport ERP
Electronics import business: chargers, RAM, cables, switches, etc.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Category(models.Model):
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self): return self.name


class Unit(models.Model):
    name         = models.CharField(max_length=50)  # e.g. Piece, Box, Dozen
    abbreviation = models.CharField(max_length=10)  # e.g. Pcs, Bx, Dz

    def __str__(self): return self.name


class Product(models.Model):
    STATUS_CHOICES = [
        ('active',       'Active'),
        ('inactive',     'Inactive'),
        ('discontinued', 'Discontinued'),
    ]

    # Identification
    sku          = models.CharField(max_length=50, unique=True)
    barcode      = models.CharField(max_length=100, blank=True)
    name         = models.CharField(max_length=255)
    category     = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    unit         = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    description  = models.TextField(blank=True)
    image        = models.ImageField(upload_to='products/', blank=True, null=True)

    # Pricing
    purchase_price = models.DecimalField(max_digits=14, decimal_places=2, default=0,
                                         validators=[MinValueValidator(0)])
    selling_price  = models.DecimalField(max_digits=14, decimal_places=2, default=0,
                                         validators=[MinValueValidator(0)])
    wholesale_price = models.DecimalField(max_digits=14, decimal_places=2, default=0,
                                          validators=[MinValueValidator(0)])
    tax_rate       = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                         help_text='Tax percentage, e.g. 17 for 17%')

    # Stock
    current_stock  = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    minimum_stock  = models.DecimalField(max_digits=14, decimal_places=2, default=0,
                                         help_text='Reorder alert threshold')
    reorder_qty    = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # Supplier info
    supplier_name  = models.CharField(max_length=255, blank=True)
    origin_country = models.CharField(max_length=100, blank=True, default='China')
    hs_code        = models.CharField(max_length=20, blank=True,
                                       help_text='HS tariff code for customs')

    # Status
    status     = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    is_deleted = models.BooleanField(default=False)  # Soft delete

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['sku']),
            models.Index(fields=['status', 'is_deleted']),
        ]

    def __str__(self): return f'{self.sku} – {self.name}'

    @property
    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock

    @property
    def stock_value(self):
        return self.current_stock * self.purchase_price

    @property
    def profit_margin(self):
        if not self.purchase_price:
            return 0
        return round((self.selling_price - self.purchase_price) / self.purchase_price * 100, 2)
