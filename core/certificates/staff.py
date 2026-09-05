"""Main Dispatcher - Routes to correct generator"""
from .receipt import generate_payment_receipt_reportlab
from .vip import generate_a4_landscape_certificate_reportlab
from .completion import generate_a4_portrait_certificate_reportlab

# ==============================================================================
# MAIN ROUTING GATEWAY
# ==============================================================================

def generate_certificate_reportlab(certificate_data, qr_data_uri=None):
    """
    Main PDF Generator Gateway.
    Routes certificates based on orientation requirements:
    - A6_PORTRAIT  -> Payment Receipts (A6 Portrait: 105mm x 148mm)
    - A4_LANDSCAPE -> VIP & Promotion Certificates (A4 Landscape: 297mm x 210mm)
    - A4_PORTRAIT  -> Completion & Other Certificates (A4 Portrait: 210mm x 297mm)
    """
    meta = resolve_certificate_meta(certificate_data)
    
    if meta['orientation'] == 'A6_PORTRAIT':
        return generate_payment_receipt_reportlab(certificate_data, qr_data_uri)
    elif meta['orientation'] == 'A4_LANDSCAPE':
        return generate_a4_landscape_certificate_reportlab(certificate_data, qr_data_uri)
    else:
        return generate_a4_portrait_certificate_reportlab(certificate_data, qr_data_uri)
