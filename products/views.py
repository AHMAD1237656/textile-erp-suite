"""
Products app views – full CRUD + JSON API endpoints
"""
import csv
from decimal import Decimal, InvalidOperation
from io import StringIO
import json
import logging
from zipfile import BadZipFile

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.db import models
from django.db.models import Q, Sum, Count, F
from django.core.paginator import Paginator
from django.utils import timezone

from .models import Product, Category, Unit
from .qr_utils import generate_product_qr
from audit_log.utils import log_activity
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

logger = logging.getLogger(__name__)

# ── Realistic sample data (shown when DB is empty) ───────────────────────────
SAMPLE_PRODUCTS = [
    {'sku':'CHG-65W-001', 'name':'USB-C 65W GaN Charger',     'category':'Chargers',  'unit':'Pcs',
     'purchase_price':850,  'selling_price':1299, 'current_stock':340, 'minimum_stock':50,
     'status':'active', 'origin_country':'China', 'tax_rate':17},
    {'sku':'RAM-DDR4-16G', 'name':'DDR4 16GB 3200MHz RAM',    'category':'Memory',    'unit':'Pcs',
     'purchase_price':4200, 'selling_price':6500, 'current_stock':8,   'minimum_stock':50,
     'status':'active', 'origin_country':'China', 'tax_rate':17},
    {'sku':'CBL-HDMI-4K',  'name':'HDMI 2.1 Cable 4K 2m',    'category':'Cables',    'unit':'Pcs',
     'purchase_price':320,  'selling_price':599,  'current_stock':520, 'minimum_stock':100,
     'status':'active', 'origin_country':'China', 'tax_rate':17},
    {'sku':'HUB-USB7-001', 'name':'USB 3.0 Hub 7-Port',       'category':'Hubs',      'unit':'Pcs',
     'purchase_price':1100, 'selling_price':1899, 'current_stock':85,  'minimum_stock':30,
     'status':'active', 'origin_country':'China', 'tax_rate':17},
    {'sku':'SSD-1TB-NVM',  'name':'NVMe SSD 1TB Gen4',        'category':'Storage',   'unit':'Pcs',
     'purchase_price':9500, 'selling_price':14999,'current_stock':42,  'minimum_stock':20,
     'status':'active', 'origin_country':'China', 'tax_rate':17},
    {'sku':'CBL-RJ45-5M',  'name':'CAT6 RJ45 Patch Cable 5m', 'category':'Cables',   'unit':'Pcs',
     'purchase_price':180,  'selling_price':350,  'current_stock':1200,'minimum_stock':200,
     'status':'active', 'origin_country':'China', 'tax_rate':17},
    {'sku':'PB-20K-001',   'name':'Power Bank 20000mAh PD45W','category':'Power',     'unit':'Pcs',
     'purchase_price':2800, 'selling_price':4500, 'current_stock':60,  'minimum_stock':25,
     'status':'active', 'origin_country':'China', 'tax_rate':17},
    {'sku':'CBL-TYCA-001', 'name':'Type-C to A Cable 1m 3A',  'category':'Cables',   'unit':'Pcs',
     'purchase_price':120,  'selling_price':250,  'current_stock':12,  'minimum_stock':100,
     'status':'active', 'origin_country':'China', 'tax_rate':17},
    {'sku':'MSE-WLS-001',  'name':'Wireless Mouse 2.4GHz',    'category':'Peripherals','unit':'Pcs',
     'purchase_price':650,  'selling_price':1199, 'current_stock':95,  'minimum_stock':40,
     'status':'active', 'origin_country':'China', 'tax_rate':17},
    {'sku':'SW-ETH-8P',    'name':'Ethernet Switch 8-Port',   'category':'Networking','unit':'Pcs',
     'purchase_price':3200, 'selling_price':5499, 'current_stock':28,  'minimum_stock':15,
     'status':'active', 'origin_country':'China', 'tax_rate':17},
]


def _get_products_qs():
    """Return live queryset or inject sample data if DB empty."""
    qs = Product.objects.filter(is_deleted=False)
    if not qs.exists():
        # Return sample data as dicts (not model instances) for template display
        return None
    return qs


@login_required
def product_list(request):
    """List page with search, category filter, status filter."""
    query    = request.GET.get('q', '')
    category = request.GET.get('category', '')
    status   = request.GET.get('status', '')

    qs = Product.objects.filter(is_deleted=False)

    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(sku__icontains=query) |
                       Q(barcode__icontains=query))
    if category:
        qs = qs.filter(category__name=category)
    if status:
        qs = qs.filter(status=status)

    paginator = Paginator(qs, 25)
    page      = paginator.get_page(request.GET.get('page', 1))

    categories = Category.objects.all()
    stats = qs.aggregate(
        total_count  = Count('id'),
        total_value  = Sum('current_stock'),
        low_stock_ct = Count('id', filter=Q(current_stock__lte=models.F('minimum_stock'))),
    ) if hasattr(Product, 'objects') else {}

    context = {
        'page_obj':        page,
        'categories':      categories,
        'query':           query,
        'selected_cat':    category,
        'selected_status': status,
        'stats':           stats,
        'sample_products': SAMPLE_PRODUCTS if not qs.exists() else [],
        # Breadcrumbs
        'breadcrumbs': [('Home', '/'), ('Products', None)],
    }
    return render(request, 'products/list.html', context)


