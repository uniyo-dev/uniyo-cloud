"""
UNIYO LMS - Course Completion Certificate (A4 Landscape)
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

def generate_completion_certificate(certificate_data, qr_data_uri=None):
    full_name = certificate_data.get('full_name', 'Student Name')
    university = certificate_data.get('university', 'University')
    stream = certificate_data.get('stream', '')
    sex = certificate_data.get('sex', '')
    cert_number = certificate_data.get('certificate_number', 'UNIYO-COMP-001')
    verification_token = certificate_data.get('verification_token', '')
    issue_date = certificate_data.get('issue_date', datetime.now().strftime('%B %d, %Y'))
    title = certificate_data.get('title', 'Certificate of Completion')
    reason = certificate_data.get('reason', 'For successfully completing all lessons and worksheets.')
    
    cert_id = cert_number.replace('/', '_').replace('\\', '_')
    output_pdf = CERTIFICATES_DIR / f"{cert_id}.pdf"
    
    c = canvas.Canvas(str(output_pdf), pagesize=landscape(A4), pageCompression=0)
    w, h = landscape(A4)
    
    gold_light = HexColor('#D4AF37')
    gold_mid = HexColor('#C5A059')
    gold_dark = HexColor('#9A7C36')
    text_dark = HexColor('#1A1A1A')
    text_mid = HexColor('#3A3A3A')
    text_muted = HexColor('#555B62')
    
    # Background
    c.setFillColor(HexColor('#FDFBF7'))
    c.rect(0, 0, w, h, fill=True, stroke=False)
    
    # Watermark (from organized assets)
    c.saveState()
    c.translate(w/2, h/2)
    c.rotate(35)
    c.setFillColor(HexColor('#4B0082'))
    c.setFillAlpha(0.04)
    c.setFont('Cinzel' if 'Cinzel' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold', 60)
    c.drawCentredString(0, 0, 'UNIYO')
    c.restoreState()
    
    # Border
    borders_dir = BASE_DIR / 'static' / 'Certificates' / 'completion'
    ornate_border = borders_dir / 'divider_floral_flourish.png'
    if ornate_border.exists():
        c.drawImage(ImageReader(str(ornate_border)), 15*mm, 13*mm, w-30*mm, h-26*mm, preserveAspectRatio=False, mask='auto')
    
    # Inner Indigo border
    c.setStrokeColor(HexColor('#4B0082'))
    c.setLineWidth(2)
    c.rect(25*mm, 22*mm, w-50*mm, h-44*mm, fill=False, stroke=True)
    
    # Logo
    logo_file = BASE_DIR / 'static' / 'icons' / 'app_icon-192.png'
    if logo_file.exists():
        c.drawImage(ImageReader(str(logo_file)), w/2-10*mm, h-30*mm, 20*mm, 20*mm, preserveAspectRatio=True, mask='auto')
    
    # Title
    c.setFillColor(text_dark)
    c.setFont('Cinzel' if 'Cinzel' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold', 28)
    c.drawCentredString(w/2, h-42*mm, 'CERTIFICATE')
    
    c.setFont('Playfair' if 'Playfair' in pdfmetrics.getRegisteredFontNames() else 'Helvetica', 15)
    c.setFillColor(text_muted)
    c.drawCentredString(w/2, h-50*mm, 'of ' + title)
    
    # Divider - Chinese cloud
    divider_file = BASE_DIR / 'static' / 'Certificates' / 'completion' / 'divider_floral_flourish.png'
    if divider_file.exists():
        c.drawImage(ImageReader(str(divider_file)), w/2-40*mm, h-58*mm, 80*mm, 10*mm, preserveAspectRatio=True, mask='auto')
    
    # Presented to
    c.setFont('Montserrat' if 'Montserrat' in pdfmetrics.getRegisteredFontNames() else 'Helvetica', 10)
    c.setFillColor(text_mid)
    c.drawCentredString(w/2, h-70*mm, 'THIS CERTIFICATE IS PROUDLY PRESENTED TO')
    
    # Student name
    c.setFont('AlexBrush' if 'AlexBrush' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold', 36)
    c.setFillColor(text_dark)
    c.drawCentredString(w/2, h-84*mm, full_name)
    
    c.setStrokeColor(gold_mid)
    c.setLineWidth(0.8)
    c.line(w/2-50*mm, h-88*mm, w/2+50*mm, h-88*mm)
    
    # Reason
    c.setFont('Montserrat' if 'Montserrat' in pdfmetrics.getRegisteredFontNames() else 'Helvetica', 9)
    c.setFillColor(text_mid)
    words = reason.split()
    lines = []
    current = []
    current_w = 0
    max_w = 110*mm
    for word in words:
        ww = len(word) * 2*mm
        if current_w + ww < max_w:
            current.append(word)
            current_w += ww + 2*mm
        else:
            lines.append(' '.join(current))
            current = [word]
            current_w = ww
    if current:
        lines.append(' '.join(current))
    
    y_reason = h - 97*mm
    for line in lines[:2]:
        c.drawCentredString(w/2, y_reason, line)
        y_reason -= 6*mm
    
    # University details
    details = university
    if stream:
        details += f' • {stream} Science'
    if sex:
        details += f' • {sex}'
    c.setFont('Montserrat' if 'Montserrat' in pdfmetrics.getRegisteredFontNames() else 'Helvetica', 8)
    c.setFillColor(HexColor('#667788'))
    c.drawCentredString(w/2, y_reason - 3*mm, details)
    
    # Credentials
    y_cred = y_reason - 12*mm
    c.setFont('Courier', 7)
    c.setFillColor(text_mid)
    c.drawCentredString(w/2, y_cred, f'Certificate No: {cert_number}')
    y_cred -= 5*mm
    c.drawCentredString(w/2, y_cred, f'Date: {issue_date[:20]}')
    y_cred -= 5*mm
    c.drawCentredString(w/2, y_cred, f'Type: {certificate_data.get("certificate_type", "completion").upper()}')
    
    # Verify URL
    verify_url = f"https://uniyo-cloud.onrender.com/verify/{verification_token}"
    c.setFont('Helvetica', 6)
    c.setFillColor(HexColor('#4B0082'))
    c.drawRightString(w-30*mm, h-33*mm, f'Verify: {verify_url[:45]}')
    
    # Footer
    footer_y = 28*mm
    
    # Barcode
    c.setFillColor(HexColor('#000000'))
    random.seed(cert_number)
    bar_x = 55*mm
    bar_y = footer_y + 5*mm
    for i in range(30):
        bar_w = random.choice([1, 2]) * 0.4*mm
        c.rect(bar_x, bar_y, bar_w, 10*mm, fill=True, stroke=False)
        bar_x += bar_w + 0.3*mm
    c.setFont('Courier', 5)
    c.setFillColor(HexColor('#333333'))
    c.drawCentredString(70*mm, footer_y + 2*mm, cert_number[:20])
    
    # QR code
    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
        qr.add_data(verify_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color='black', back_color='white')
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        c.drawImage(ImageReader(qr_buffer), 30*mm, footer_y, 20*mm, 20*mm, preserveAspectRatio=True)
    except:
        pass
    
    # Stamp
    stamp_file = BASE_DIR / 'static' / 'certificates' / 'completion' / 'stamp.png'
    if stamp_file.exists():
        c.drawImage(ImageReader(str(stamp_file)), w/2-27*mm, 28*mm, 54*mm, 54*mm, preserveAspectRatio=True, mask='auto')
    
    # Replica stamp
    c.saveState()
    c.setFillAlpha(0.08)
    c.drawImage(ImageReader(str(stamp_file)), 50*mm, h/2-50*mm, 100*mm, 100*mm, preserveAspectRatio=True, mask='auto')
    c.restoreState()
    
    # Signature
    sig_file = BASE_DIR / 'static' / 'Authenticity' / 'admin_signature.png'
    if sig_file.exists():
        c.drawImage(ImageReader(str(sig_file)), w-60*mm, footer_y+8*mm, 25*mm, 8*mm, preserveAspectRatio=True, mask='auto')
    c.setFont('AlexBrush' if 'AlexBrush' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold', 14)
    c.setFillColor(text_dark)
    c.drawCentredString(w-47*mm, footer_y+5*mm, 'Chalachew Agegn')
    c.setFont('Montserrat' if 'Montserrat' in pdfmetrics.getRegisteredFontNames() else 'Helvetica', 6)
    c.drawCentredString(w-47*mm, footer_y+2*mm, 'SUPER ADMIN')
    
    # Microtext
    c.setFont('Helvetica', 5)
    c.setFillColor(HexColor('#999999'))
    c.drawCentredString(w/2, 8*mm, 'UNIYO AUTHENTIC CERTIFICATE • VERIFY ONLINE • SECURITY FEATURES INCLUDED • DO NOT COPY • UNIYO AUTHENTIC CERTIFICATE')
    
    c.setTitle(f"UNIYO Certificate - {full_name}")
    c.setAuthor("UNIYO - University Made for YOU")
    c.setSubject(title)
    
    c.save()
    return output_pdf
