"""
UNIYO LMS - EXCLUSIVE PERFECT PDF CERTIFICATE & PAYMENT RECEIPT GENERATOR
File: /sdcard/UNIYO/core/certificate_reportlab.py
Update: Upgraded A4 Completion Certificate (Ultra-Rich Quality matching A6 Receipt)
100% Vector Quality, Multi-Layer Security, Bézier Filigrees, Transparent PNGs (mask='auto')
"""

import os
import math
from pathlib import Path
from io import BytesIO
from datetime import datetime

# ReportLab Core Imports
from reportlab.lib.pagesizes import A4, A6
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode import code128

import qrcode

# LMS Path Imports
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
# COMMON VECTOR & GRAPHICS HELPERS
# ==============================================================================

def draw_parchment_background(c, w, h, bg_hex='#FAF7F0'):
    """Draws a premium parchment/cream background (not harsh white)."""
    c.saveState()
    c.setFillColor(HexColor(bg_hex))
    c.rect(0, 0, w, h, fill=True, stroke=False)
    c.restoreState()


def draw_smooth_gradient(c, x, y, width, height, color1, color2, vertical=True):
    """Renders a smooth gradient for title glows and gold foil highlights."""
    c.saveState()
    steps = 80
    for i in range(steps):
        ratio = i / steps
        r = color1.red * (1 - ratio) + color2.red * ratio
        g = color1.green * (1 - ratio) + color2.green * ratio
        b = color1.blue * (1 - ratio) + color2.blue * ratio
        c.setFillColor(Color(r, g, b, alpha=0.025))
        if vertical:
            c.rect(x, y + i * (height / steps), width, (height / steps) + 0.5, fill=True, stroke=False)
        else:
            c.rect(x + i * (width / steps), y, (width / steps) + 0.5, height, fill=True, stroke=False)
    c.restoreState()


def draw_watermark(c, w, h, text="UNIYO"):
    """Draws a subtle 4% opacity diagonal watermark."""
    c.saveState()
    c.translate(w / 2.0, h / 2.0)
    c.rotate(32)
    c.setFillColor(HexColor('#1E1B4B'))
    c.setFillAlpha(0.04)
    c.setFont(SERIF_BOLD, 72 if w > 150 * mm else 42)
    c.drawCentredString(0, 0, text)
    c.restoreState()


def draw_guilloche_pattern_a4(c, w, h, primary_color, gold_color):
    """
    Renders 14+ concentric vector Guilloché security lines
    strictly inside the 15mm border.
    """
    c.saveState()
    c.setLineWidth(0.25)
    c.setStrokeColor(Color(primary_color.red, primary_color.green, primary_color.blue, alpha=0.12))
    
    steps = 14
    for i in range(steps):
        offset = 18 * mm + (i * 1.2 * mm)
        c.rect(offset, offset, w - (2 * offset), h - (2 * offset), fill=False, stroke=True)
        
    c.restoreState()


def draw_bezier_corners_a4(c, w, h, primary_color, gold_color):
    """Draws smooth Bézier curve filigree corner ornaments (not sharp L-shapes)."""
    c.saveState()
    c.setStrokeColor(gold_color)
    c.setLineWidth(1.8)
    
    corner_size = 22 * mm
    m = 15 * mm  # Strict 15mm margin
    
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
    
    # Small Gold Filigree Circles
    c.setFillColor(gold_color)
    c.circle(m + 7 * mm, m + 7 * mm, 1.2 * mm, fill=True, stroke=False)
    c.circle(w - m - 7 * mm, m + 7 * mm, 1.2 * mm, fill=True, stroke=False)
    c.circle(m + 7 * mm, h - m - 7 * mm, 1.2 * mm, fill=True, stroke=False)
    c.circle(w - m - 7 * mm, h - m - 7 * mm, 1.2 * mm, fill=True, stroke=False)

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


def draw_barcode(c, text, x, y, width=44 * mm, height=12 * mm):
    """Renders a Code-128 barcode directly onto the PDF canvas."""
    try:
        bc = code128.Code128(text, barHeight=height, barWidth=0.75)
        bc.drawOn(c, x, y)
    except Exception:
        c.saveState()
        c.setFillColor(HexColor('#111111'))
        c.rect(x, y, width, height, fill=True, stroke=False)
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont(SANS_FONT, 6)
        c.drawCentredString(x + (width / 2.0), y + 3 * mm, text)
        c.restoreState()