@login_required
def product_create(request):
    """Create product (handles both modal AJAX POST and full-page GET)."""
    if request.method == 'POST':
        return _save_product(request, None)

    categories = Category.objects.all()
    units      = Unit.objects.all()
    return render(request, 'products/form.html', {
        'categories': categories,
        'units':      units,
        'action':     'Add Product',
        'breadcrumbs': [('Home','/'),('Products','/products/'),('Add',None)],
    })


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk, is_deleted=False)
    if request.method == 'POST':
        return _save_product(request, product)

    categories = Category.objects.all()
    units      = Unit.objects.all()
    return render(request, 'products/form.html', {
        'product':    product,
        'categories': categories,
        'units':      units,
        'action':     'Edit Product',
        'breadcrumbs': [('Home','/'),('Products','/products/'),('Edit',None)],
    })


def _save_product(request, instance):
    """Shared save logic for create and edit."""
    data = request.POST
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    errors = {}
    if not data.get('name'):      errors['name'] = 'Product name is required.'
    if not data.get('sku'):       errors['sku']  = 'SKU is required.'
    if not data.get('selling_price'): errors['selling_price'] = 'Selling price is required.'

    if errors:
        if is_ajax:
            return JsonResponse({'success': False, 'errors': errors}, status=400)
        # Re-render form with errors
        return render(request, 'products/form.html', {
            'errors': errors, 'data': data,
            'categories': Category.objects.all(), 'units': Unit.objects.all(),
        })

    is_update = instance is not None
    obj = instance or Product()
    obj.name           = data['name']
    obj.sku            = data['sku']
    obj.barcode        = data.get('barcode', '')
    obj.description    = data.get('description', '')
    obj.purchase_price = data.get('purchase_price') or 0
    obj.selling_price  = data.get('selling_price')  or 0
    obj.wholesale_price= data.get('wholesale_price') or 0
    obj.tax_rate       = data.get('tax_rate') or 0
    obj.minimum_stock  = data.get('minimum_stock') or 0
    obj.reorder_qty    = data.get('reorder_qty') or 0
    obj.current_stock  = data.get('current_stock') or 0
    obj.status         = data.get('status', 'active')
    obj.origin_country = data.get('origin_country', 'China')
    obj.hs_code        = data.get('hs_code', '')
    obj.supplier_name  = data.get('supplier_name', '')

    # Category & Unit FK
    cat_name = data.get('category_name')
    if cat_name:
        cat, _ = Category.objects.get_or_create(name=cat_name)
        obj.category = cat

    unit_name = data.get('unit_name')
    if unit_name:
        unit, _ = Unit.objects.get_or_create(name=unit_name, defaults={'abbreviation': unit_name[:5]})
        obj.unit = unit

    # Image upload
    if 'image' in request.FILES:
        obj.image = request.FILES['image']

    obj.save()
    log_activity(
        request,
        'UPDATE' if is_update else 'CREATE',
        'Products',
        f'{"Updated" if is_update else "Created"} product {obj.sku} ({obj.name}).',
    )

    if is_ajax:
        return JsonResponse({'success': True, 'id': obj.pk, 'sku': obj.sku, 'name': obj.name})

    from django.contrib import messages
    messages.success(request, f'Product "{obj.name}" saved successfully.')
    return redirect('products:list')


@login_required
def product_detail(request, pk):
    product    = get_object_or_404(Product, pk=pk, is_deleted=False)
    return render(request, 'products/detail.html', {
        'product': product,
        'breadcrumbs': [('Home','/'),('Products','/products/'),(product.name, None)],
    })


@login_required
def product_qr_code(request, pk):
    """Return a dynamically generated QR code for a product label."""
    product = get_object_or_404(
        Product.objects.select_related('category'),
        pk=pk,
        is_deleted=False,
    )
    response = HttpResponse(
        generate_product_qr(product),
        content_type='image/png',
    )
    response['Cache-Control'] = 'no-store'
    return response


PRODUCT_IMPORT_HEADERS = {
    'name': {'name', 'productname'},
    'sku': {'sku', 'code'},
    'category': {'category'},
    'stock': {'stock', 'quantity', 'stockquantity'},
    'reorder': {'reorderlevel', 'minimumstock', 'minstock'},
    'unit_price': {'unitprice', 'price'},
}


