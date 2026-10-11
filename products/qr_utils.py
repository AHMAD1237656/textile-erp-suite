"""Utilities for generating printable product-identification QR codes."""
from io import BytesIO
import json

import qrcode
from django.utils.encoding import force_str


def product_qr_payload(product):
    """Build a stable, machine-readable payload from current product details."""
    return json.dumps({
        'name': force_str(product.name),
        'sku': force_str(product.sku),
        'category': force_str(product.category.name if product.category else ''),
        'current_stock': force_str(product.current_stock),
    }, ensure_ascii=False)


def generate_product_qr(product):
    """Return a PNG QR code containing the product's current identifying data."""
    qr_code = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=4,
    )
    qr_code.add_data(product_qr_payload(product))
    qr_code.make(fit=True)

    image = qr_code.make_image(fill_color='black', back_color='white')
    output = BytesIO()
    image.save(output, format='PNG')
    return output.getvalue()
