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
    
    # QR Code
    try:
        import qrcode
        from io import BytesIO
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
        qr.add_data(f"{certificate_data.get('verification_token', '')}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color='black', back_color='white')
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        qr_image = ImageReader(qr_buffer)
        c.drawImage(qr_image, w-50*mm, 15*mm, 30*mm, 30*mm, preserveAspectRatio=True)
    except Exception as e:
        print(f"QR error: {e}")

    # Barcode (using simple lines)
    c.setLineWidth(1)
    c.setStrokeColor(HexColor('#000000'))
    barcode_x = w/2 + 10*mm
    barcode_y = 15*mm
    import random
    random.seed(certificate_data.get('certificate_number', 'UNKNOWN'))
    for i in range(50):
        bar_width = random.choice([1, 2, 3]) * 0.5*mm
        c.line(barcode_x, barcode_y, barcode_x, barcode_y + 20*mm)
        barcode_x += bar_width + 0.5*mm
    # Barcode text
    c.setFont('Courier', 8)
    c.setFillColor(HexColor('#334155'))
    c.drawCentredString(w/2 + 40*mm, 12*mm, cert_number)
    
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
    
    # Secondary stamp for VIP/Payment/Promo
    if cert_type in ['vip_leaderboard', 'payment', 'promotion']:
        secondary_stamp = auth_dir / 'super_admin_stamp.png'
        if secondary_stamp.exists():
            c.drawImage(ImageReader(str(secondary_stamp)), w-60*mm, 35*mm, 30*mm, 30*mm, preserveAspectRatio=True)
    
    # Signatures (Super Admin + Content Manager)
    sig_file = auth_dir / 'super_admin_signature.png'
    if sig_file.exists():
        c.drawImage(ImageReader(str(sig_file)), w/2-60*mm, 15*mm, 35*mm, 12*mm, preserveAspectRatio=True)
        # Super Admin name
        c.setFont('Helvetica-Bold', 10)
        c.setFillColor(HexColor('#1e1b4b'))
        c.drawCentredString(w/2-42*mm, 12*mm, 'Chalachew Agegn')
        c.setFont('Helvetica', 8)
        c.setFillColor(HexColor('#64748b'))
        c.drawCentredString(w/2-42*mm, 9*mm, 'Super Admin')
    
    # Content Manager signature
    cm_sig = auth_dir / 'signature_(content_manager).png'
    if cm_sig.exists() and cert_type not in ['other', 'excellence', 'content_creator', 'marketing_manager', 'advertiser', 'staff', 'special_congratulations', 'participation', 'appreciation', 'congratulations']:
        c.drawImage(ImageReader(str(cm_sig)), w/2+25*mm, 15*mm, 35*mm, 12*mm, preserveAspectRatio=True)
        c.setFont('Helvetica-Bold', 10)
        c.setFillColor(HexColor('#1e1b4b'))
        c.drawCentredString(w/2+42*mm, 12*mm, 'Banch Destaw')
        c.setFont('Helvetica', 8)
        c.setFillColor(HexColor('#64748b'))
        c.drawCentredString(w/2+42*mm, 9*mm, 'Content Manager')
    
    # Microtext
    c.setFillColor(HexColor('#94a3b8'))
    c.setFont('Helvetica', 8)
    # Enhanced microtext with multiple security layers
    c.setFillColor(HexColor('#94a3b8'))
    c.setFont('Helvetica', 6)
    c.drawCentredString(w/2, 6*mm, 'UNIYO AUTHENTIC CERTIFICATE • VERIFY ONLINE • SECURITY FEATURES INCLUDED • DO NOT COPY')
    c.setFont('Courier', 5)
    c.setFillColor(HexColor('#cbd5e1'))
    c.drawCentredString(w/2, 4*mm, 'UNIYO AUTHENTIC CERTIFICATE • VERIFY ONLINE • SECURITY FEATURES INCLUDED • DO NOT COPY • UNIYO AUTHENTIC CERTIFICATE')
    
    c.save()
    
    # Convert PDF to PNG (requires pdf2image on Render)
    return output_pdf