def _normalise_import_header(value):
    return ''.join(character for character in str(value or '').lower() if character.isalnum())


def _read_product_import(upload):
    extension = upload.name.rsplit('.', 1)[-1].lower()
    if extension == 'csv':
        try:
            text = upload.read().decode('utf-8-sig')
            reader = csv.reader(StringIO(text))
            rows = list(reader)
        except (UnicodeDecodeError, csv.Error) as error:
            raise ValueError('The CSV file could not be read as UTF-8.') from error
    elif extension == 'xlsx':
        try:
            workbook = load_workbook(upload, read_only=True, data_only=True)
            worksheet = workbook.active
            rows = list(worksheet.iter_rows(values_only=True))
            workbook.close()
        except (InvalidFileException, BadZipFile, OSError, ValueError) as error:
            raise ValueError('The Excel file is invalid or could not be opened.') from error
    else:
        raise ValueError('Please upload a .csv or .xlsx file.')

    if not rows:
        raise ValueError('The uploaded file is empty.')

    headers = [_normalise_import_header(value) for value in rows[0]]
    indexes = {}
    for field, aliases in PRODUCT_IMPORT_HEADERS.items():
        index = next((i for i, header in enumerate(headers) if header in aliases), None)
        if index is not None:
            indexes[field] = index

    missing = [field for field in PRODUCT_IMPORT_HEADERS if field not in indexes]
    if missing:
        names = {
            'name': 'Name',
            'sku': 'SKU',
            'category': 'Category',
            'stock': 'Stock/Quantity',
            'reorder': 'Reorder Level',
            'unit_price': 'Unit Price',
        }
        raise ValueError('Missing required columns: ' + ', '.join(names[field] for field in missing))

    parsed_rows = []
    for row_number, row in enumerate(rows[1:], start=2):
        if not any(value is not None and str(value).strip() for value in row):
            continue
        values = {
            field: str(row[index]).strip() if index < len(row) and row[index] is not None else ''
            for field, index in indexes.items()
        }
        parsed_rows.append((row_number, values))
    return parsed_rows


def _import_decimal(value, label):
    try:
        number = Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f'{label} must be a valid number.') from error
    if not number.is_finite() or number < 0 or number > Decimal('999999999999.99'):
        raise ValueError(f'{label} must be between 0 and 999999999999.99.')
    return number.quantize(Decimal('0.01'))


@login_required
@require_http_methods(['GET', 'POST'])
def product_import(request):
    if request.method == 'GET':
        return render(request, 'products/import.html', {
            'breadcrumbs': [('Home', '/'), ('Products', '/products/'), ('Import', None)],
        })

    upload = request.FILES.get('file')
    if not upload:
        messages.error(request, 'Choose a CSV or Excel file to import.')
        return redirect('products:list')
    if upload.size > 10 * 1024 * 1024:
        messages.error(request, 'The import file must be smaller than 10 MB.')
        return redirect('products:list')

    try:
        rows = _read_product_import(upload)
    except ValueError as error:
        messages.error(request, str(error))
        return redirect('products:list')

    existing_skus = set(Product.objects.values_list('sku', flat=True))
    seen_skus = set()
    valid_products = []
    row_errors = []
    for row_number, values in rows:
        try:
            name = values['name']
            sku = values['sku']
            category_name = values['category']
            if not name or len(name) > 255:
                raise ValueError('Name is required and must be 255 characters or fewer.')
            if not sku or len(sku) > 50:
                raise ValueError('SKU is required and must be 50 characters or fewer.')
            if sku in existing_skus or sku in seen_skus:
                raise ValueError(f'SKU "{sku}" already exists or is duplicated in this file.')
            if not category_name or len(category_name) > 100:
                raise ValueError('Category is required and must be 100 characters or fewer.')

            stock = _import_decimal(values['stock'], 'Stock/Quantity')
            reorder = _import_decimal(values['reorder'], 'Reorder Level')
            unit_price = _import_decimal(values['unit_price'], 'Unit Price')
            valid_products.append({
                'sku': sku,
                'name': name,
                'category_name': category_name,
                'current_stock': stock,
                'minimum_stock': reorder,
                'purchase_price': unit_price,
                'selling_price': unit_price,
            })
            seen_skus.add(sku)
        except ValueError as error:
            row_errors.append(f'Row {row_number}: {error}')

    imported_count = 0
    try:
        with transaction.atomic():
            for values in valid_products:
                category, _ = Category.objects.get_or_create(
                    name=values.pop('category_name'),
                )
                Product.objects.create(category=category, **values)
                imported_count += 1
    except Exception:
        logger.exception('Bulk product import failed while saving valid rows')
        messages.error(request, 'The import could not be saved. No products were imported.')
        return redirect('products:list')

    if row_errors:
        details = ' '.join(row_errors[:5])
        if len(row_errors) > 5:
            details += f' (+{len(row_errors) - 5} more row errors)'
        messages.warning(
            request,
            f'Successfully imported {imported_count} products. '
            f'{len(row_errors)} row(s) skipped. {details}',
        )
    else:
        messages.success(request, f'Successfully imported {imported_count} products.')
    if imported_count:
        log_activity(
            request,
            'IMPORT',
            'Products',
            f'Imported {imported_count} products; skipped {len(row_errors)} invalid rows.',
        )
    return redirect('products:list')


