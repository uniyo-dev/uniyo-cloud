"""
UNIYO LMS - Certificate ReportLab Dispatcher
"""

from core.certificates.receipt import generate_payment_receipt_banknote
from core.certificates.vip import generate_a4_landscape_certificate_reportlab
from core.certificates.completion import generate_completion_certificate
from core.certificates.appreciate import generate_appreciation_certificate
from core.certificates.congrats import generate_congratulations_certificate
from core.certificates.participate import generate_participation_certificate
from core.certificates.create import generate_creator_certificate

def generate_certificate_reportlab(certificate_data, qr_data_uri=None):
    cert_type = certificate_data.get('certificate_type', 'completion').lower()
    
    if 'payment' in cert_type or 'paid' in cert_type:
        return generate_payment_receipt_banknote(certificate_data, qr_data_uri)
    elif 'vip' in cert_type or 'promotion' in cert_type:
        return generate_a4_landscape_certificate_reportlab(certificate_data, qr_data_uri)
    elif 'completion' in cert_type:
        return generate_completion_certificate(certificate_data, qr_data_uri)
    elif cert_type in ['appreciation', 'staff']:
        return generate_appreciation_certificate(certificate_data, qr_data_uri)
    elif cert_type in ['congratulations', 'special_congratulations']:
        return generate_congratulations_certificate(certificate_data, qr_data_uri)
    elif cert_type in ['participation', 'excellence', 'advertiser']:
        return generate_participation_certificate(certificate_data, qr_data_uri)
    elif cert_type in ['content_creator', 'marketing_manager']:
        return generate_creator_certificate(certificate_data, qr_data_uri)
    else:
        return generate_completion_certificate(certificate_data, qr_data_uri)