# ==============================================================================
# 1. UPGRADED A4 PORTRAIT COMPLETION CERTIFICATE GENERATOR (210mm × 297mm)
# ==============================================================================

def generate_completion_certificate_reportlab(certificate_data, qr_data_uri=None):
    """
    Generate ULTRA-RICH A4 Portrait Completion Certificate (210mm x 297mm)
    Matches the craftsmanship, rich colors, and multi-layer security of the Payment Receipt.
    Strictly fitted inside 15mm margins.
    """
    full_name = certificate_data.get('full_name', 'Student Name').title()
    university = certificate_data.get('university', 'Ethiopian University')
    stream = certificate_data.get('stream', 'Natural')
    sex = certificate_data.get('sex', 'N/A')
    cert_number = certificate_data.get('certificate_number', 'UNY-COMP-2026-0001')
    title = certificate_data.get('title', 'CERTIFICATE OF COMPLETION')
    issue_date = certificate_data.get('issue_date', datetime.now().strftime('%B %d, %Y'))
    verification_token = certificate_data.get('verification_token', '')
    
    cert_id = cert_number.replace('/', '_').replace('\\', '_')
    output_pdf = CERTIFICATES_DIR / f"{cert_id}.pdf"

    # A4 Portrait: w = 210mm (595.28pt), h = 297mm (841.89pt)
    c = canvas.Canvas(
        str(output_pdf),
        pagesize=A4,
        pageCompression=0,  # Max quality, zero compression
        invariant=1
    )
    
    c.setTitle(f"UNIYO Certificate - {full_name}")
    c.setAuthor("UNIYO - Ethiopian Higher Education Freshman Hub")
    c.setSubject(f"{title} - COMPLETION")
    
    w, h = A4
    m = 15 * mm  # Strict 15mm margin
    
    # Professional Palette: Deep Indigo + Warm Gold
    primary_color = HexColor('#4B0082')  # Deep Indigo (#4B0082)
    accent_dark = HexColor('#1E1B4B')    # Midnight Violet
    gold_color = HexColor('#C5A059')     # Warm Antique Gold

    # 1. Background & Security Layers
    draw_parchment_background(c, w, h, bg_hex='#FAF7F0')
    draw_watermark(c, w, h, "UNIYO")
    draw_guilloche_pattern_a4(c, w, h, primary_color, gold_color)

    # 2. Double Borders (Outer at 15mm, Inner Gold at 18mm)
    c.setStrokeColor(primary_color)
    c.setLineWidth(2.5)
    c.rect(m, m, w - (2 * m), h - (2 * m), fill=False, stroke=True)
    
    c.setStrokeColor(gold_color)
    c.setLineWidth(1.2)
    c.rect(m + 3 * mm, m + 3 * mm, w - (2 * m) - 6 * mm, h - (2 * m) - 6 * mm, fill=False, stroke=True)

    # Smooth Bézier Corner Filigrees
    draw_bezier_corners_a4(c, w, h, primary_color, gold_color)

    # 3. TOP SECTION: Logo, Title, Subtitle, Divider
    # Logo (App Icon at top center)
    logo_file = BASE_DIR / 'static' / 'icons' / 'app_icon-192.png'
    draw_transparent_image(c, logo_file, (w / 2.0) - (9 * mm), h - m - 23 * mm, 18 * mm, 18 * mm)

    # Gold Gradient Glow Behind Title
    draw_smooth_gradient(c, (w / 2.0) - 75 * mm, h - m - 39 * mm, 150 * mm, 12 * mm,
                         Color(0.98, 0.88, 0.5, alpha=0.03), Color(0.7, 0.5, 0.1, alpha=0.03))

    # Certificate Title (24pt Serif Bold)
    c.setFillColor(primary_color)
    c.setFont(SERIF_BOLD, 22)
    c.drawCentredString(w / 2.0, h - m - 36 * mm, "CERTIFICATE OF COMPLETION")
    
    # Subtitle
    c.setFillColor(HexColor('#555555'))
    c.setFont(SERIF_ITALIC, 10.5)
    c.drawCentredString(w / 2.0, h - m - 42 * mm, "Ethiopian Higher Education Freshman Hub")

    # Gold Accent Divider Line
    c.setStrokeColor(gold_color)
    c.setLineWidth(1)
    c.line((w / 2.0) - 45 * mm, h - m - 46 * mm, (w / 2.0) + 45 * mm, h - m - 46 * mm)
    c.setFillColor(gold_color)
    c.circle(w / 2.0, h - m - 46 * mm, 1.5 * mm, fill=True, stroke=False)

    # 4. MIDDLE SECTION: Student Presentation & Name
    c.setFillColor(HexColor('#666666'))
    c.setFont(SERIF_ITALIC, 11)
    c.drawCentredString(w / 2.0, h - m - 58 * mm, "This certificate is proudly presented to")

    # Student Name (Large Serif, 30pt)
    c.setFillColor(accent_dark)
    c.setFont(SERIF_BOLD, 28)
    c.drawCentredString(w / 2.0, h - m - 71 * mm, full_name)

    # Gold Underline Accent
    c.setStrokeColor(gold_color)
    c.setLineWidth(1.8)
    name_w = max(c.stringWidth(full_name, SERIF_BOLD, 28) * 0.75, 95 * mm)
    c.line((w / 2.0) - (name_w / 2.0), h - m - 74 * mm, (w / 2.0) + (name_w / 2.0), h - m - 74 * mm)

    # Reason Text (Boxed with soft parchment tint)
    reason_box_y = h - m - 94 * mm
    reason_box_h = 16 * mm
    reason_box_w = w - (2 * m) - 18 * mm
    reason_box_x = (w - reason_box_w) / 2.0

    c.setFillColor(HexColor('#F8F6F0'))
    c.setStrokeColor(HexColor('#E2D9C8'))
    c.setLineWidth(0.8)
    c.roundRect(reason_box_x, reason_box_y, reason_box_w, reason_box_h, 3 * mm, fill=True, stroke=True)

    c.setFillColor(HexColor('#333333'))
    c.setFont(SERIF_FONT, 10)
    c.drawCentredString(w / 2.0, reason_box_y + 9.5 * mm, "For successfully completing lessons and worksheets with dedication,")
    c.drawCentredString(w / 2.0, reason_box_y + 4.5 * mm, "demonstrating academic excellence in the Ethiopian Freshman Curriculum.")

    # Academic Metadata Strip (University • Stream • Sex)
    stream_str = f"{stream} Science" if not str(stream).endswith('Science') else stream
    meta_str = f"{university}   •   {stream_str}   •   Sex: {sex}"
    c.setFont(SERIF_ITALIC, 9.5)
    c.setFillColor(gold_color)
    c.drawCentredString(w / 2.0, h - m - 102 * mm, meta_str)

    # 5. CREDENTIALS BOX (Number, Date, Type, Verify URL)
    cred_y = h - m - 132 * mm
    cred_h = 26 * mm
    cred_w = w - (2 * m) - 18 * mm
    cred_x = (w - cred_w) / 2.0

    c.setFillColor(HexColor('#FFFFFF'))
    c.setStrokeColor(primary_color)
    c.setLineWidth(1)
    c.roundRect(cred_x, cred_y, cred_w, cred_h, 3 * mm, fill=True, stroke=True)

    # Credential Details
    c.setFont(SANS_FONT, 8.5)
    c.setFillColor(HexColor('#555555'))
    c.drawString(cred_x + 6 * mm, cred_y + 18 * mm, "Certificate Number:")
    c.setFont(SANS_BOLD, 8.5)
    c.setFillColor(HexColor('#111111'))
    c.drawRightString(cred_x + cred_w - 6 * mm, cred_y + 18 * mm, cert_number)

    c.setFont(SANS_FONT, 8.5)
    c.setFillColor(HexColor('#555555'))
    c.drawString(cred_x + 6 * mm, cred_y + 11.5 * mm, "Issue Date:")
    c.setFont(SANS_BOLD, 8.5)
    c.setFillColor(HexColor('#111111'))
    c.drawRightString(cred_x + cred_w - 6 * mm, cred_y + 11.5 * mm, str(issue_date)[:12])

    c.setFont(SANS_FONT, 8.5)
    c.setFillColor(HexColor('#555555'))
    c.drawString(cred_x + 6 * mm, cred_y + 5 * mm, "Type:")
    c.setFont(SANS_BOLD, 8.5)
    c.setFillColor(primary_color)
    c.drawRightString(cred_x + cred_w - 6 * mm, cred_y + 5 * mm, "COMPLETION")

    # Verify URL (Placed cleanly below credentials box)
    verify_url = f"https://uniyo-cloud.onrender.com/verify/{verification_token}"
    c.setFont(SANS_BOLD, 8)
    c.setFillColor(primary_color)
    c.drawCentredString(w / 2.0, cred_y - 6 * mm, f"Verify Online at: {verify_url}")

    # 6. BOTTOM SECTION: Signatures, Primary Stamp, QR Code, Barcode, Microtext
    auth_dir = BASE_DIR / 'static' / 'Authenticity'

    # --- SIGNATURES (y = 86mm) ---
    sig_y = 84 * mm
    sig_sa_file = auth_dir / 'super_admin_signature.png'
    sig_cm_file = auth_dir / 'signature_(content_manager).png'

    # Super Admin Signature (Bottom Left)
    draw_transparent_image(c, sig_sa_file, m + 8 * mm, sig_y + 5 * mm, 30 * mm, 12 * mm)
    c.setStrokeColor(HexColor('#94A3B8'))
    c.setLineWidth(0.8)
    c.line(m + 8 * mm, sig_y + 5 * mm, m + 44 * mm, sig_y + 5 * mm)
    c.setFont(SANS_BOLD, 8)
    c.setFillColor(HexColor('#111111'))
    c.drawString(m + 8 * mm, sig_y + 0.5 * mm, "Chalachew Agegn")
    c.setFont(SANS_FONT, 7)
    c.setFillColor(HexColor('#666666'))
    c.drawString(m + 8 * mm, sig_y - 3.5 * mm, "Super Admin Director")

    # Content Manager Signature (Bottom Right)
    draw_transparent_image(c, sig_cm_file, w - m - 44 * mm, sig_y + 5 * mm, 30 * mm, 12 * mm)
    c.line(w - m - 44 * mm, sig_y + 5 * mm, w - m - 8 * mm, sig_y + 5 * mm)
    c.setFont(SANS_BOLD, 8)
    c.setFillColor(HexColor('#111111'))
    c.drawString(w - m - 44 * mm, sig_y + 0.5 * mm, "Banch Destaw")
    c.setFont(SANS_FONT, 7)
    c.setFillColor(HexColor('#666666'))
    c.drawString(w - m - 44 * mm, sig_y - 3.5 * mm, "Content Manager")

    # --- PRIMARY STAMP ONLY (general.png, Bottom Center: y = 46mm to 78mm) ---
    primary_stamp_file = auth_dir / 'general.png'
    draw_transparent_image(c, primary_stamp_file, (w / 2.0) - (16 * mm), 46 * mm, 32 * mm, 32 * mm)

    # --- QR CODE & BARCODE (Bottom Area: y = 22mm to 42mm) ---
    # QR Code (Bottom Left)
    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=1)
        qr.add_data(verify_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color='black', back_color='white')
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        qr_image = ImageReader(qr_buffer)
        c.drawImage(qr_image, m + 8 * mm, 22 * mm, 20 * mm, 20 * mm, preserveAspectRatio=True)
        c.setFont(SANS_FONT, 6.5)
        c.setFillColor(HexColor('#666666'))
        c.drawString(m + 8 * mm, 18.5 * mm, "Scan to Verify")
    except Exception as e:
        print(f"Warning: QR Code Generation Failed: {e}")

    # Barcode (Bottom Center: y = 22mm to 34mm)
    draw_barcode(c, cert_number, (w / 2.0) - (20 * mm), 22 * mm, width=40 * mm, height=12 * mm)

    # --- MICROTEXT SECURITY LINE (Very Bottom at 16.5mm, strictly inside 15mm margin) ---
    c.setFillColor(HexColor('#888888'))
    c.setFont(SANS_FONT, 5.5)
    c.drawCentredString(w / 2.0, m + 1.5 * mm,
                        "UNIYO AUTHENTIC CERTIFICATE • ETHIOPIAN HIGHER EDUCATION FRESHMAN HUB • VERIFY ONLINE • TAMPER EVIDENT")

    # 7. Save Canvas
    c.showPage()
    c.save()
    
    return output_pdf