@login_required
@require_http_methods(['GET'])
def product_import_sample(request):
    output = StringIO(newline='')
    writer = csv.writer(output)
    writer.writerow(['Name', 'SKU', 'Category', 'Stock/Quantity', 'Reorder Level', 'Unit Price'])
    response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="product_import_template.csv"'
    return response


@login_required
@require_http_methods(['POST', 'DELETE'])
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, is_deleted=False)
    product.is_deleted = True  # Soft delete
    product.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': f'"{product.name}" deleted.'})
    from django.contrib import messages
    messages.success(request, f'Product "{product.name}" deleted.')
    return redirect('products:list')


# ── JSON API endpoints (used by DataTables & other pages) ────────────────────

@login_required
def api_products(request):
    """
    GET /products/api/?q=&category=&status=
    Returns product list as JSON for DataTables server-side processing.

    Sample JSON response:
    {
      "draw": 1,
      "recordsTotal": 10,
      "recordsFiltered": 10,
      "data": [
        {"id":1, "sku":"CHG-65W-001", "name":"USB-C 65W GaN Charger",
         "category":"Chargers", "unit":"Pcs", "selling_price":"1299.00",
         "current_stock":"340.00", "minimum_stock":"50.00",
         "is_low_stock": false, "status":"active"},
        ...
      ]
    }
    """
    q      = request.GET.get('q','')
    status = request.GET.get('status','')
    cat    = request.GET.get('category','')

    qs = Product.objects.filter(is_deleted=False)
    if q:      qs = qs.filter(Q(name__icontains=q)|Q(sku__icontains=q))
    if status: qs = qs.filter(status=status)
    if cat:    qs = qs.filter(category__name=cat)

    # If DB empty return sample data
    if not qs.exists():
        return JsonResponse({
            'draw': 1, 'recordsTotal': len(SAMPLE_PRODUCTS),
            'recordsFiltered': len(SAMPLE_PRODUCTS),
            'data': [dict(p, id=i+1, is_low_stock=p['current_stock']<=p['minimum_stock'])
                     for i, p in enumerate(SAMPLE_PRODUCTS)],
        })

    data = [{
        'id':             p.pk,
        'sku':            p.sku,
        'name':           p.name,
        'category':       p.category.name if p.category else '—',
        'unit':           p.unit.name if p.unit else '—',
        'purchase_price': str(p.purchase_price),
        'selling_price':  str(p.selling_price),
        'current_stock':  str(p.current_stock),
        'minimum_stock':  str(p.minimum_stock),
        'is_low_stock':   p.is_low_stock,
        'stock_value':    str(p.stock_value),
        'profit_margin':  p.profit_margin,
        'status':         p.status,
    } for p in qs[:500]]

    return JsonResponse({
        'draw': int(request.GET.get('draw', 1)),
        'recordsTotal': qs.count(),
        'recordsFiltered': qs.count(),
        'data': data,
    })


@login_required
def api_product_search(request):
    """
    GET /products/api/search/?q=usb
    Lightweight search for Select2 / invoice line-item autocomplete.

    Sample response:
    {"results": [{"id":1, "text":"USB-C 65W GaN Charger", "sku":"CHG-65W-001",
                  "price":"1299.00", "unit":"Pcs", "stock":"340.00"}]}
    """
    q = request.GET.get('q', '')
    if len(q) < 2:
        # Return sample data for demo
        results = [{'id':i+1,'text':p['name'],'sku':p['sku'],
                    'price':str(p['selling_price']),'unit':p['unit'],
                    'stock':str(p['current_stock'])}
                   for i,p in enumerate(SAMPLE_PRODUCTS) if q.lower() in p['name'].lower()]
        return JsonResponse({'results': results[:10]})

    qs = Product.objects.filter(
        is_deleted=False, status='active'
    ).filter(Q(name__icontains=q) | Q(sku__icontains=q) | Q(barcode=q))[:20]

    results = [{'id': p.pk, 'text': p.name, 'sku': p.sku,
                'price': str(p.selling_price), 'unit': p.unit.name if p.unit else '',
                'stock': str(p.current_stock)} for p in qs]
    return JsonResponse({'results': results})


# fix missing import
from django.db import models as django_models
