"""
Master URL configuration for TechImport ERP.
Routes to all app-level URL files.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # ERP modules
    path('', include('dashboard.urls')),
    path('products/', include('products.urls')),
    path('sales/', include('sales.urls')),
    path('purchases/', include('purchases.urls')),
    path('inventory/', include('inventory.urls')),
    path('manufacturing/', include('manufacturing.urls')),
    path('distribution/', include('distribution.urls')),
    path('invoices/', include('invoices.urls')),
    path('payments/', include('payments.urls')),
    path('ledger/', include('ledger.urls')),
    path('reports/', include('reports_app.urls')),
    path('audit-trail/', include('audit_log.urls')),
    path('roles/', include('roles.urls')),
    path('users/', include('users_app.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
