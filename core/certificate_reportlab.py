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
    
    # ============================================
    # EXACT A4 LAYOUT (210mm x 297mm)
    # ============================================
    # Measurements are in millimeters (mm)
    # Page: 210mm wide, 297mm tall
    # Margins: 15mm on all sides
    # Usable area: 180mm x 267mm
    # ============================================
    
    # LOGO (top center, at 15mm from top)
    logo_file = BASE_DIR / 'static' / 'images' / 'logo.png'
    if not logo_file.exists():
        logo_file = BASE_DIR / 'static' / 'icons' / 'app_icon-192.png'
    if logo_file.exists():
        logo_img = ImageReader(str(logo_file))
        c.drawImage(logo_img, w/2-10*mm, h-25*mm, 20*mm, 20*mm, preserveAspectRatio=True, mask='auto')
    
    # TITLE (at 40mm from top, centered)
    c.setFillColor(primary)
    c.setFont('Helvetica-Bold', 26)
    c.drawCentredString(w/2, h-40*mm, title.upper())
    
    # SUBTITLE (at 48mm from top)
    c.setFillColor(HexColor('#64748b'))
    c.setFont('Helvetica', 12)
    c.drawCentredString(w/2, h-48*mm, 'Ethiopian Higher Education Freshman Hub')
    
    # DIVIDER LINE (at 54mm from top)
    c.setStrokeColor(primary)
    c.setLineWidth(1.5)
    c.line(30*mm, h-54*mm, w-30*mm, h-54*mm)
    
    # "PRESENTED TO" (at 62mm from top)
    c.setFillColor(HexColor('#64748b'))
    c.setFont('Helvetica', 13)
    c.drawCentredString(w/2, h-62*mm, 'This certificate is proudly presented to')
    
    # STUDENT NAME (at 72mm from top)
    c.setFillColor(HexColor('#1e1b4b'))
    c.setFont('Helvetica-Bold', 34)
    c.drawCentredString(w/2, h-72*mm, full_name)
    
    # REASON TEXT BOX (at 80mm from top, boxed)
    reason = 'For successfully completing lessons and worksheets with dedication.'
    c.setFillColor(HexColor('#334155'))
    c.setFont('Helvetica', 11)
    c.roundRect(35*mm, h-86*mm, w-70*mm, 10*mm, 3*mm, fill=False, stroke=True)
    c.drawCentredString(w/2, h-81*mm, reason)
    
    # UNIVERSITY DETAILS (at 94mm from top)
    c.setFillColor(HexColor('#64748b'))
    c.setFont('Helvetica', 11)
    details = university
    if stream:
        details += f' • {stream} Science'
    if sex:
        details += f' • {sex}'
    c.drawCentredString(w/2, h-94*mm, details)
    
    # CREDENTIALS BOX (at 104mm to 130mm from top)
    cred_y = h - 108*mm
    c.roundRect(30*mm, cred_y-20*mm, w-60*mm, 28*mm, 3*mm, fill=False, stroke=True)
    
    c.setFont('Helvetica', 10)
    c.setFillColor(HexColor('#334155'))
    c.drawString(40*mm, cred_y, 'Certificate Number:')
    c.setFillColor(HexColor('#1e1b4b'))
    c.drawRightString(w-40*mm, cred_y, cert_number)
    
    cred_y -= 8*mm
    c.setFillColor(HexColor('#334155'))
    c.drawString(40*mm, cred_y, 'Issue Date:')
    c.setFillColor(HexColor('#1e1b4b'))
    c.drawRightString(w-40*mm, cred_y, issue_date[:10])
    
    cred_y -= 8*mm
    c.setFillColor(HexColor('#334155'))
    c.drawString(40*mm, cred_y, 'Type:')
    c.setFillColor(primary)
    c.drawRightString(w-40*mm, cred_y, cert_type.upper())
    
    # VERIFY URL (at 140mm from top)
    c.setFillColor(primary)
    c.setFont('Helvetica', 9)
    verify_url = f"https://uniyo-cloud.onrender.com/verify/{certificate_data.get('verification_token', '')}"
    c.drawCentredString(w/2, h-140*mm, f'Verify at: {verify_url}')
    
    # ============================================
    # BOTTOM SECTION (150mm to 280mm from top)
    # ============================================
    
    # QR CODE (bottom left, at 180mm from top = 35mm from bottom)
    try:
        import qrcode
        from io import BytesIO
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
        qr.add_data(verify_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color='black', back_color='white')
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        qr_image = ImageReader(qr_buffer)
        # QR at: left 25mm, bottom 35mm
        c.drawImage(qr_image, 25*mm, 30*mm, 28*mm, 28*mm, preserveAspectRatio=True)
        c.setFont('Helvetica', 8)
        c.setFillColor(HexColor('#64748b'))
        c.drawCentredString(39*mm, 27*mm, 'Scan to Verify')
    except Exception as e:
        print(f"QR error: {e}")
    
    # PRIMARY STAMP (bottom center, at 35mm from bottom)
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
        # Stamp at: center, bottom 30mm
        c.drawImage(stamp_img, w/2-17*mm, 28*mm, 34*mm, 34*mm, preserveAspectRatio=True, mask='auto')
    
    # SECONDARY STAMP (right side, at 40mm from bottom)
    if cert_type in ['vip_leaderboard', 'payment', 'promotion']:
        secondary_stamp = auth_dir / 'super_admin_stamp.png'
        if secondary_stamp.exists():
            sec_img = ImageReader(str(secondary_stamp))
            # Secondary at: right 30mm, bottom 40mm
            c.drawImage(sec_img, w-45*mm, 38*mm, 24*mm, 24*mm, preserveAspectRatio=True, mask='auto')
    
    # SUPER ADMIN SIGNATURE (bottom left, at 15mm from bottom)
    sig_file = auth_dir / 'super_admin_signature.png'
    if sig_file.exists():
        sig_img = ImageReader(str(sig_file))
        # Signature at: left 25mm, bottom 12mm
        c.drawImage(sig_img, 25*mm, 12*mm, 32*mm, 10*mm, preserveAspectRatio=True, mask='auto')
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(HexColor('#1e1b4b'))
        c.drawCentredString(41*mm, 10*mm, 'Chalachew Agegn')
        c.setFont('Helvetica', 7)
        c.setFillColor(HexColor('#64748b'))
        c.drawCentredString(41*mm, 7*mm, 'Super Admin')
    
    # CONTENT MANAGER SIGNATURE (bottom right, at 15mm from bottom)
    if cert_type not in ['other', 'excellence', 'content_creator', 'marketing_manager', 'advertiser', 'staff', 'special_congratulations', 'participation', 'appreciation', 'congratulations']:
        cm_sig = auth_dir / 'signature_(content_manager).png'
        if cm_sig.exists():
            cm_img = ImageReader(str(cm_sig))
            # CM at: right 25mm, bottom 12mm
            c.drawImage(cm_img, w-57*mm, 12*mm, 32*mm, 10*mm, preserveAspectRatio=True, mask='auto')
            c.setFont('Helvetica-Bold', 8)
            c.setFillColor(HexColor('#1e1b4b'))
            c.drawCentredString(w-41*mm, 10*mm, 'Banch Destaw')
            c.setFont('Helvetica', 7)
            c.setFillColor(HexColor('#64748b'))
            c.drawCentredString(w-41*mm, 7*mm, 'Content Manager')
    
    # BARCODE (bottom center, at 15mm from bottom)
    c.setLineWidth(1)
    c.setStrokeColor(HexColor('#000000'))
    barcode_x = w/2 + 20*mm
    barcode_y = 12*mm
    import random
    random.seed(cert_number)
    for i in range(30):
        bar_width = random.choice([1, 2]) * 0.4*mm
        c.line(barcode_x, barcode_y, barcode_x, barcode_y + 12*mm)
        barcode_x += bar_width + 0.3*mm
    c.setFont('Courier', 6)
    c.setFillColor(HexColor('#334155'))
    c.drawCentredString(w/2 + 40*mm, 9*mm, cert_number[:30])
    
    # MICROTEXT (very bottom, at 3mm from bottom)
    c.setFillColor(HexColor('#94a3b8'))
    c.setFont('Helvetica', 5)
    c.drawCentredString(w/2, 4*mm, 'UNIYO AUTHENTIC CERTIFICATE • VERIFY ONLINE • SECURITY FEATURES INCLUDED • DO NOT COPY • UNIYO AUTHENTIC CERTIFICATE')
    
    c.save()


    
    # Convert PDF to PNG (requires pdf2image on Render)
    return output_pdf
