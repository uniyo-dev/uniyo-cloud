"""
UNIYO LMS - Appreciation & Staff Certificates (A4 Landscape)
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

def generate_appreciation_certificate(certificate_data, qr_data_uri=None):
    full_name = certificate_data.get('full_name', 'Student Name')
    university = certificate_data.get('university', 'University')
    stream = certificate_data.get('stream', '')
    sex = certificate_data.get('sex', '')
    cert_number = certificate_data.get('certificate_number', 'UNIYO-APPR-001')
    verification_token = certificate_data.get('verification_token', '')
    issue_date = certificate_data.get('issue_date', datetime.now().strftime('%B %d, %Y'))
    title = certificate_data.get('title', 'Certificate of Appreciation')
    cert_type = certificate_data.get('certificate_type', 'appreciation')
    
    if cert_type == 'staff':
        title = 'Staff Appreciation Certificate'
        reason = 'In recognition of outstanding service and dedication to the UNIYO learning platform.'
        stamp = 'super_admin_stamp.png'
    else:
        title = 'Certificate of Appreciation'
        reason = 'In recognition of outstanding contribution and dedication to the UNIYO learning community.'
        stamp = 'super_admin_stamp.png'
    
    cert_id = cert_number.replace('/', '_').replace('\\', '_')
    output_pdf = CERTIFICATES_DIR / f"{cert_id}.pdf"
    
    c = canvas.Canvas(str(output_pdf), pagesize=landscape(A4), pageCompression=0)
    w, h = landscape(A4)
    
    # Colors
    gold = HexColor('#C5A059')
    text_dark = HexColor('#1A1A1A')
    text_mid = HexColor('#3A3A3A')
    
    # Background
    c.setFillColor(HexColor('#FDFBF7'))
    c.rect(0, 0, w, h, fill=True, stroke=False)
    
    # WATERMARK
    c.saveState()
    c.translate(w/2, h/2)
    c.rotate(35)
    c.setFillColor(HexColor('#4B0082'))
    c.setFillAlpha(0.04)
    c.setFont('Helvetica-Bold', 50)
    c.drawCentredString(0, 0, 'UNIYO')
    c.restoreState()
    
    # Watermark
    
    
    # Border
    border_file = BASE_DIR / 'static' / 'Certificates' / 'other' / 'png_converted' / 'option53_gold_single_line.png'
    if border_file.exists():
        c.drawImage(ImageReader(str(border_file)), 8*mm, 8*mm, w-16*mm, h-16*mm, preserveAspectRatio=True, mask='auto')
    
    # Inner border
    c.setStrokeColor(gold)
    c.setLineWidth(1.5)
    c.rect(12*mm, 12*mm, w-24*mm, h-24*mm, fill=False, stroke=True)
    
    # Logo
    logo_file = BASE_DIR / 'static' / 'icons' / 'app_icon-192.png'
    if logo_file.exists():
        c.drawImage(ImageReader(str(logo_file)), w/2-9*mm, h-30*mm, 18*mm, 18*mm, preserveAspectRatio=True, mask='auto')
    
    # Title
    c.setFillColor(text_dark)
    c.setFont('Cinzel' if 'Cinzel' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold', 28)
    c.drawCentredString(w/2, h-42*mm, title.upper())
    
    # Divider
    divider_file = BASE_DIR / 'static' / 'Certificates' / 'ribbons' / 'ribbon_gold.png'
    if divider_file.exists():
        c.drawImage(ImageReader(str(divider_file)), w/2-30*mm, h-52*mm, 60*mm, 7*mm, preserveAspectRatio=True, mask='auto')
    
    # Presented to
    c.setFont('Helvetica', 10)
    c.setFillColor(text_mid)
    c.drawCentredString(w/2, h-65*mm, 'THIS CERTIFICATE IS PROUDLY PRESENTED TO')
    
    # Name
    c.setFont('AlexBrush' if 'AlexBrush' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold', 36)
    c.setFillColor(text_dark)
    c.drawCentredString(w/2, h-75*mm, full_name)
    
    # Reason
    c.setFont('Helvetica', 9)
    c.setFillColor(text_mid)
    c.drawCentredString(w/2, h-85*mm, reason)
    
    # Details
    details = university
    if stream:
        details += f' • {stream} Science'
    if sex:
        details += f' • {sex}'
    c.setFont('Helvetica', 8)
    c.setFillColor(HexColor('#667788'))
    c.drawCentredString(w/2, h-92*mm, details)
    
    # Credentials
    c.setFont('Courier', 7)
    c.setFillColor(text_mid)
    c.drawCentredString(w/2, h-100*mm, f'Certificate No: {cert_number}')
    c.drawCentredString(w/2, h-105*mm, f'Date: {issue_date[:20]}')
    
    # Verify URL
    verify_url = f"https://uniyo-cloud.onrender.com/verify/{verification_token}"
    c.setFont('Helvetica', 6)
    c.setFillColor(HexColor('#4B0082'))
    c.drawRightString(w-28*mm, h-35*mm, f'Verify: {verify_url[:45]}')
    
    # BARCODE
    c.setFillColor(HexColor('#000000'))
    import random as barcode_random
    barcode_random.seed(cert_number)
    bar_x = 55*mm
    bar_y = 16*mm
    for i in range(25):
        bar_w = barcode_random.choice([1, 2]) * 0.35*mm
        c.rect(bar_x, bar_y, bar_w, 8*mm, fill=True, stroke=False)
        bar_x += bar_w + 0.25*mm
    c.setFont('Courier', 4)
    c.setFillColor(HexColor('#333333'))
    c.drawCentredString(70*mm, 14*mm, cert_number[:15])
    
    # QR
    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
        qr.add_data(verify_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color='black', back_color='white')
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        c.drawImage(ImageReader(qr_buffer), 28*mm, 15*mm, 16*mm, 16*mm, preserveAspectRatio=True)
    except:
        pass
    
    # Stamp
    stamp_file = BASE_DIR / 'static' / 'Authenticity' / stamp
    if stamp_file.exists():
        c.drawImage(ImageReader(str(stamp_file)), w/2-25*mm, 18*mm, 50*mm, 50*mm, preserveAspectRatio=True, mask='auto')
    
    # Signature
    sig_file = BASE_DIR / 'static' / 'Authenticity' / 'super_admin_signature.png'
    if sig_file.exists():
        c.drawImage(ImageReader(str(sig_file)), w-52*mm, 15*mm, 22*mm, 7*mm, preserveAspectRatio=True, mask='auto')
    c.setFont('Helvetica-Bold', 6)
    c.setFillColor(text_dark)
    c.drawCentredString(w-47*mm, 16*mm, 'Chalachew Agegn')
    
    # Microtext
    c.setFont('Helvetica', 5)
    c.setFillColor(HexColor('#999999'))
    c.drawCentredString(w/2, 13*mm, 'UNIYO AUTHENTIC CERTIFICATE • VERIFY ONLINE • SECURITY FEATURES INCLUDED')
    
    # MICROTEXT
        
    c.save()
    return output_pdf
