"""
UNIYO LMS - Certificate Generator using ReportLab (Professional Quality)
"""

from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from core.paths import CERTIFICATES_DIR, BASE_DIR

def generate_certificate_reportlab(certificate_data, qr_data_uri):
    """Generate professional certificate using ReportLab"""
    cert_type = certificate_data.get('certificate_type', 'completion')
    full_name = certificate_data.get('full_name', 'Student')
    university = certificate_data.get('university', '')
    stream = certificate_data.get('stream', '')
    sex = certificate_data.get('sex', '')
    cert_number = certificate_data.get('certificate_number', 'UNKNOWN')
    title = certificate_data.get('title', 'Certificate')
    issue_date = certificate_data.get('issue_date', '')
    rank = certificate_data.get('rank')
    
    cert_id = cert_number.replace('/', '_').replace('\\', '_')
    
    # Use A4 landscape for VIP/Promo, portrait for others
    if cert_type in ['vip_leaderboard', 'promotion']:
        page_size = landscape(A4)
    else:
        page_size = A4
    
    output_pdf = CERTIFICATES_DIR / f"{cert_id}.pdf"
    output_png = CERTIFICATES_DIR / f"{cert_id}.png"
    
    # Colors
    colors = {
        'vip_leaderboard': HexColor('#F59E0B'),
        'payment': HexColor('#14B8A6'),
        'promotion': HexColor('#F97316'),
        'other': HexColor('#38BDF8'),
    }
    primary = colors.get(cert_type, HexColor('#6D28D9'))
    
    c = canvas.Canvas(str(output_pdf), pagesize=page_size)
    w, h = page_size
    
    # Background
    c.setFillColor(HexColor('#fffdf9'))
    c.rect(0, 0, w, h, fill=True, stroke=False)
    
    # Double border
    c.setStrokeColor(primary)
    c.setLineWidth(5)
    c.rect(10*mm, 10*mm, w-20*mm, h-20*mm, fill=False, stroke=True)
    
    c.setStrokeColor(HexColor('#F59E0B'))
    c.setLineWidth(2)
    c.rect(12*mm, 12*mm, w-24*mm, h-24*mm, fill=False, stroke=True)
    
    # Corner ornaments
    corner = 30*mm
    c.setLineWidth(8)
    c.line(10*mm, 10*mm+corner, 10*mm, 10*mm)
    c.line(10*mm, 10*mm, 10*mm+corner, 10*mm)
    c.line(w-10*mm, 10*mm+corner, w-10*mm, 10*mm)
    c.line(w-10*mm, 10*mm, w-10*mm-corner, 10*mm)
    c.line(10*mm, h-10*mm-corner, 10*mm, h-10*mm)
    c.line(10*mm, h-10*mm, 10*mm+corner, h-10*mm)
    c.line(w-10*mm, h-10*mm-corner, w-10*mm, h-10*mm)
    c.line(w-10*mm, h-10*mm, w-10*mm-corner, h-10*mm)
    
    # Watermark
    c.saveState()
    c.translate(w/2, h/2)
    c.rotate(30)
    c.setFillColor(HexColor('#6D28D9'))
    c.setFont('Helvetica-Bold', 100)
    c.setFillAlpha(0.05)
    c.drawCentredString(0, 0, 'UNIYO')
    c.restoreState()
    
    # Title
    c.setFillColor(primary)
    c.setFont('Helvetica-Bold', 36)
    c.drawCentredString(w/2, h-60*mm, title.upper())
    
    c.setFillColor(HexColor('#64748b'))
    c.setFont('Helvetica', 14)
    c.drawCentredString(w/2, h-70*mm, 'Ethiopian Higher Education Freshman Hub')
    
    # Presented to
    c.setFont('Helvetica', 16)
    c.drawCentredString(w/2, h-100*mm, 'This certificate is proudly presented to')
    
    # Student name
    c.setFillColor(HexColor('#1e1b4b'))
    c.setFont('Helvetica-Bold', 48)
    c.drawCentredString(w/2, h-115*mm, full_name)
    
    # Reason
    c.setFillColor(HexColor('#334155'))
    c.setFont('Helvetica', 16)
    reason = 'For successfully completing lessons and worksheets with dedication.'
    c.drawCentredString(w/2, h-130*mm, reason)
    
    # University details
    c.setFillColor(HexColor('#64748b'))
    c.setFont('Helvetica', 14)
    details = university
    if stream:
        details += f' • {stream} Science'
    if sex:
        details += f' • {sex}'
    c.drawCentredString(w/2, h-140*mm, details)
    
    # Credentials
    y = h - 160*mm
    c.setFont('Helvetica', 12)
    c.setFillColor(HexColor('#334155'))
    c.drawString(40*mm, y, 'Certificate Number:')
    c.setFillColor(HexColor('#1e1b4b'))
    c.drawRightString(w-40*mm, y, cert_number)
    
    y -= 10*mm
    c.setFillColor(HexColor('#334155'))
    c.drawString(40*mm, y, 'Issue Date:')
    c.setFillColor(HexColor('#1e1b4b'))
    c.drawRightString(w-40*mm, y, issue_date[:10])
    
    y -= 10*mm
    c.setFillColor(HexColor('#334155'))
    c.drawString(40*mm, y, 'Type:')
    c.setFillColor(primary)
    c.drawRightString(w-40*mm, y, cert_type.upper())
    
    # Stamps
    auth_dir = BASE_DIR / 'static' / 'Authenticity'
    if cert_type == 'vip_leaderboard' and rank:
        stamp_file = auth_dir / f'vip{min(rank,5)}.png'
    elif cert_type == 'payment':
        stamp_file = auth_dir / 'paid.png'
    elif cert_type == 'promotion':
        stamp_file = auth_dir / 'promotion.png'
    else:
        stamp_file = auth_dir / 'general.png'
    
    if stamp_file.exists():
        c.drawImage(ImageReader(str(stamp_file)), w/2-20*mm, 25*mm, 40*mm, 40*mm, preserveAspectRatio=True)
    
    # Signature
    sig_file = auth_dir / 'super_admin_signature.png'
    if sig_file.exists():
        c.drawImage(ImageReader(str(sig_file)), w/2-50*mm, 15*mm, 40*mm, 15*mm, preserveAspectRatio=True)
    
    # Microtext
    c.setFillColor(HexColor('#94a3b8'))
    c.setFont('Helvetica', 8)
    c.drawCentredString(w/2, 8*mm, 'UNIYO AUTHENTIC CERTIFICATE • VERIFY ONLINE • SECURITY FEATURES INCLUDED')
    
    c.save()
    
    # Convert PDF to PNG (requires pdf2image on Render)
    return output_pdf
