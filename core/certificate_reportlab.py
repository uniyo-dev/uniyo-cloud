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
    """Generate PROFESSIONAL certificate using ReportLab with HIGH QUALITY"""
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from core.paths import CERTIFICATES_DIR, BASE_DIR
    
    # Register high-quality TrueType fonts
    font_paths = [
        ('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
        ('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
    ]
    for font_name, font_path in font_paths:
        try:
            if Path(font_path).exists():
                pdfmetrics.registerFont(TTFont(font_name, font_path))
        except:
            pass
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
    # Premium color palette (rich, deep colors)
    colors = {
        'vip_leaderboard': HexColor('#D97706'),  # Deep gold
        'payment': HexColor('#0D9488'),          # Deep teal
        'promotion': HexColor('#EA580C'),        # Deep orange
        'other': HexColor('#0284C7'),            # Deep blue
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
    # Multi-layer premium border
    c.rect(8*mm, 8*mm, w-16*mm, h-16*mm, fill=False, stroke=True)  # Outer
    c.rect(10*mm, 10*mm, w-20*mm, h-20*mm, fill=False, stroke=True)  # Main
    c.setLineWidth(1)
    c.setStrokeColor(HexColor('#D4AF37'))  # Gold accent
    c.rect(9*mm, 9*mm, w-18*mm, h-18*mm, fill=False, stroke=True)  # Inner gold
    
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
    
    # Watermark (diagonal UNIYO)
    c.saveState()
    c.translate(w/2, h/2)
    c.rotate(30)
    c.setFillColor(HexColor('#6D28D9'))
    c.setFont('DejaVuSans-Bold', 100)
    c.setFillAlpha(0.04)
    c.drawCentredString(0, 0, 'UNIYO')
    c.restoreState()
    
    # GUILLOCHÉ PATTERN (fine lines around border)
    c.setStrokeColor(HexColor('#6D28D9'))
    c.setLineWidth(0.3)
    c.setStrokeAlpha(0.15)
    for i in range(20):
        offset = i * 0.5*mm
        c.rect(15*mm + offset, 15*mm + offset, w - 30*mm - 2*offset, h - 30*mm - 2*offset, fill=False, stroke=True)
    c.setStrokeAlpha(1)
    
    # HOLOGRAPHIC EFFECT (subtle gradient bars)
    c.setFillAlpha(0.008)
    colors_holographic = ['#6D28D9', '#F59E0B', '#14B8A6', '#EC4899']
    for i, color in enumerate(colors_holographic):
        c.setFillColor(HexColor(color))
        y_start = h/2 - 60*mm + i * 30*mm
        c.rect(20*mm, y_start, w-40*mm, 3*mm, fill=True, stroke=False)
    c.setFillAlpha(1)
    
    # GOLD FOIL (for VIP - subtle gold overlay)
    if cert_type == 'vip_leaderboard':
        c.setFillColor(HexColor('#F59E0B'))
        # Smooth gold gradient overlay
        c.saveState()
        c.setFillAlpha(0.015)
        for i in range(50):
            alpha = 0.015 * (1 - i/50)
            c.setFillAlpha(alpha)
            c.setFillColor(HexColor('#F59E0B'))
            c.rect(0, i*2*mm, w, 2*mm, fill=True, stroke=False)
        c.restoreState()
        c.rect(0, 0, w, h, fill=True, stroke=False)
        c.setFillAlpha(1)
    
    # SPARKLES (for VIP/Promo - tiny dots)
    if cert_type in ['vip_leaderboard', 'promotion']:
        import random as sparkle_random
        sparkle_random.seed(42)
        c.setFillColor(HexColor('#FCD34D'))
        c.setFillAlpha(0.3)
        for _ in range(30):
            sx = sparkle_random.uniform(30*mm, w-30*mm)
            sy = sparkle_random.uniform(60*mm, h-60*mm)
            c.circle(sx, sy, 0.5*mm, fill=True, stroke=False)
        c.setFillAlpha(1)
    
    # ANTI-COPY PATTERN (fine lines - payment only)
    if cert_type == 'payment':
        c.setStrokeColor(HexColor('#14B8A6'))
        c.setLineWidth(0.2)
        c.setStrokeAlpha(0.1)
        for i in range(40):
            y_line = 20*mm + i * 5*mm
            c.line(20*mm, y_line, w-20*mm, y_line)
        c.setStrokeAlpha(1)
    
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
    c.setFont('DejaVuSans-Bold', 26)
    c.drawCentredString(w/2, h-40*mm, title.upper())
    
    # SUBTITLE (at 48mm from top)
    c.setFillColor(HexColor('#64748b'))
    c.setFont('DejaVuSans', 12)
    c.drawCentredString(w/2, h-48*mm, 'Ethiopian Higher Education Freshman Hub')
    
    # DIVIDER LINE (at 54mm from top)
    c.setStrokeColor(primary)
    c.setLineWidth(1.5)
    c.line(30*mm, h-54*mm, w-30*mm, h-54*mm)
    
    # "PRESENTED TO" (at 62mm from top)
    c.setFillColor(HexColor('#64748b'))
    c.setFont('DejaVuSans', 13)
    c.drawCentredString(w/2, h-62*mm, 'This certificate is proudly presented to')
    
    # STUDENT NAME (at 72mm from top)
    c.setFillColor(HexColor('#1e1b4b'))
    c.setFont('DejaVuSans-Bold', 34)
    c.drawCentredString(w/2, h-72*mm, full_name)
    
    # REASON TEXT BOX (at 80mm from top, boxed)
    reason = 'For successfully completing lessons and worksheets with dedication.'
    c.setFillColor(HexColor('#334155'))
    c.setFont('DejaVuSans', 11)
    c.roundRect(35*mm, h-86*mm, w-70*mm, 10*mm, 3*mm, fill=False, stroke=True)
    c.drawCentredString(w/2, h-81*mm, reason)
    
    # UNIVERSITY DETAILS (at 94mm from top)
    c.setFillColor(HexColor('#64748b'))
    c.setFont('DejaVuSans', 11)
    details = university
    if stream:
        details += f' • {stream} Science'
    if sex:
        details += f' • {sex}'
    c.drawCentredString(w/2, h-94*mm, details)
    
    # CREDENTIALS BOX (at 104mm to 130mm from top)
    cred_y = h - 108*mm
    c.roundRect(30*mm, cred_y-20*mm, w-60*mm, 28*mm, 3*mm, fill=False, stroke=True)
    
    c.setFont('DejaVuSans', 10)
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
    c.setFont('DejaVuSans', 9)
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
        c.setFont('DejaVuSans', 8)
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
        c.drawImage(stamp_img, w/2-17*mm, 28*mm, 34*mm, 34*mm, preserveAspectRatio=True, mask='auto', anchor='c')
    
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
        c.drawImage(sig_img, 20*mm, 15*mm, 28*mm, 9*mm, preserveAspectRatio=True, mask='auto')
        c.setFont('DejaVuSans-Bold', 8)
        c.setFillColor(HexColor('#1e1b4b'))
        c.drawCentredString(34*mm, 13*mm, 'Chalachew Agegn')
        c.setFont('DejaVuSans', 7)
        c.setFillColor(HexColor('#64748b'))
        c.drawCentredString(34*mm, 11*mm, 'Super Admin')
    
    # CONTENT MANAGER SIGNATURE (bottom right, at 15mm from bottom)
    if cert_type not in ['other', 'excellence', 'content_creator', 'marketing_manager', 'advertiser', 'staff', 'special_congratulations', 'participation', 'appreciation', 'congratulations']:
        cm_sig = auth_dir / 'signature_(content_manager).png'
        if cm_sig.exists():
            cm_img = ImageReader(str(cm_sig))
            # CM at: right 25mm, bottom 12mm
            c.drawImage(cm_img, w-48*mm, 15*mm, 28*mm, 9*mm, preserveAspectRatio=True, mask='auto')
            c.setFont('DejaVuSans-Bold', 8)
            c.setFillColor(HexColor('#1e1b4b'))
            c.drawCentredString(w-34*mm, 13*mm, 'Banch Destaw')
            c.setFont('DejaVuSans', 7)
            c.setFillColor(HexColor('#64748b'))
            c.drawCentredString(w-34*mm, 11*mm, 'Content Manager')
    
    # BARCODE (bottom center, at 15mm from bottom)
    c.setLineWidth(1)
    c.setStrokeColor(HexColor('#000000'))
    barcode_x = w/2 + 10*mm
    barcode_y = 15*mm
    import random
    random.seed(cert_number)
    for i in range(30):
        bar_width = random.choice([1, 2]) * 0.4*mm
        c.line(barcode_x, barcode_y, barcode_x, barcode_y + 12*mm)
        barcode_x += bar_width + 0.3*mm
    c.setFont('Courier', 6)
    c.setFillColor(HexColor('#334155'))
    c.drawCentredString(w/2 + 20*mm, 12*mm, cert_number[:25])
    
    # MICROTEXT (very bottom, at 3mm from bottom)
    c.setFillColor(HexColor('#94a3b8'))
    c.setFont('DejaVuSans', 5)
    c.drawCentredString(w/2, 8*mm, 'UNIYO AUTHENTIC CERTIFICATE • VERIFY ONLINE • SECURITY FEATURES INCLUDED')
    
    # PDF METADATA (Professional)
    c.setTitle(f"UNIYO Certificate - {full_name}")
    c.setAuthor("UNIYO - University Made for YOU")
    c.setSubject(f"{title} - {cert_type.upper()}")
    c.setKeywords(["UNIYO", "Certificate", cert_type, full_name])
    
    # EXCLUSIVE QUALITY SETTINGS
    c.setPageCompression(1)  # Best compression
    c.setPageRotation(0)  # Correct orientation
    
    c.save()


    
    # Convert PDF to PNG (requires pdf2image on Render)
    return output_pdf
