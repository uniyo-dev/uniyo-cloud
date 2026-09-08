"""
UNIYO LMS - Custom Certificate Generator (A4 Landscape)
Handles ALL custom certificate types:
- Appreciation, Staff
- Congratulations, Special Congratulations  
- Participation, Excellence, Advertiser
- Content Creator, Marketing Manager
- Any other custom type with custom title/reason

Admin can issue with:
- Custom Title
- Custom Reason text
- Student Name
- Any other custom fields
"""

from pathlib import Path
from io import BytesIO
from datetime import datetime
import qrcode
import random
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from core.paths import CERTIFICATES_DIR, BASE_DIR

FONTS_DIR = BASE_DIR / 'assets' / 'fonts'
if FONTS_DIR.exists():
    try:
        pdfmetrics.registerFont(TTFont('AlexBrush', str(FONTS_DIR / 'AlexBrush-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('Cinzel', str(FONTS_DIR / 'Cinzel-Bold.ttf')))
        pdfmetrics.registerFont(TTFont('Montserrat', str(FONTS_DIR / 'Montserrat-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('Playfair', str(FONTS_DIR / 'PlayfairDisplay-Bold.ttf')))
    except:
        pass

def generate_custom_certificate(certificate_data, qr_data_uri=None):
    """
    Generate CUSTOM certificate for any type
    Admin provides: title, reason, student info
    """
    full_name = certificate_data.get('full_name', 'Student Name')
    university = certificate_data.get('university', 'University')
    stream = certificate_data.get('stream', '')
    sex = certificate_data.get('sex', '')
    cert_number = certificate_data.get('certificate_number', 'UNIYO-CUSTOM-001')
    verification_token = certificate_data.get('verification_token', '')
    issue_date = certificate_data.get('issue_date', datetime.now().strftime('%B %d, %Y'))
    
    # CUSTOM FIELDS (admin provides these)
    title = certificate_data.get('title', 'Certificate of Recognition')
    reason = certificate_data.get('reason', 'In recognition of your achievement.')
    cert_type = certificate_data.get('certificate_type', 'other')
    
    cert_id = cert_number.replace('/', '_').replace('\\', '_')
    output_pdf = CERTIFICATES_DIR / f"{cert_id}.pdf"
    
    c = canvas.Canvas(str(output_pdf), pagesize=landscape(A4), pageCompression=0)
    w, h = landscape(A4)
    
    # Colors
    gold = HexColor('#C5A059')
    text_dark = HexColor('#1A1A1A')
    text_mid = HexColor('#3A3A3A')
    text_muted = HexColor('#555B62')
    
    # Background
    c.setFillColor(HexColor('#FFFFFF'))
    c.rect(0, 0, w, h, fill=True, stroke=False)
    
    # Watermark
    c.saveState()
    c.translate(w/2, h/2)
    c.rotate(35)
    c.setFillColor(HexColor('#4B0082'))
    c.setFillAlpha(0.04)
    c.setFont('Helvetica-Bold', 50)
    c.drawCentredString(0, 0, 'UNIYO')
    c.restoreState()
    
    # Border - use theme_nature_organic
    border_file = BASE_DIR / 'static' / 'Certificates' / 'other' / 'png_converted' / 'theme_nature_organic.png'
    if border_file.exists():
        c.drawImage(ImageReader(str(border_file)), 0, 0, w, h, preserveAspectRatio=True, mask='auto')
    
    # Inner frame
    c.setStrokeColor(gold)
    c.setLineWidth(1.2)
    c.rect(12*mm, 12*mm, w-24*mm, h-24*mm, fill=False, stroke=True)
    
    # Logo
    logo_file = BASE_DIR / 'static' / 'icons' / 'uniyo_branding_logo.png'
    if logo_file.exists():
        c.drawImage(ImageReader(str(logo_file)), w/2-8*mm, h-30*mm, 16*mm, 16*mm, preserveAspectRatio=True, mask='auto')
    
    # CUSTOM TITLE (admin-provided)
    c.setFillColor(text_dark)
    c.setFont('Cinzel' if 'Cinzel' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold', 24)
    c.drawCentredString(w/2, h-42*mm, title.upper())
    
    # Divider
    c.setStrokeColor(gold)
    c.setLineWidth(0.8)
    c.line(w/2-30*mm, h-48*mm, w/2+30*mm, h-48*mm)
    
    # Presented to
    c.setFont('Helvetica', 10)
    c.setFillColor(text_mid)
    c.drawCentredString(w/2, h-58*mm, 'THIS CERTIFICATE IS PROUDLY PRESENTED TO')
    
    # Student Name
    c.setFont('AlexBrush' if 'AlexBrush' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold', 32)
    c.setFillColor(text_dark)
    c.drawCentredString(w/2, h-72*mm, full_name)
    
    c.setStrokeColor(gold)
    c.setLineWidth(0.5)
    c.line(w/2-40*mm, h-76*mm, w/2+40*mm, h-76*mm)
    
    # CUSTOM REASON (admin-provided)
    c.setFont('Helvetica', 9)
    c.setFillColor(text_mid)
    words = reason.split()
    lines = []
    current = []
    for word in words:
        current.append(word)
        if len(' '.join(current)) > 40:
            lines.append(' '.join(current[:-1]))
            current = [word]
    if current:
        lines.append(' '.join(current))
    
    y = h-84*mm
    for line in lines[:2]:
        c.drawCentredString(w/2, y, line)
        y -= 6*mm
    
    # University details
    details = university
    if stream:
        details += f' • {stream} Science'
    if sex:
        details += f' • {sex}'
    c.setFont('Helvetica', 8)
    c.setFillColor(text_muted)
    c.drawCentredString(w/2, y-2*mm, details)
    
    # Credentials
    y_cred = y - 10*mm
    c.setFont('Courier', 7)
    c.setFillColor(text_mid)
    c.drawCentredString(w/2, y_cred, f'Certificate No: {cert_number}')
    y_cred -= 5*mm
    c.drawCentredString(w/2, y_cred, f'Date: {issue_date[:20]}')
    y_cred -= 5*mm
    c.drawCentredString(w/2, y_cred, f'Type: {cert_type.upper()}')
    
    # Verify URL
    verify_url = f"https://uniyo-cloud.onrender.com/verify/{verification_token}"
    c.setFont('Helvetica', 6)
    c.setFillColor(HexColor('#4B0082'))
    c.drawRightString(w-25*mm, h-35*mm, f'Verify: {verify_url[:40]}')
    
    # QR Code
    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
        qr.add_data(verify_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color='black', back_color='white')
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        c.drawImage(ImageReader(qr_buffer), 18*mm, 15*mm, 14*mm, 14*mm, preserveAspectRatio=True)
    except:
        pass
    
    # Barcode
    c.setFillColor(HexColor('#000000'))
    random.seed(cert_number)
    bar_x = 38*mm
    bar_y = 16*mm
    for i in range(25):
        bar_w = random.choice([1, 2]) * 0.35*mm
        c.rect(bar_x, bar_y, bar_w, 8*mm, fill=True, stroke=False)
        bar_x += bar_w + 0.25*mm
    c.setFont('Courier', 4)
    c.setFillColor(text_mid)
    c.drawCentredString(55*mm, 14*mm, cert_number[:15])
    
    # Stamp (super_admin for custom)
    stamp_file = BASE_DIR / 'static' / 'Authenticity' / 'super_admin_stamp.png'
    if stamp_file.exists():
        c.drawImage(ImageReader(str(stamp_file)), w/2-22*mm, 18*mm, 44*mm, 44*mm, preserveAspectRatio=True, mask='auto')
    
    # Signature (Super Admin only for custom)
    sig_file = BASE_DIR / 'static' / 'Authenticity' / 'super_admin_signature.png'
    if sig_file.exists():
        c.drawImage(ImageReader(str(sig_file)), w-52*mm, 15*mm, 22*mm, 7*mm, preserveAspectRatio=True, mask='auto')
    c.setFont('Helvetica-Bold', 6)
    c.setFillColor(text_dark)
    c.drawCentredString(w-40*mm, 13*mm, 'Chalachew Agegn')
    
    # Microtext
    c.setFont('Helvetica', 4.5)
    c.setFillColor(HexColor('#999999'))
    c.drawCentredString(w/2, 5*mm, 'UNIYO AUTHENTIC CERTIFICATE • VERIFY ONLINE • SECURITY FEATURES INCLUDED')
    
    c.setTitle(f"UNIYO Certificate - {full_name}")
    c.setAuthor("UNIYO - University Made for YOU")
    c.setSubject(title)
    
    c.save()
    return output_pdf
