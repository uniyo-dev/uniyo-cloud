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
    
    # LOGO (top center)
    logo_file = BASE_DIR / 'static' / 'images' / 'logo.svg'
    # Note: ReportLab doesn't support SVG directly, skip logo or use PNG version
    
    # Title (compact)
    c.setFillColor(primary)
    c.setFont('Helvetica-Bold', 24)
    c.drawCentredString(w/2, h-25*mm, title.upper())
    
    c.setFillColor(HexColor('#64748b'))
    c.setFont('Helvetica', 12)
    c.drawCentredString(w/2, h-32*mm, 'Ethiopian Higher Education Freshman Hub')
    
    # Divider line
    c.setStrokeColor(primary)
    c.setLineWidth(2)
    c.line(40*mm, h-38*mm, w-40*mm, h-38*mm)
    
    # Presented to
    c.setFillColor(HexColor('#64748b'))
    c.setFont('Helvetica', 14)
    c.drawCentredString(w/2, h-48*mm, 'This certificate is proudly presented to')
    
    # Student name
    c.setFillColor(HexColor('#1e1b4b'))
    c.setFont('Helvetica-Bold', 32)
    c.drawCentredString(w/2, h-58*mm, full_name)
    
    # Reason text (boxed)
    reason = 'For successfully completing lessons and worksheets with dedication.'
    c.setFillColor(HexColor('#334155'))
    c.setFont('Helvetica', 12)
    c.roundRect(40*mm, h-68*mm, w-80*mm, 10*mm, 3*mm, fill=False, stroke=True)
    c.drawCentredString(w/2, h-64*mm, reason)
    
    # University details
    c.setFillColor(HexColor('#64748b'))
    c.setFont('Helvetica', 12)
    details = university
    if stream:
        details += f' • {stream} Science'
    if sex:
        details += f' • {sex}'
    c.drawCentredString(w/2, h-75*mm, details)
    
    # Credentials (in box)
    y = h - 90*mm
    c.setFont('Helvetica', 10)
    c.setFillColor(HexColor('#334155'))
    c.roundRect(30*mm, y-15*mm, w-60*mm, 25*mm, 3*mm, fill=False, stroke=True)
    
    c.drawString(40*mm, y, 'Certificate Number:')
    c.setFillColor(HexColor('#1e1b4b'))
    c.drawRightString(w-40*mm, y, cert_number)
    
    y -= 8*mm
    c.setFillColor(HexColor('#334155'))
    c.drawString(40*mm, y, 'Issue Date:')
    c.setFillColor(HexColor('#1e1b4b'))
    c.drawRightString(w-40*mm, y, issue_date[:10])
    
    y -= 8*mm
    c.setFillColor(HexColor('#334155'))
    c.drawString(40*mm, y, 'Type:')
    c.setFillColor(primary)
    c.drawRightString(w-40*mm, y, cert_type.upper())
    
    # QR Code (bottom left)
    try:
        import qrcode
        from io import BytesIO
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
        verify_url = f"https://uniyo-cloud.onrender.com/verify/{certificate_data.get('verification_token', '')}"
        qr.add_data(verify_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color='black', back_color='white')
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        qr_image = ImageReader(qr_buffer)
        c.drawImage(qr_image, 25*mm, 25*mm, 25*mm, 25*mm, preserveAspectRatio=True)
        c.setFont('Helvetica', 8)
        c.setFillColor(HexColor('#64748b'))
        c.drawCentredString(37*mm, 22*mm, 'Scan to Verify')
    except Exception as e:
        print(f"QR error: {e}")
    
    # Barcode (bottom center)
    c.setLineWidth(1)
    c.setStrokeColor(HexColor('#000000'))
    barcode_x = w/2 - 15*mm
    barcode_y = 30*mm
    import random
    random.seed(cert_number)
    for i in range(40):
        bar_width = random.choice([1, 2]) * 0.5*mm
        c.line(barcode_x, barcode_y, barcode_x, barcode_y + 15*mm)
        barcode_x += bar_width + 0.3*mm
    c.setFont('Courier', 7)
    c.setFillColor(HexColor('#334155'))
    c.drawCentredString(w/2, 26*mm, cert_number)
    
    # Primary Stamp (bottom right of center)
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
        stamp_img = ImageReader(str(stamp_file))
        c.drawImage(stamp_img, w/2+10*mm, 25*mm, 30*mm, 30*mm, preserveAspectRatio=True, mask='auto')
    
    # Secondary stamp (right side)
    if cert_type in ['vip_leaderboard', 'payment', 'promotion']:
        secondary_stamp = auth_dir / 'super_admin_stamp.png'
        if secondary_stamp.exists():
            sec_img = ImageReader(str(secondary_stamp))
            c.drawImage(sec_img, w-45*mm, 30*mm, 22*mm, 22*mm, preserveAspectRatio=True, mask='auto')
    
    # Super Admin signature (bottom left)
    sig_file = auth_dir / 'super_admin_signature.png'
    if sig_file.exists():
        sig_img = ImageReader(str(sig_file))
        c.drawImage(sig_img, 25*mm, 10*mm, 30*mm, 10*mm, preserveAspectRatio=True, mask='auto')
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(HexColor('#1e1b4b'))
        c.drawCentredString(40*mm, 8*mm, 'Chalachew Agegn')
        c.setFont('Helvetica', 7)
        c.setFillColor(HexColor('#64748b'))
        c.drawCentredString(40*mm, 6*mm, 'Super Admin')
    
    # Content Manager signature (bottom right)
    if cert_type not in ['other', 'excellence', 'content_creator', 'marketing_manager', 'advertiser', 'staff', 'special_congratulations', 'participation', 'appreciation', 'congratulations']:
        cm_sig = auth_dir / 'signature_(content_manager).png'
        if cm_sig.exists():
            cm_img = ImageReader(str(cm_sig))
            c.drawImage(cm_img, w-55*mm, 10*mm, 30*mm, 10*mm, preserveAspectRatio=True, mask='auto')
            c.setFont('Helvetica-Bold', 8)
            c.setFillColor(HexColor('#1e1b4b'))
            c.drawCentredString(w-40*mm, 8*mm, 'Banch Destaw')
            c.setFont('Helvetica', 7)
            c.setFillColor(HexColor('#64748b'))
            c.drawCentredString(w-40*mm, 6*mm, 'Content Manager')
    
    # Microtext (bottom center)
    c.setFillColor(HexColor('#94a3b8'))
    c.setFont('Helvetica', 5)
    c.drawCentredString(w/2, 5*mm, 'UNIYO AUTHENTIC CERTIFICATE • VERIFY ONLINE • SECURITY FEATURES INCLUDED • DO NOT COPY • UNIYO AUTHENTIC CERTIFICATE')
    
    c.save()

    
    # Convert PDF to PNG (requires pdf2image on Render)
    return output_pdf
