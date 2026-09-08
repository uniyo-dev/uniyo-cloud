"""
UNIYO LMS - Certificate ReportLab Dispatcher
THIN DISPATCHER: Routes to correct generator module
"""

from core.certificates.receipt import generate_payment_receipt_banknote
from core.certificates.vip import generate_a4_landscape_certificate_reportlab
from core.certificates.completion import generate_completion_certificate
from core.certificates.custom import generate_custom_certificate

def generate_certificate_reportlab(certificate_data, qr_data_uri=None):
    """Route to correct certificate generator based on type."""
    cert_type = certificate_data.get('certificate_type', 'completion').lower()
    
    if 'payment' in cert_type or 'paid' in cert_type:
        return generate_payment_receipt_banknote(certificate_data, qr_data_uri)
    elif 'vip' in cert_type or 'promotion' in cert_type:
        return generate_a4_landscape_certificate_reportlab(certificate_data, qr_data_uri)
    elif 'completion' in cert_type:
        return generate_completion_certificate(certificate_data, qr_data_uri)
    else:
        # ALL OTHER TYPES (appreciation, staff, congratulations, etc.)
        return generate_custom_certificate(certificate_data, qr_data_uri)
