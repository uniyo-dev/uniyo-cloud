"""
UNIYO LMS - EXCLUSIVE PERFECT PDF CERTIFICATE & PAYMENT RECEIPT GENERATOR
File: /sdcard/UNIYO/core/certificate_reportlab.py
Update: 100% Comprehensive A6 Portrait Payment Receipt (All 27 Requirements Included)
"""

import os
import math
from pathlib import Path
from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4, A6
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode import code128
import qrcode

from core.paths import CERTIFICATES_DIR, BASE_DIR

# ==============================================================================
# FONT REGISTRATION (Serif & Sans Fallbacks)
# ==============================================================================
font_dir = Path('/usr/share/fonts/truetype/dejavu')
SERIF_FONT = 'Times-Roman'
SERIF_BOLD = 'Times-Bold'
SERIF_ITALIC = 'Times-Italic'
SANS_FONT = 'Helvetica'
SANS_BOLD = 'Helvetica-Bold'

if font_dir.exists():
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSerif', str(font_dir / 'DejaVuSerif.ttf')))
        pdfmetrics.registerFont(TTFont('DejaVuSerif-Bold', str(font_dir / 'DejaVuSerif-Bold.ttf')))
        pdfmetrics.registerFont(TTFont('DejaVuSerif-Italic', str(font_dir / 'DejaVuSerif-Italic.ttf')))
        SERIF_FONT = 'DejaVuSerif'
        SERIF_BOLD = 'DejaVuSerif-Bold'
        SERIF_ITALIC = 'DejaVuSerif-Italic'
    except Exception:
        pass
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', str(font_dir / 'DejaVuSans.ttf')))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', str(font_dir / 'DejaVuSans-Bold.ttf')))
        SANS_FONT = 'DejaVuSans'
        SANS_BOLD = 'DejaVuSans-Bold'
    except Exception:
        pass


# ==============================================================================
# CORE HELPER FUNCTIONS FOR A6 PORTRAIT RECEIPT
# ==============================================================================

def draw_parchment_background(c, w, h, bg_hex='#FAF7F0'):
    """Draws a premium parchment/cream background."""
    c.saveState()
    c.setFillColor(HexColor(bg_hex))
    c.rect(0, 0, w, h, fill=True, stroke=False)
    c.restoreState()


def draw_watermark(c, w, h, text="UNIYO PAID"):
    """Draws a subtle 4% opacity diagonal watermark."""
    c.saveState()
    c.translate(w / 2.0, h / 2.0)
    c.rotate(30)
    c.setFillColor(HexColor('#064E3B'))
    c.setFillAlpha(0.04)
    c.setFont(SERIF_BOLD, 42)
    c.drawCentredString(0, 0, text)
    c.restoreState()


def draw_anti_copy_pattern(c, w, h, margin_mm=8):
    """Draws fine anti-copy interference lines."""
    c.saveState()
    c.setStrokeColor(Color(0.02, 0.3, 0.2, alpha=0.04))
    c.setLineWidth(0.25)
    y = margin_mm * mm
    while y < h - (margin_mm * mm):
        c.line(margin_mm * mm, y, w - (margin_mm * mm), y + 10 * mm)
        y += 3.5 * mm
    c.restoreState()


def draw_guilloche_pattern_a6(c, w, h, primary_color, gold_color):
    """Draws fine concentric vector Guilloché border lines inside A6 margins."""
    c.saveState()
    c.setLineWidth(0.2)
    c.setStrokeColor(Color(primary_color.red, primary_color.green, primary_color.blue, alpha=0.10))
    for i in range(4):
        offset = 9.5 * mm + (i * 0.8 * mm)
        c.rect(offset, offset, w - (2 * offset), h - (2 * offset), fill=False, stroke=True)
    c.restoreState()


