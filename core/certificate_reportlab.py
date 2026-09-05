"""
UNIYO LMS - EXCLUSIVE PERFECT PDF Certificate Generator
Professional printing quality using ReportLab
Exact A4: 210mm x 297mm
"""

from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from core.paths import CERTIFICATES_DIR, BASE_DIR

def generate_certificate_reportlab(certificate_data, qr_data_uri):
    """Generate PERFECT A4 PDF certificate"""
    
    cert_type = certificate_data.get('certificate_type', 'completion')
    full_name = certificate_data.get('full_name', 'Student')
    university = certificate_data.get('university', '')
    stream = certificate_data.get('stream', '')
    sex = certificate_data.get('sex', '')
    cert_number = certificate_data.get('certificate_number', 'UNKNOWN')
    title = certificate_data.get('title', 'Certificate')
    issue_date = certificate_data.get('issue_date', '')
    rank = certificate_data.get('rank')
    verification_token = certificate_data.get('verification_token', '')
    
    cert_id = cert_number.replace('/', '_').replace('\\', '_')
    output_pdf = CERTIFICATES_DIR / f"{cert_id}.pdf"
    
    # ============================================
    # REGISTER HIGH-QUALITY FONTS
    # ============================================
    font_dir = Path('/usr/share/fonts/truetype/dejavu')
    if font_dir.exists():
        try:
            pdfmetrics.registerFont(TTFont('UniyoSans', str(font_dir / 'DejaVuSans.ttf')))
            pdfmetrics.registerFont(TTFont('UniyoSans-Bold', str(font_dir / 'DejaVuSans-Bold.ttf')))
        except:
            pass
    
    # ============================================
    # PAGE SETUP - EXACT A4 PORTRAIT (210 x 297 mm)
    # ============================================
    c = canvas.Canvas(
        str(output_pdf),
        pagesize=A4,  # 210mm x 297mm
        pageCompression=0,  # No compression = best quality
        invariant=1
    )
    
    w, h = A4  # w=210mm, h=297mm
    
    # ============================================
    # COLORS - PROFESSIONAL PALETTE
    # ============================================
    colors = {
        'vip_leaderboard': HexColor('#B8860B'),  # Dark goldenrod
        'payment': HexColor('#008080'),           # Teal
        'promotion': HexColor('#D2691E'),         # Chocolate
        'other': HexColor('#4682B4'),             # Steel blue
    }
    primary = colors.get(cert_type, HexColor('#4B0082'))  # Indigo default
    
    # ============================================
    # BACKGROUND - CLEAN WHITE
    # ============================================
    c.setFillColor(HexColor('#FFFFFF'))
    c.rect(0, 0, w, h, fill=True, stroke=False)
    
    # ============================================
    # EXACT BORDERS (within 15mm printable margins)
    # ============================================
    # Outer border: 15mm from edges
    c.setStrokeColor(primary)
    c.setLineWidth(3)
    c.rect(15*mm, 15*mm, w-30*mm, h-30*mm, fill=False, stroke=True)
    
    # Inner gold border: 18mm from edges
    c.setStrokeColor(HexColor('#DAA520'))
    c.setLineWidth(1.5)
    c.rect(18*mm, 18*mm, w-36*mm, h-36*mm, fill=False, stroke=True)
    
    # ============================================
    # CORNER ORNAMENTS (within margins)
    # ============================================
    c.setStrokeColor(primary)
    c.setLineWidth(5)
    corner_len = 20*mm
    # Top-left
    c.line(15*mm, 15*mm+corner_len, 15*mm, 15*mm)
    c.line(15*mm, 15*mm, 15*mm+corner_len, 15*mm)
    # Top-right
    c.line(w-15*mm, 15*mm+corner_len, w-15*mm, 15*mm)
    c.line(w-15*mm, 15*mm, w-15*mm-corner_len, 15*mm)
    # Bottom-left
    c.line(15*mm, h-15*mm-corner_len, 15*mm, h-15*mm)
    c.line(15*mm, h-15*mm, 15*mm+corner_len, h-15*mm)
    # Bottom-right
    c.line(w-15*mm, h-15*mm-corner_len, w-15*mm, h-15*mm)
    c.line(w-15*mm, h-15*mm, w-15*mm-corner_len, h-15*mm)
    
    # ============================================
    # WATERMARK - SUBTLE DIAGONAL UNIYO
    # ============================================
    c.saveState()
    c.translate(w/2, h/2)
    c.rotate(30)
    c.setFillColor(primary)
    c.setFont('UniyoSans-Bold' if 'UniyoSans-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold', 80)
    c.setFillAlpha(0.04)
    c.drawCentredString(0, 0, 'UNIYO')
    c.restoreState()
    
    # ============================================
    # GUILLOCHÉ PATTERN - FINE SECURITY LINES
    # ============================================
    c.setStrokeColor(primary)
    c.setStrokeAlpha(0.06)
    c.setLineWidth(0.3)
    for i in range(15):
        offset = i * 1.5*mm
        c.rect(20*mm + offset, 20*mm + offset, w-40*mm-2*offset, h-40*mm-2*offset, fill=False, stroke=True)
    c.setStrokeAlpha(1)
    
    # ============================================
    # LOGO (top center)
    # ============================================
    logo_file = BASE_DIR / 'static' / 'icons' / 'app_icon-192.png'
    if logo_file.exists():
        logo_img = ImageReader(str(logo_file))
        c.drawImage(logo_img, w/2-8*mm, h-23*mm, 16*mm, 16*mm, preserveAspectRatio=True, mask='auto')
    
    # ============================================
    # TITLE (centered, 28mm from top)
    # ============================================
    c.setFillColor(primary)
    c.setFont('UniyoSans-Bold' if 'UniyoSans-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold', 24)
    c.drawCentredString(w/2, h-32*mm, title.upper())
    
    # SUBTITLE
    c.setFillColor(HexColor('#666666'))
    c.setFont('Helvetica', 11)
    c.drawCentredString(w/2, h-39*mm, 'Ethiopian Higher Education Freshman Hub')
    
    # ============================================
    # PRESENTED TO
    # ============================================
    c.setFillColor(HexColor('#666666'))
    c.setFont('Helvetica', 13)
    c.drawCentredString(w/2, h-52*mm, 'This certificate is proudly presented to')
    
    # STUDENT NAME
    c.setFillColor(HexColor('#1a1a2e'))
    c.setFont('UniyoSans-Bold' if 'UniyoSans-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold', 32)
    c.drawCentredString(w/2, h-62*mm, full_name)
    
    # ============================================
    # REASON TEXT
    # ============================================
    reason = 'For successfully completing lessons and worksheets with dedication.'
    c.setFillColor(HexColor('#444444'))
    c.setFont('Helvetica', 11)
    c.drawCentredString(w/2, h-72*mm, reason)
    
    # UNIVERSITY DETAILS
    c.setFillColor(HexColor('#666666'))
    c.setFont('Helvetica', 10)
    details = university
    if stream:
        details += f' • {stream} Science'
    if sex:
        details += f' • {sex}'
    c.drawCentredString(w/2, h-79*mm, details)
    
    # ============================================
    # CREDENTIALS (boxed, centered)
    # ============================================
    cred_top = h - 87*mm
    c.setStrokeColor(primary)
    c.setLineWidth(1)
    c.roundRect(35*mm, cred_top-22*mm, w-70*mm, 28*mm, 2*mm, fill=False, stroke=True)
    
    y = cred_top - 6*mm
    c.setFont('Helvetica', 9)
    c.setFillColor(HexColor('#444444'))
    c.drawString(42*mm, y, 'Certificate Number:')
    c.setFillColor(HexColor('#1a1a2e'))
    c.drawRightString(w-42*mm, y, cert_number)
    
    y -= 7*mm
    c.setFillColor(HexColor('#444444'))
    c.drawString(42*mm, y, 'Issue Date:')
    c.setFillColor(HexColor('#1a1a2e'))
    c.drawRightString(w-42*mm, y, issue_date[:10])
    
    y -= 7*mm
    c.setFillColor(HexColor('#444444'))
    c.drawString(42*mm, y, 'Type:')
    c.setFillColor(primary)
    c.drawRightString(w-42*mm, y, cert_type.upper())
    
    # ============================================
    # VERIFY URL
    # ============================================
    verify_url = f"https://uniyo-cloud.onrender.com/verify/{verification_token}"
    c.setFillColor(primary)
    c.setFont('Helvetica', 8)
    c.drawCentredString(w/2, h-114*mm, f'Verify at: {verify_url}')
    
    # ============================================
    # QR CODE (bottom left)
    # ============================================
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
        c.drawImage(qr_image, 20*mm, 20*mm, 25*mm, 25*mm, preserveAspectRatio=True)
        c.setFont('Helvetica', 7)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(32*mm, 18*mm, 'Scan')
    except:
        pass
    
    # ============================================
    # PRIMARY STAMP (bottom center)
    # ============================================
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
        c.drawImage(stamp_img, w/2-16*mm, 22*mm, 32*mm, 32*mm, preserveAspectRatio=True, mask='auto')
    
    # ============================================
    # SIGNATURES (bottom)
    # ============================================
    sig_file = auth_dir / 'super_admin_signature.png'
    if sig_file.exists():
        sig_img = ImageReader(str(sig_file))
        c.drawImage(sig_img, 20*mm, 12*mm, 28*mm, 8*mm, preserveAspectRatio=True, mask='auto')
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(HexColor('#1a1a2e'))
        c.drawCentredString(34*mm, 10*mm, 'Chalachew Agegn')
        c.setFont('Helvetica', 7)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(34*mm, 8*mm, 'Super Admin')
    
    if cert_type not in ['other', 'excellence', 'content_creator', 'marketing_manager', 'advertiser', 'staff', 'special_congratulations', 'participation', 'appreciation', 'congratulations']:
        cm_sig = auth_dir / 'signature_(content_manager).png'
        if cm_sig.exists():
            cm_img = ImageReader(str(cm_sig))
            c.drawImage(cm_img, w-48*mm, 12*mm, 28*mm, 8*mm, preserveAspectRatio=True, mask='auto')
            c.setFont('Helvetica-Bold', 8)
            c.setFillColor(HexColor('#1a1a2e'))
            c.drawCentredString(w-34*mm, 10*mm, 'Banch Destaw')
            c.setFont('Helvetica', 7)
            c.setFillColor(HexColor('#666666'))
            c.drawCentredString(w-34*mm, 8*mm, 'Content Manager')
    
    # ============================================
    # MICROTEXT (bottom, within margins)
    # ============================================
    c.setFillColor(HexColor('#999999'))
    c.setFont('Helvetica', 6)
    c.drawCentredString(w/2, 6*mm, 'UNIYO AUTHENTIC CERTIFICATE • VERIFY ONLINE • SECURITY FEATURES INCLUDED')
    
    # ============================================
    # PDF METADATA
    # ============================================
    c.setTitle(f"UNIYO Certificate - {full_name}")
    c.setAuthor("UNIYO - University Made for YOU")
    c.setSubject(f"{title} - {cert_type.upper()}")
    
    c.save()
    
    return output_pdf
