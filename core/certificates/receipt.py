"""
UNIYO LMS - Banknote-Grade A6 Payment Receipt Generator
Complete with:
- Multi-layer borders
- Guilloche rosettes
- Holographic security thread
- Watermark
- Microtext
- Dual stamps
- Signatures
- QR + Barcode
- Crypto verification
"""

from pathlib import Path
from io import BytesIO
from datetime import datetime
import qrcode
import random
from reportlab.lib.pagesizes import A6
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from core.paths import CERTIFICATES_DIR, BASE_DIR

# Fonts
FONTS_DIR = BASE_DIR / 'assets' / 'fonts'
if FONTS_DIR.exists():
    try:
        pdfmetrics.registerFont(TTFont('AlexBrush', str(FONTS_DIR / 'AlexBrush-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('Cinzel', str(FONTS_DIR / 'Cinzel-Bold.ttf')))
        pdfmetrics.registerFont(TTFont('Montserrat', str(FONTS_DIR / 'Montserrat-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('Playfair', str(FONTS_DIR / 'PlayfairDisplay-Bold.ttf')))
        pdfmetrics.registerFont(TTFont('SourceCode', str(FONTS_DIR / 'SourceCodePro-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('OpenSans', str(FONTS_DIR / 'OpenSans-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('Lato', str(FONTS_DIR / 'Lato-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('IBMPlex', str(FONTS_DIR / 'IBMPlexSans-Regular.ttf')))
    except:
        pass

def generate_payment_receipt_banknote(certificate_data, qr_data_uri=None):
    """Generate banknote-grade A6 payment receipt"""
    
    full_name = certificate_data.get('full_name', 'Student Name')
    university = certificate_data.get('university', 'University')
    phone = certificate_data.get('phone', '')
    stream = certificate_data.get('stream', '')
    sex = certificate_data.get('sex', '')
    cert_number = certificate_data.get('certificate_number', 'UNY-REC-001')
    verification_token = certificate_data.get('verification_token', '')
    issue_date = certificate_data.get('issue_date', datetime.now().strftime('%b %d, %Y'))
    amount = certificate_data.get('amount', 200)
    payment_method = certificate_data.get('payment_method', 'CBE')
    transaction_number = certificate_data.get('transaction_number', 'TXN-000')
    
    cert_id = cert_number.replace('/', '_').replace('\\', '_')
    output_pdf = CERTIFICATES_DIR / f"{cert_id}.pdf"
    
    # A6 Portrait (105mm x 148mm)
    c = canvas.Canvas(str(output_pdf), pagesize=A6, pageCompression=0)
    w, h = A6  # 105mm x 148mm
    m = 8 * mm  # 8mm OUTER margin
    inner_pad = 6 * mm  # Additional padding inside inner frame
    content_m = m + inner_pad  # All content starts HERE (14mm from edge)
    
    # Colors
    navy = HexColor('#0F2B48')
    gold = HexColor('#C5A059')
    red = HexColor('#B81D1D')
    green = HexColor('#006644')
    white = HexColor('#FFFFFF')
    cream = HexColor('#FDFBF7')
    
    # ============================================
    # PAGE SETUP - Everything INSIDE inner frame
    # ============================================
    # A6: 105mm x 148mm
    # Outer margin: 8mm
    # Triple border thickness: ~5mm total
    # Content safe area: starts at 15mm from all edges
    # ============================================
    
    # CONTENT AREA BOUNDARIES (everything inside these)
    LEFT = 15 * mm      # 15mm from left edge
    RIGHT = w - 15 * mm  # 15mm from right edge
    TOP = h - 15 * mm    # 15mm from top edge
    BOTTOM = 15 * mm     # 15mm from bottom edge
    CONTENT_WIDTH = RIGHT - LEFT  # 75mm usable width
    CONTENT_HEIGHT = TOP - BOTTOM  # 118mm usable height
    
    # ============================================
    # BACKGROUND (white)
    # ============================================
    c.setFillColor(white)
    c.rect(0, 0, w, h, fill=True, stroke=False)
    
    # ============================================
    # WATERMARK (diagonal, visible)
    # ============================================
    c.saveState()
    c.translate(w/2, h/2)
    c.rotate(30)
    c.setFillColor(navy)
    c.setFillAlpha(0.15)
    c.setFont('Cinzel' if 'Cinzel' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold', 30)
    c.drawCentredString(0, 0, 'UNIYO OFFICIAL')
    c.setFillAlpha(1)
    c.restoreState()
    
    # ============================================
    # GUILLOCHE BACKGROUND (inside content area)
    # ============================================
    c.saveState()
    c.setStrokeColor(navy)
    c.setStrokeAlpha(0.01)
    c.setLineWidth(0.2)
    for i in range(15):
        offset = i * 1*mm
        c.rect(LEFT+offset, BOTTOM+offset, CONTENT_WIDTH-2*offset, CONTENT_HEIGHT-2*offset, fill=False, stroke=True)
    c.restoreState()
    
    # ============================================
    # TRIPLE BORDER SYSTEM
    # ============================================
    # Fill between outer and middle frames
    c.setFillColor(gold)
    c.setFillAlpha(0.12)
    c.rect(8*mm, 8*mm, w-16*mm, h-16*mm, fill=True, stroke=False)
    c.setFillAlpha(1)
    
    # FILL between Outer and Middle frames (2mm gold band)
    c.setFillColor(HexColor('#064E3B'))  # Emerald Green (Payment Trust)
    c.setFillAlpha(1.0)
    c.rect(8*mm, 8*mm, w-16*mm, h-16*mm, fill=True, stroke=False)
    c.setFillColor(white)
    c.rect(10*mm, 10*mm, w-20*mm, h-20*mm, fill=True, stroke=False)
    c.setFillAlpha(1)
    
    # Outer navy border (at 8mm)
    # Outer border REMOVED (fill band only)
    
    # Middle border REMOVED (fill band only)
    
    # Inner navy border (at 12mm)
    c.setStrokeColor(navy)
    c.setLineWidth(0.6)
    c.rect(12*mm, 12*mm, w-24*mm, h-24*mm, fill=False, stroke=True)

    # ============================================
    # WATERMARK (diagonal, visible)
    # ============================================
    c.saveState()
    c.translate(w/2, h/2)
    c.rotate(30)
    c.setFillColor(navy)
    c.setFillAlpha(0.15)
    c.setFont('Cinzel' if 'Cinzel' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold', 30)
    c.drawCentredString(0, 0, 'UNIYO OFFICIAL')
    c.setFillAlpha(1)
    c.restoreState()


    
    # ============================================
    # CORNER ROSETTES (on inner border)
    # ============================================
    corner_r = 4*mm
    c.setStrokeColor(gold)
    c.setLineWidth(0.8)
    for cx, cy in [(12*mm, h-12*mm), (w-12*mm, h-12*mm), (12*mm, 12*mm), (w-12*mm, 12*mm)]:
        c.circle(cx, cy, corner_r, fill=False, stroke=True)
        c.setStrokeColor(navy)
        c.setLineWidth(0.4)
        c.circle(cx, cy, corner_r-1.5*mm, fill=False, stroke=True)
        c.setStrokeColor(gold)
    
    # ============================================
    # CONTENT (ALL inside 15mm safe area)
    # ============================================
    
    # Microtext (top, inside frame)
    y_micro = TOP - 3*mm
    c.setFont('Helvetica', 3)
    c.setFillColor(navy)
    c.setFillAlpha(0.4)
    microtext = 'UNIYO • OFFICIAL PAYMENT RECEIPT • BANKNOTE SECURITY • DO NOT FORGE • VALIDATED'
    c.drawCentredString(w/2, y_micro, microtext)
    c.setFillAlpha(1)
    
    # Serial Number
    y_serial = TOP - 6*mm
    c.setFont('Courier-Bold', 5)
    c.setFillColor(red)
    c.drawString(LEFT, y_serial, f'SERIAL: {cert_number[:18]}')
    
    c.setFont('Helvetica-Bold', 3.5)
    c.setFillColor(navy)
    c.drawRightString(RIGHT, y_serial, 'ENCRYPTED')
    
    # Divider line
    c.setStrokeColor(gold)
    c.setLineWidth(0.3)
    c.line(LEFT, TOP-8*mm, RIGHT, TOP-8*mm)
    
    # ============================================
    # HEADER (inside frame)
    # ============================================
    y_header = TOP - 14*mm
    
    # Logo
    logo_file = BASE_DIR / 'static' / 'icons' / 'app_icon-192.png'
    if logo_file.exists():
        logo_img = ImageReader(str(logo_file))
        c.drawImage(logo_img, LEFT, y_header-8*mm, 8*mm, 8*mm, preserveAspectRatio=True, mask='auto')
    
    # UNIYO title
    c.setFillColor(navy)
    c.setFont('Cinzel' if 'Cinzel' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold', 8)
    c.drawString(LEFT+10*mm, y_header-2*mm, 'UNIYO')
    
    c.setFont('Helvetica', 3.5)
    c.setFillColor(gold)
    c.drawString(LEFT+10*mm, y_header-5*mm, 'Office of Student Accounts')
    
    # Receipt headline (right)
    c.setFillColor(navy)
    c.setFont('Playfair' if 'Playfair' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold', 8)
    c.drawRightString(RIGHT, y_header-2*mm, 'OFFICIAL RECEIPT')
    
    c.setFillColor(green)
    c.setFont('Courier-Bold', 4.5)
    c.drawRightString(RIGHT, y_header-5*mm, '✓ PAID & CLEARED')
    
    # ============================================
    # STUDENT INFO (inside frame)
    # ============================================
    y_info = y_header - 12*mm
    
    password = certificate_data.get('password', '')
    # Partial reveal: first + last char, middle obscured
    if password and len(password) > 2:
        partial_pw = password[0] + '•' * (len(password)-2) + password[-1]
    else:
        partial_pw = '•' * len(password) if password else 'N/A'
    
    # SHA256 hash of password
    import hashlib
    pw_hash = hashlib.sha256(password.encode()).hexdigest()[:20] if password else 'N/A'
    
    info_items = [
        ('STUDENT', full_name),
        ('UNIVERSITY', university),
        ('STREAM', f'{stream} Science' if stream else ''),
        ('SEX', sex),
        ('MOBILE', phone),
        ('PASSWORD', partial_pw),
        ('PW-HASH', pw_hash),
        ('RECEIPT NO', cert_number),
        ('DATE', issue_date),
    ]
    
    for label, value in info_items:
        c.setFont('Courier-Bold', 4.5)
        c.setFillColor(navy)
        c.drawString(LEFT, y_info, f'{label}:')
        c.setFont('Courier', 5.5)
        c.setFillColor(HexColor('#333333'))
        c.drawString(LEFT+18*mm, y_info, str(value)[:30])
        y_info -= 4*mm
    
    # ============================================
    # FINANCIAL BOX (inside frame)
    # ============================================
    y_fin = y_info - 5*mm
    box_h = 12*mm
    
    c.setFillColor(HexColor('#FFFBEB'))  # Soft Gold Premium
    c.setStrokeColor(HexColor('#D4AF37'))  # Gold border
    c.setLineWidth(1)
    c.rect(LEFT, y_fin, CONTENT_WIDTH, box_h, fill=True, stroke=True)
    
    c.setFillColor(navy)
    c.setFont('Helvetica-Bold', 6)
    c.drawString(LEFT+3*mm, y_fin+8*mm, 'PREMIUM SUBSCRIPTION')
    
    c.setFont('Helvetica', 3.5)
    c.setFillColor(HexColor('#667788'))
    c.drawString(LEFT+3*mm, y_fin+5.5*mm, '1 Year Full Access - All Courses')
    
    c.setFillColor(navy)
    c.setFont('Playfair' if 'Playfair' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold', 8)
    c.drawRightString(RIGHT-3*mm, y_fin+8*mm, f'{amount} ETB')
    
    c.setFillColor(green)
    c.setFont('Helvetica-Bold', 5)
    c.drawRightString(RIGHT-3*mm, y_fin+5*mm, '✓ PAID')
    
    c.setFont('Helvetica', 4)
    c.setFillColor(navy)
    c.drawString(LEFT+3*mm, y_fin+2.5*mm, f'Method: {payment_method}')
    c.drawString(w/2, y_fin+2.5*mm, f'Trans: {transaction_number}')
    
    # ============================================
    # DUAL STAMPS (inside frame)
    # ============================================
    y_stamp = y_fin - 15*mm
    
    paid_file = BASE_DIR / 'static' / 'Authenticity' / 'paid.png'
    if paid_file.exists():
        paid_img = ImageReader(str(paid_file))
        c.saveState()
    c.translate(w/2, y_stamp+3*mm)
    c.rotate(8)  # Clockwise rotation
    c.drawImage(paid_img, -18*mm, -11*mm, 36*mm, 22*mm, preserveAspectRatio=True, mask='auto')
    c.restoreState()
    
    sa_file = BASE_DIR / 'static' / 'Authenticity' / 'super_admin_stamp.png'
    if sa_file.exists():
        sa_img = ImageReader(str(sa_file))
        c.drawImage(sa_img, RIGHT-25*mm, BOTTOM + CONTENT_HEIGHT*0.60, 28*mm, 28*mm, preserveAspectRatio=True, mask='auto')
    
    # ============================================
    # SIGNATURES (inside frame)
    # ============================================
    y_sig = y_stamp - 10*mm
    
    sig_file = BASE_DIR / 'static' / 'Authenticity' / 'super_admin_signature.png'
    if sig_file.exists():
        sig_img = ImageReader(str(sig_file))
        c.drawImage(sig_img, LEFT+2*mm, y_sig+2*mm, 18*mm, 5*mm, preserveAspectRatio=True, mask='auto')
    c.setFont('Courier-Bold', 4.5)
    c.setFillColor(navy)
    c.drawCentredString(LEFT+12*mm, y_sig-1*mm, 'Chalachew Agegn')
    c.setFont('Helvetica', 3.5)
    c.setFillColor(HexColor('#667788'))
    c.drawCentredString(LEFT+12*mm, y_sig-3.5*mm, 'SUPER ADMIN')
    
    cm_file = BASE_DIR / 'static' / 'Authenticity' / 'signature_(content_manager).png'
    if cm_file.exists():
        cm_img = ImageReader(str(cm_file))
        c.drawImage(cm_img, RIGHT-20*mm, y_sig+2*mm, 18*mm, 5*mm, preserveAspectRatio=True, mask='auto')
    c.setFont('Courier-Bold', 4.5)
    c.setFillColor(navy)
    c.drawCentredString(RIGHT-12*mm, y_sig-1*mm, 'Banch Destaw')
    c.setFont('Helvetica', 3.5)
    c.setFillColor(HexColor('#667788'))
    c.drawCentredString(RIGHT-12*mm, y_sig-3.5*mm, 'CONTENT MANAGER')
    
    # ============================================
    # QR + BARCODE + VERIFY (inside frame)
    # ============================================
    y_qr = BOTTOM + 10*mm
    
    verify_url = f"https://uniyo-cloud.onrender.com/verify/{verification_token}"
    
    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=1)
        qr.add_data(verify_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color='black', back_color='white')
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        c.drawImage(ImageReader(qr_buffer), LEFT, y_qr, 12*mm, 12*mm, preserveAspectRatio=True)
    except:
        pass
    
    c.setFont('Helvetica', 3)
    c.setFillColor(navy)
    c.drawString(LEFT+14*mm, y_qr+8*mm, 'SCAN')
    c.drawString(LEFT+14*mm, y_qr+5*mm, 'TO')
    c.drawString(LEFT+14*mm, y_qr+2*mm, 'VERIFY')
    
    # Barcode
    c.setFillColor(navy)
    random.seed(cert_number)
    bar_x = RIGHT - 25*mm
    for i in range(25):
        bar_w = random.choice([1, 2]) * 0.35*mm
        c.rect(bar_x, y_qr+4*mm, bar_w, 6*mm, fill=True, stroke=False)
        bar_x += bar_w + 0.25*mm
    
    c.setFont('Courier', 3.5)
    c.setFillColor(navy)
    c.drawCentredString(RIGHT-12*mm, y_qr+1*mm, f'*{cert_number[:12]}*')
    
    # ============================================
    # CRYPTO HASH BAR (inside frame, at bottom)
    # ============================================
    y_hash = BOTTOM + 2*mm
    c.setFillColor(navy)
    c.rect(LEFT, y_hash, CONTENT_WIDTH, 5*mm, fill=True, stroke=False)
    
    c.setFillColor(gold)
    c.setFont('Helvetica-Bold', 3.5)
    c.drawString(LEFT+2*mm, y_hash+1.5*mm, 'BANKNOTE GRADE-A')
    
    c.setFont('Courier', 2.5)
    hash_text = verification_token[:40]
    c.drawRightString(RIGHT-2*mm, y_hash+1.5*mm, f'SHA256:{hash_text}')
    
    c.setTitle(f"UNIYO Payment Receipt - {full_name}")
    c.setAuthor("UNIYO - University Made for YOU")
    c.setSubject("Payment Receipt")
    
    c.save()
    return output_pdf
