from django.db import models

class Client(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Exceeded', 'Credit Exceeded'),
    ]

    name = models.CharField(max_length=200, help_text="Full individual or contact name")
    company_name = models.CharField(max_length=200, blank=True, default='', help_text="Registered trading or business name")
    phone = models.CharField(max_length=50, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    city = models.CharField(max_length=100, default='Karachi')
    address = models.TextField(blank=True, default='')
    ntn_tax_id = models.CharField(max_length=50, blank=True, default='', help_text="NTN / STRN Tax number")
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=500000.00)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        if self.company_name:
            return f"{self.name} ({self.company_name})"
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'company_name': self.company_name,
            'phone': self.phone,
            'email': self.email,
            'city': self.city,
            'address': self.address,
            'ntn_tax_id': self.ntn_tax_id,
            'credit_limit': float(self.credit_limit),
            'current_balance': float(self.current_balance),
            'status': self.status,
            'notes': self.notes,
        }
