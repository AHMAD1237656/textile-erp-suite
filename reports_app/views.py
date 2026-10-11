"""
Reports app views – Financial analytics, P&L statements, sales & purchase breakdowns
"""
from io import BytesIO
from xml.sax.saxutils import escape

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from products.models import Product
from audit_log.utils import log_activity


REPORT_DEFINITIONS = {
    'sales': {
        'title': 'Sales Report',
        'headers': (
            'Invoice #', 'Date', 'Client', 'City', 'Total', 'Paid', 'Balance',
            'Status',
        ),
        'currency_columns': (4, 5, 6),
        'quantity_columns': (),
    },
    'inventory': {
        'title': 'Inventory Report',
        'headers': (
            'SKU', 'Product', 'Category', 'Quantity', 'Unit', 'Unit Cost',
            'Stock Value', 'Minimum Stock', 'Reorder Quantity',
        ),
        'currency_columns': (5, 6),
        'quantity_columns': (3, 7, 8),
    },
}


def _get_report_rows(report_type):
    """Return the current backend records and formatting metadata for a report."""
    definition = REPORT_DEFINITIONS[report_type]

    if report_type == 'sales':
        # The sales module currently exposes its invoice list from this source.
        from sales.views import SAMPLE_SALES

        rows = (
            (
                sale['number'],
                sale['date'],
                sale['client_name'],
                sale['client_city'],
                sale['total_amount'],
                sale['paid_amount'],
                sale['balance'],
                sale['status'].title(),
            )
            for sale in SAMPLE_SALES
        )
    else:
        products = (
            Product.objects.filter(is_deleted=False)
            .select_related('category', 'unit')
            .order_by('sku')
        )
        rows = (
            (
                product.sku,
                product.name,
                product.category.name if product.category else '',
                product.current_stock,
                product.unit.abbreviation if product.unit else '',
                product.purchase_price,
                product.stock_value,
                product.minimum_stock,
                product.reorder_qty,
            )
            for product in products
        )

    return definition, list(rows)


def _report_type(request):
    report_type = request.GET.get('type', 'sales').lower()
    if report_type not in REPORT_DEFINITIONS:
        return None
    return report_type


def _invalid_report_response():
    return JsonResponse(
        {'status': 'error', 'message': 'Report type must be "sales" or "inventory".'},
        status=400,
    )


def _safe_excel_value(value):
    if isinstance(value, str) and value.lstrip().startswith(('=', '+', '-', '@')):
        return f"'{value}"
    return value


@require_GET
def export_excel(request):
    """Download a formatted Excel report for sales or current inventory."""
    report_type = _report_type(request)
    if report_type is None:
        return _invalid_report_response()

    definition, rows = _get_report_rows(report_type)
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = definition['title'][:31]
    worksheet.append(definition['headers'])

    for row in rows:
        worksheet.append([_safe_excel_value(value) for value in row])

    header_fill = PatternFill('solid', fgColor='1E5EFF')
    for cell in worksheet[1]:
        cell.font = Font(color='FFFFFF', bold=True)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')

    for row in worksheet.iter_rows(min_row=2):
        for column in definition['currency_columns']:
            row[column].number_format = '"₨"#,##0.00;[Red]-"₨"#,##0.00'
        for column in definition['quantity_columns']:
            row[column].number_format = '#,##0.##'

    for column_cells in worksheet.columns:
        column_index = column_cells[0].column
        longest = max(
            (len(str(cell.value or '')) for cell in column_cells),
            default=0,
        )
        worksheet.column_dimensions[get_column_letter(column_index)].width = min(
            max(longest + 2, 12), 36
        )

    worksheet.freeze_panes = 'A2'
    worksheet.auto_filter.ref = worksheet.dimensions

    output = BytesIO()
    workbook.save(output)
    response = HttpResponse(
        output.getvalue(),
        content_type=(
            'application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.sheet'
        ),
    )
    response['Content-Disposition'] = 'attachment; filename="sales_report.xlsx"'
    log_activity(request, 'EXPORT', 'Reports', f'Exported {report_type} report as Excel.')
    return response


@require_GET
def export_pdf(request):
    """Download a styled PDF report for sales or current inventory."""
    report_type = _report_type(request)
    if report_type is None:
        return _invalid_report_response()

    definition, rows = _get_report_rows(report_type)
    output = BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=landscape(letter),
        rightMargin=0.45 * inch,
        leftMargin=0.45 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        title=definition['title'],
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Title'],
        textColor=colors.HexColor('#173B7A'),
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    cell_style = ParagraphStyle(
        'ReportCell',
        parent=styles['BodyText'],
        fontSize=7,
        leading=9,
        spaceAfter=0,
    )
    header_style = ParagraphStyle(
        'ReportHeader',
        parent=cell_style,
        textColor=colors.white,
        fontName='Helvetica-Bold',
    )

    table_data = [[
        Paragraph(escape(str(header)), header_style)
        for header in definition['headers']
    ]]
    for row in rows:
        formatted_row = []
        for column, value in enumerate(row):
            if column in definition['currency_columns']:
                value = f'₨ {value:,.2f}'
            elif column in definition['quantity_columns']:
                value = f'{value:,.2f}'.rstrip('0').rstrip('.')
            formatted_row.append(Paragraph(escape(str(value)), cell_style))
        table_data.append(formatted_row)

    available_width = landscape(letter)[0] - document.leftMargin - document.rightMargin
    column_width = available_width / len(definition['headers'])
    report_table = Table(
        table_data,
        colWidths=[column_width] * len(definition['headers']),
        repeatRows=1,
        hAlign='LEFT',
    )
    report_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E5EFF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
            colors.white, colors.HexColor('#F2F6FC'),
        ]),
        ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#D6DEEA')),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))

    document.build([
        Paragraph(escape(definition['title']), title_style),
        Paragraph(
            f'Generated {timezone.localtime():%Y-%m-%d %H:%M}',
            styles['Normal'],
        ),
        Spacer(1, 0.2 * inch),
        report_table,
    ])
    response = HttpResponse(output.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
    log_activity(request, 'EXPORT', 'Reports', f'Exported {report_type} report as PDF.')
    return response

def reports_index(request):
    """Reports hub page with Chart.js analytics and custom builder"""
    context = {
        'breadcrumbs': [('Home', '/'), ('Reports', None)],
        'categories': ['Chargers', 'Cables', 'Memory', 'Storage', 'Networking', 'Power'],
    }
    return render(request, 'reports_app/index.html', context)

def api_report_data(request):
    """JSON API endpoint returning data for dynamic reports"""
    report_type = request.GET.get('type', 'sales')
    data = {
        'status': 'success',
        'report': report_type,
        'summary': {
            'total_revenue': 148200000,
            'total_cogs': 105400000,
            'gross_profit': 42800000,
            'net_profit': 28400000,
        }
    }
    return JsonResponse(data)