# ==============================================================================
# 2. A6 PORTRAIT PAYMENT RECEIPT GENERATOR (105mm × 148mm)
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
    
    amount = certificate_data.get('amount', certificate_data.get('amount_paid', '200'))
    amount_paid = f"{amount} ETB" if not str(amount).endswith('ETB') else amount
    payment_method = str(certificate_data.get('payment_method', 'CBE / Telebirr')).upper()
    transaction_id = certificate_data.get('transaction_number', certificate_data.get('transaction_id', 'TXN-998822'))
    subscription_plan = certificate_data.get('subscription', '1 Year Premium Access')
    
    cert_id = cert_number.replace('/', '_').replace('\\', '_')
    output_pdf = CERTIFICATES_DIR / f"{cert_id}.pdf"

    c = canvas.Canvas(
        str(output_pdf),
        pagesize=A6,
        pageCompression=0,
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

    # Anti-copy fine lines
    c.saveState()
    c.setStrokeColor(Color(0.02, 0.3, 0.2, alpha=0.04))
    c.setLineWidth(0.25)
    y = m
    while y < h - m:
        c.line(m, y, w - m, y + 10 * mm)
        y += 3.5 * mm
    c.restoreState()

    # Guilloche Frames
    c.saveState()
    c.setLineWidth(0.2)
    c.setStrokeColor(Color(primary_color.red, primary_color.green, primary_color.blue, alpha=0.10))
    for i in range(4):
        offset = 9.5 * mm + (i * 0.8 * mm)
        c.rect(offset, offset, w - (2 * offset), h - (2 * offset), fill=False, stroke=True)
    c.restoreState()

    # 2. Double Borders (Outer at 8mm, Inner Gold at 9.5mm)
    c.setStrokeColor(primary_color)
    c.setLineWidth(1.5)
    c.rect(m, m, w - (2 * m), h - (2 * m), fill=False, stroke=True)
    
    c.setStrokeColor(gold_color)
    c.setLineWidth(0.8)
    c.rect(m + 1.5 * mm, m + 1.5 * mm, w - (2 * m) - 3 * mm, h - (2 * m) - 3 * mm, fill=False, stroke=True)

    # 3. HEADER SECTION
    logo_file = BASE_DIR / 'static' / 'icons' / 'app_icon-192.png'
    draw_transparent_image(c, logo_file, (w / 2.0) - (5 * mm), h - m - 12 * mm, 10 * mm, 10 * mm)

    c.setFillColor(primary_color)
    c.setFont(SERIF_BOLD, 12)
    c.drawCentredString(w / 2.0, h - m - 16.5 * mm, "PAYMENT RECEIPT")
    
    c.setFillColor(HexColor('#555555'))
    c.setFont(SANS_FONT, 6.5)
    c.drawCentredString(w / 2.0, h - m - 20.5 * mm, "Ethiopian Higher Education Freshman Hub")

    # 4. RECEIPT METADATA
    y_pos = h - m - 25.5 * mm
    c.setFont(SANS_BOLD, 7)
    c.setFillColor(primary_color)
    c.drawString(m + 4 * mm, y_pos, f"Receipt: {cert_number}")
    c.setFont(SANS_FONT, 7)
    c.setFillColor(HexColor('#333333'))
    c.drawRightString(w - m - 4 * mm, y_pos, f"Date: {str(issue_date)[:10]}")
    
    y_pos -= 2.5 * mm
    c.setStrokeColor(HexColor('#CBD5E1'))
    c.setLineWidth(0.6)
    c.line(m + 3 * mm, y_pos, w - m - 3 * mm, y_pos)

    # 5. STUDENT DETAILS
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

    # 6. FINANCIAL BOX
    box_top = y_pos - 3 * mm
    box_h = 28 * mm
    box_w = w - (2 * m) - 6 * mm
    box_x = m + 3 * mm
    
    c.setFillColor(HexColor('#F0FDF4'))
    c.setStrokeColor(primary_color)
    c.setLineWidth(0.8)
    c.roundRect(box_x, box_top - box_h, box_w, box_h, 2 * mm, fill=True, stroke=True)

    b_y = box_top - 6 * mm
    c.setFont(SANS_BOLD, 11.5)
    c.setFillColor(primary_color)
    c.drawString(box_x + 3.5 * mm, b_y, f"AMOUNT: {amount_paid}")
    
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

    # 7. STAMPS & SIGNATURES
    auth_dir = BASE_DIR / 'static' / 'Authenticity'
    stamps_y = box_top - box_h - 14 * mm
    
    draw_transparent_image(c, auth_dir / 'paid.png', (w / 2.0) - 18 * mm, stamps_y, 16 * mm, 14 * mm)
    draw_transparent_image(c, auth_dir / 'super_admin_stamp.png', (w / 2.0) + 2 * mm, stamps_y, 14 * mm, 14 * mm)

    sig_y = stamps_y - 10 * mm
    draw_transparent_image(c, auth_dir / 'super_admin_signature.png', m + 3 * mm, sig_y + 3 * mm, 16 * mm, 7 * mm)
    c.setStrokeColor(HexColor('#999999'))
    c.setLineWidth(0.5)
    c.line(m + 3 * mm, sig_y + 3 * mm, m + 21 * mm, sig_y + 3 * mm)
    c.setFont(SANS_BOLD, 5.5)
    c.setFillColor(HexColor('#111111'))
    c.drawString(m + 3 * mm, sig_y, "Chalachew Agegn")
    c.setFont(SANS_FONT, 4.5)
    c.setFillColor(HexColor('#666666'))
    c.drawString(m + 3 * mm, sig_y - 3 * mm, "Super Admin")

    draw_transparent_image(c, auth_dir / 'signature_(content_manager).png', w - m - 21 * mm, sig_y + 3 * mm, 16 * mm, 7 * mm)
    c.line(w - m - 21 * mm, sig_y + 3 * mm, w - m - 3 * mm, sig_y + 3 * mm)
    c.setFont(SANS_BOLD, 5.5)
    c.setFillColor(HexColor('#111111'))
    c.drawString(w - m - 21 * mm, sig_y, "Banch Destaw")
    c.setFont(SANS_FONT, 4.5)
    c.setFillColor(HexColor('#666666'))
    c.drawString(w - m - 21 * mm, sig_y - 3 * mm, "Content Manager")

    # 8. QR & BARCODE
    bottom_y = m + 4 * mm
    try:
        qr = qrcode.QRCode(version=1, box_size=8, border=1)
        qr.add_data(verify_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color='black', back_color='white')
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        c.drawImage(ImageReader(qr_buffer), m + 2 * mm, bottom_y + 1 * mm, 13 * mm, 13 * mm, mask='auto')
    except Exception:
        pass

    draw_barcode(c, cert_number, w - m - 28 * mm, bottom_y + 3.5 * mm, width=26 * mm, height=7 * mm)

    c.setFillColor(HexColor('#888888'))
    c.setFont(SANS_FONT, 4.2)
    c.drawCentredString(w / 2.0, m + 0.5 * mm, "UNIYO OFFICIAL PAYMENT RECEIPT • TAMPER EVIDENT FINANCIAL RECORD • VERIFY ONLINE")

    c.showPage()
    c.save()
    return output_pdf


# ==============================================================================
# MAIN ROUTING GATEWAY
# ==============================================================================

def generate_certificate_reportlab(certificate_data, qr_data_uri=None):
    """
    Main PDF Generator Gateway.
    Routes payment receipts to A6 Generator, and all other certificates to A4 Generator.
    """
    raw_type = certificate_data.get('certificate_type', 'completion').lower()
    
    # Route Payment Receipts to dedicated A6 Generator
    if 'payment' in raw_type or 'receipt' in raw_type or 'paid' in raw_type:
        return generate_payment_receipt_reportlab(certificate_data, qr_data_uri)
    
    # Default to Upgraded Ultra-Rich A4 Completion Certificate
    return generate_completion_certificate_reportlab(certificate_data, qr_data_uri)