def draw_bezier_corners_a6(c, w, h, gold_color):
    """Draws smooth Bézier curve filigree corners for A6 portrait."""
    c.saveState()
    c.setStrokeColor(gold_color)
    c.setLineWidth(1.2)
    
    corner_size = 10 * mm
    m = 8 * mm
    
    # Bottom-Left
    p = c.beginPath()
    p.moveTo(m, m + corner_size)
    p.curveTo(m, m + (corner_size / 2.0), m + (corner_size / 2.0), m, m + corner_size, m)
    c.drawPath(p, fill=False, stroke=True)
    
    # Bottom-Right
    p = c.beginPath()
    p.moveTo(w - m - corner_size, m)
    p.curveTo(w - m - (corner_size / 2.0), m, w - m, m + (corner_size / 2.0), w - m, m + corner_size)
    c.drawPath(p, fill=False, stroke=True)
    
    # Top-Left
    p = c.beginPath()
    p.moveTo(m, h - m - corner_size)
    p.curveTo(m, h - m - (corner_size / 2.0), m + (corner_size / 2.0), h - m, m + corner_size, h - m)
    c.drawPath(p, fill=False, stroke=True)
    
    # Top-Right
    p = c.beginPath()
    p.moveTo(w - m - corner_size, h - m)
    p.curveTo(w - m - (corner_size / 2.0), h - m, w - m, h - m - (corner_size / 2.0), w - m, h - m - corner_size)
    c.drawPath(p, fill=False, stroke=True)
    
    c.restoreState()


def draw_transparent_image(c, file_path, x, y, width, height):
    """Safely draws PNGs using mask='auto' to preserve 100% transparency."""
    if file_path and os.path.exists(file_path):
        try:
            img = ImageReader(str(file_path))
            c.drawImage(img, x, y, width=width, height=height, preserveAspectRatio=True, mask='auto')
            return True
        except Exception as e:
            print(f"Warning: Image load failed ({file_path}): {e}")
    return False


def draw_barcode(c, text, x, y, width=32 * mm, height=7 * mm):
    """Renders a Code-128 barcode strictly inside A6 printable area."""
    try:
        bc = code128.Code128(text, barHeight=height, barWidth=0.55)
        bc.drawOn(c, x, y)
    except Exception:
        c.saveState()
        c.setFillColor(HexColor('#111111'))
        c.rect(x, y, width, height, fill=True, stroke=False)
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont(SANS_FONT, 5)
        c.drawCentredString(x + (width / 2.0), y + 2 * mm, text)
        c.restoreState()


# ==============================================================================
# COMPLETE A6 PORTRAIT PAYMENT RECEIPT GENERATOR (105mm × 148mm)
# ==============================================================================

def generate_payment_receipt_reportlab(certificate_data, qr_data_uri=None):
    """
    Generate COMPLETE A6 Portrait Payment Receipt (105mm x 148mm)
    Meets all 27 strict requirements with zero border overflow.
    """
    full_name = certificate_data.get('full_name', 'Student Name').title()
    university = certificate_data.get('university', 'Ethiopian University')
    phone = certificate_data.get('phone', 'N/A')
    cert_number = certificate_data.get('certificate_number', 'UNY-REC-2026-001')
    issue_date = certificate_data.get('issue_date', datetime.now().strftime('%b %d, %Y'))
    verification_token = certificate_data.get('verification_token', '')
    
    # Financial fields from certificate_data / payments table mapping
    amount = certificate_data.get('amount', certificate_data.get('amount_paid', '200'))
    amount_paid = f"{amount} ETB" if not str(amount).endswith('ETB') else amount
    payment_method = str(certificate_data.get('payment_method', 'CBE / Telebirr')).upper()
    transaction_id = certificate_data.get('transaction_number', certificate_data.get('transaction_id', 'TXN-998822'))
    subscription_plan = certificate_data.get('subscription', '1 Year Premium Access')
    
    cert_id = cert_number.replace('/', '_').replace('\\', '_')
    output_pdf = CERTIFICATES_DIR / f"{cert_id}.pdf"

    # A6 Setup: w = 105mm (297.64pt), h = 148mm (419.53pt)
    c = canvas.Canvas(
        str(output_pdf),
        pagesize=A6,
        pageCompression=0,  # Max print quality
        invariant=1
    )
    
    c.setTitle(f"UNIYO Payment Receipt - {full_name}")
    c.setAuthor("UNIYO LMS Financial System")
    c.setSubject("Official Payment Receipt - A6 Portrait")
    
    w, h = A6
    m = 8 * mm  # Strict 8mm margins
    
    primary_color = HexColor('#064E3B')  # Emerald Green
    gold_color = HexColor('#C5A059')     # Warm Gold

    # 1. Background & Security Layers
    draw_parchment_background(c, w, h, bg_hex='#FAF7F0')
    draw_watermark(c, w, h, "UNIYO PAID")
    draw_anti_copy_pattern(c, w, h, margin_mm=8)
    draw_guilloche_pattern_a6(c, w, h, primary_color, gold_color)

    # 2. Double Borders (Outer at 8mm, Inner Gold at 9.5mm)
    c.setStrokeColor(primary_color)
    c.setLineWidth(1.5)
    c.rect(m, m, w - (2 * m), h - (2 * m), fill=False, stroke=True)
    
    c.setStrokeColor(gold_color)
    c.setLineWidth(0.8)
    c.rect(m + 1.5 * mm, m + 1.5 * mm, w - (2 * m) - 3 * mm, h - (2 * m) - 3 * mm, fill=False, stroke=True)

    # Corner Filigree Ornaments
    draw_bezier_corners_a6(c, w, h, gold_color)

    # 3. HEADER SECTION (Logo, Title, Subtitle)
    logo_file = BASE_DIR / 'static' / 'icons' / 'app_icon-192.png'
    if not draw_transparent_image(c, logo_file, (w / 2.0) - (5 * mm), h - m - 12 * mm, 10 * mm, 10 * mm):
        c.saveState()
        c.setFillColor(primary_color)
        c.rect((w / 2.0) - (4 * mm), h - m - 11 * mm, 8 * mm, 8 * mm, fill=True, stroke=False)
        c.restoreState()

    c.setFillColor(primary_color)
    c.setFont(SERIF_BOLD, 12)
    c.drawCentredString(w / 2.0, h - m - 16.5 * mm, "PAYMENT RECEIPT")
    
    c.setFillColor(HexColor('#555555'))
    c.setFont(SANS_FONT, 6.5)
    c.drawCentredString(w / 2.0, h - m - 20.5 * mm, "Ethiopian Higher Education Freshman Hub")

    # 4. RECEIPT METADATA (Receipt Number & Date)
    y_pos = h - m - 25.5 * mm
    c.setFont(SANS_BOLD, 7)
    c.setFillColor(primary_color)
    c.drawString(m + 4 * mm, y_pos, f"Receipt: {cert_number}")
    c.setFont(SANS_FONT, 7)
    c.setFillColor(HexColor('#333333'))
    c.drawRightString(w - m - 4 * mm, y_pos, f"Date: {str(issue_date)[:10]}")
    
    # Divider Rule
    y_pos -= 2.5 * mm
    c.setStrokeColor(HexColor('#CBD5E1'))
    c.setLineWidth(0.6)
    c.line(m + 3 * mm, y_pos, w - m - 3 * mm, y_pos)

    # 5. STUDENT & UNIVERSITY DETAILS
    y_pos -= 4.5 * mm
    c.setFont(SANS_BOLD, 6.5)
    c.setFillColor(primary_color)
    c.drawString(m + 4 * mm, y_pos, "RECEIVED FROM:")
    
    y_pos -= 4.5 * mm
    c.setFont(SERIF_BOLD, 10.5)
    c.setFillColor(HexColor('#111111'))
    c.drawString(m + 4 * mm, y_pos, full_name)
    
    y_pos -= 3.5 * mm
    c.setFont(SANS_FONT, 7)
    c.setFillColor(HexColor('#444444'))
    c.drawString(m + 4 * mm, y_pos, f"{university}  •  Ph: {phone}")

    # 6. PROMINENT FINANCIAL & SUBSCRIPTION BOX
    box_top = y_pos - 3 * mm
    box_h = 28 * mm
    box_w = w - (2 * m) - 6 * mm
    box_x = m + 3 * mm
    
    c.setFillColor(HexColor('#F0FDF4'))  # Light Emerald Tint
    c.setStrokeColor(primary_color)
    c.setLineWidth(0.8)
    c.roundRect(box_x, box_top - box_h, box_w, box_h, 2 * mm, fill=True, stroke=True)

    b_y = box_top - 6 * mm
    # Amount Paid (Large & Prominent)
    c.setFont(SANS_BOLD, 11.5)
    c.setFillColor(primary_color)
    c.drawString(box_x + 3.5 * mm, b_y, f"AMOUNT: {amount_paid}")
    
    # Status Tag: ✓ PAID
    c.setFont(SANS_BOLD, 9)
    c.setFillColor(HexColor('#16A34A'))
    c.drawRightString(box_x + box_w - 3.5 * mm, b_y, "✓ PAID")

    b_y -= 5.5 * mm
    c.setFont(SANS_FONT, 7)
    c.setFillColor(HexColor('#333333'))
    c.drawString(box_x + 3.5 * mm, b_y, f"Method: {payment_method}")
    c.drawRightString(box_x + box_w - 3.5 * mm, b_y, f"Trans: {transaction_id}")

    b_y -= 5.5 * mm
    c.setFont(SANS_BOLD, 7.5)
    c.setFillColor(primary_color)
    c.drawString(box_x + 3.5 * mm, b_y, f"Subscription: {subscription_plan}")

    b_y -= 5 * mm
    verify_url = f"https://uniyo-cloud.onrender.com/verify/{verification_token}"
    c.setFont(SANS_FONT, 6)
    c.setFillColor(HexColor('#555555'))
    c.drawString(box_x + 3.5 * mm, b_y, f"Verify: {verify_url[:42]}...")

    # 7. STAMPS & SIGNATURES SECTION (Strictly Inside Margins)
    auth_dir = BASE_DIR / 'static' / 'Authenticity'
    stamps_y = box_top - box_h - 14 * mm
    
    # Primary Stamp (paid.png) & Secondary Stamp (super_admin_stamp.png)
    paid_stamp_path = auth_dir / 'paid.png'
    admin_stamp_path = auth_dir / 'super_admin_stamp.png'
    
    draw_transparent_image(c, paid_stamp_path, (w / 2.0) - 18 * mm, stamps_y, 16 * mm, 14 * mm)
    draw_transparent_image(c, admin_stamp_path, (w / 2.0) + 2 * mm, stamps_y, 14 * mm, 14 * mm)

    # Dual Signatures (Super Admin + Content Manager)
    sig_sa_file = auth_dir / 'super_admin_signature.png'
    sig_cm_file = auth_dir / 'signature_(content_manager).png'
    
    sig_y = stamps_y - 10 * mm
    
    # Super Admin (Left)
    draw_transparent_image(c, sig_sa_file, m + 3 * mm, sig_y + 3 * mm, 16 * mm, 7 * mm)
    c.setStrokeColor(HexColor('#999999'))
    c.setLineWidth(0.5)
    c.line(m + 3 * mm, sig_y + 3 * mm, m + 21 * mm, sig_y + 3 * mm)
    c.setFont(SANS_BOLD, 5.5)
    c.setFillColor(HexColor('#111111'))
    c.drawString(m + 3 * mm, sig_y, "Chalachew Agegn")
    c.setFont(SANS_FONT, 4.5)
    c.setFillColor(HexColor('#666666'))
    c.drawString(m + 3 * mm, sig_y - 3 * mm, "Super Admin")

    # Content Manager (Right)
    draw_transparent_image(c, sig_cm_file, w - m - 21 * mm, sig_y + 3 * mm, 16 * mm, 7 * mm)
    c.line(w - m - 21 * mm, sig_y + 3 * mm, w - m - 3 * mm, sig_y + 3 * mm)
    c.setFont(SANS_BOLD, 5.5)
    c.setFillColor(HexColor('#111111'))
    c.drawString(w - m - 21 * mm, sig_y, "Banch Destaw")
    c.setFont(SANS_FONT, 4.5)
    c.setFillColor(HexColor('#666666'))
    c.drawString(w - m - 21 * mm, sig_y - 3 * mm, "Content Manager")

    # 8. QR CODE & BARCODE SECTION (Strictly Inside 8mm Borders)
    bottom_y = m + 4 * mm
    
    # QR Code (Bottom-Left)
    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=1)
        qr.add_data(verify_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color='black', back_color='white')
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        qr_image = ImageReader(qr_buffer)
        c.drawImage(qr_image, m + 2 * mm, bottom_y + 1 * mm, 13 * mm, 13 * mm, preserveAspectRatio=True)
    except Exception as e:
        print(f"Warning: QR Code Generation Failed: {e}")

    # Barcode (Bottom-Right)
    draw_barcode(c, cert_number, w - m - 28 * mm, bottom_y + 3.5 * mm, width=26 * mm, height=7 * mm)

    # 9. MICROTEXT SECURITY (Very Bottom at 8.5mm, safely inside margin)
    c.setFillColor(HexColor('#888888'))
    c.setFont(SANS_FONT, 4.2)
    c.drawCentredString(w / 2.0, m + 0.5 * mm, "UNIYO OFFICIAL PAYMENT RECEIPT • TAMPER EVIDENT FINANCIAL RECORD • VERIFY ONLINE")

    # Save PDF Canvas
    c.showPage()
    c.save()
    
    return output_pdf


# ==============================================================================
# MAIN CERTIFICATE GATEWAY (Routes Payment to A6, Others to A4)
# ==============================================================================

def generate_certificate_reportlab(certificate_data, qr_data_uri=None):
    """
    Main PDF Generator Gateway.
    Routes payment receipts to specialized A6 Portrait Generator, and others to A4.
    """
    raw_type = certificate_data.get('certificate_type', 'completion').lower()
    
    # Route Payment Receipts to dedicated A6 Generator
    if 'payment' in raw_type or 'receipt' in raw_type or 'paid' in raw_type:
        return generate_payment_receipt_reportlab(certificate_data, qr_data_uri)

    # Standard A4 Certificates (VIP, Completion, Promotion, Other)
    if 'vip' in raw_type:
        cert_type = 'vip'
    elif 'promo' in raw_type:
        cert_type = 'promotion'
    elif 'other' in raw_type:
        cert_type = 'other'
    else:
        cert_type = 'completion'

    full_name = certificate_data.get('full_name', 'Student Name').title()
    university = certificate_data.get('university', 'Ethiopian University')
    stream = certificate_data.get('stream', '')
    sex = certificate_data.get('sex', '')
    cert_number = certificate_data.get('certificate_number', 'UNY-2026-0000')
    title = certificate_data.get('title', 'Certificate of Completion')
    issue_date = certificate_data.get('issue_date', datetime.now().strftime('%Y-%m-%d'))
    rank = certificate_data.get('rank')
    verification_token = certificate_data.get('verification_token', '')
    
    cert_id = cert_number.replace('/', '_').replace('\\', '_')
    output_pdf = CERTIFICATES_DIR / f"{cert_id}.pdf"

    # A4 Portrait Setup: w = 210mm, h = 297mm
    c = canvas.Canvas(
        str(output_pdf),
        pagesize=A4,
        pageCompression=0,
        invariant=1
    )
    
    c.setTitle(f"UNIYO Certificate - {full_name}")
    c.setAuthor("UNIYO - Ethiopian Higher Education Freshman Hub")
    c.setSubject(f"{title} - {cert_type.upper()}")
    
    w, h = A4
    primary_color = HexColor('#0B192C') if cert_type == 'vip' else HexColor('#1E3A8A')
    gold_color = HexColor('#C5A059')

    # Background & Borders
    c.setFillColor(HexColor('#FAF7F0'))
    c.rect(0, 0, w, h, fill=True, stroke=False)
    
    c.setStrokeColor(primary_color)
    c.setLineWidth(2.5)
    c.rect(15 * mm, 15 * mm, w - 30 * mm, h - 30 * mm, fill=False, stroke=True)
    
    c.setStrokeColor(gold_color)
    c.setLineWidth(1.2)
    c.rect(18 * mm, 18 * mm, w - 36 * mm, h - 36 * mm, fill=False, stroke=True)

    # Logo & Header
    logo_file = BASE_DIR / 'static' / 'icons' / 'app_icon-192.png'
    draw_transparent_image(c, logo_file, (w / 2.0) - (8 * mm), h - 38 * mm, 16 * mm, 16 * mm)

    c.setFillColor(primary_color)
    c.setFont(SERIF_BOLD, 20)
    c.drawCentredString(w / 2.0, h - 46 * mm, title.upper())
    
    c.setFillColor(HexColor('#555555'))
    c.setFont(SERIF_ITALIC, 10)
    c.drawCentredString(w / 2.0, h - 52 * mm, "Ethiopian Higher Education Freshman Hub")

    # Student Attestation
    c.setFillColor(HexColor('#666666'))
    c.setFont(SERIF_ITALIC, 11)
    c.drawCentredString(w / 2.0, h - 63 * mm, "This certificate is proudly presented to")

    c.setFillColor(primary_color)
    c.setFont(SERIF_BOLD, 24)
    c.drawCentredString(w / 2.0, h - 75 * mm, full_name)

    c.setFillColor(HexColor('#333333'))
    c.setFont(SERIF_FONT, 10)
    c.drawCentredString(w / 2.0, h - 87 * mm, "For successfully completing lessons and worksheets with dedication.")

    # Credentials Box
    cred_top = h - 100 * mm
    c.setFillColor(HexColor('#FAF9F5'))
    c.setStrokeColor(primary_color)
    c.setLineWidth(1)
    c.roundRect(22 * mm, cred_top - 28 * mm, w - 44 * mm, 28 * mm, 3 * mm, fill=True, stroke=True)

    y_line = cred_top - 7 * mm
    c.setFont(SANS_FONT, 8.5)
    c.setFillColor(HexColor('#555555'))
    c.drawString(28 * mm, y_line, "Certificate Number:")
    c.setFillColor(HexColor('#111111'))
    c.drawRightString(w - 28 * mm, y_line, cert_number)

    y_line -= 6.5 * mm
    c.setFillColor(HexColor('#555555'))
    c.drawString(28 * mm, y_line, "Issue Date:")
    c.setFillColor(HexColor('#111111'))
    c.drawRightString(w - 28 * mm, y_line, str(issue_date)[:10])

    y_line -= 6.5 * mm
    c.setFillColor(HexColor('#555555'))
    c.drawString(28 * mm, y_line, "Type:")
    c.setFillColor(primary_color)
    c.drawRightString(w - 28 * mm, y_line, cert_type.upper())

    y_line -= 6.5 * mm
    verify_url = f"https://uniyo-cloud.onrender.com/verify/{verification_token}"
    c.setFillColor(primary_color)
    c.setFont(SANS_BOLD, 7.5)
    c.drawCentredString(w / 2.0, y_line, f"Verify at: {verify_url}")

    # Bottom Section (Stamps, Barcode, Signatures)
    auth_dir = BASE_DIR / 'static' / 'Authenticity'
    primary_stamp_file = auth_dir / 'general.png'
    draw_transparent_image(c, primary_stamp_file, (w / 2.0) - (19 * mm), 72 * mm, 38 * mm, 38 * mm)

    draw_barcode(c, cert_number, (w / 2.0) - (22 * mm), 42 * mm, width=44 * mm, height=14 * mm)

    # Signatures
    sig_sa_file = auth_dir / 'super_admin_signature.png'
    sig_cm_file = auth_dir / 'signature_(content_manager).png'
    
    draw_transparent_image(c, sig_sa_file, 24 * mm, 134 * mm, 30 * mm, 12 * mm)
    draw_transparent_image(c, sig_cm_file, w - 54 * mm, 134 * mm, 30 * mm, 12 * mm)

    # Save
    c.showPage()
    c.save()
    
    return output_pdf
