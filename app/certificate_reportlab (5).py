"""
UNIYO LMS - EXCLUSIVE PERFECT PDF CERTIFICATE & PAYMENT RECEIPT GENERATOR
File: /sdcard/UNIYO/core/certificate_reportlab.py

ORIENTATIONS & FORMATS:
1. VIP Certificates: A4 LANDSCAPE (297mm x 210mm) | Gold Theme | 2 Stamps | Dual Signatures | Gold Foil & Sparkle Particles
2. Promotion Certificates: A4 LANDSCAPE (297mm x 210mm) | Bronze Theme | 2 Stamps | Dual Signatures | Holographic Shimmer
3. Completion Certificates: A4 PORTRAIT (210mm x 297mm) | Indigo Theme | 1 Stamp | Dual Signatures
4. Payment Receipts: A6 PORTRAIT (105mm x 148mm) | Emerald Green Theme | 2 Stamps (Paid Oval + Admin) | Dual Signatures | Watermark "UNIYO PAID"
5. Other Certificates: A4 PORTRAIT (210mm x 297mm) | Slate Theme | 1 Stamp | Single Signature (Super Admin ONLY)
"""

import os
import math
import random
from pathlib import Path
from io import BytesIO
from datetime import datetime

# ReportLab Core Imports
from reportlab.lib.pagesizes import A4, A6, landscape
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

# Asset Directories Setup
ASSETS_DIR = BASE_DIR / "assets" / "certificates"
STAMPS_DIR = ASSETS_DIR / "stamps"
SIGNATURES_DIR = ASSETS_DIR / "signatures"
STATIC_AUTH_DIR = BASE_DIR / "static" / "Authenticity"

for folder in [CERTIFICATES_DIR, ASSETS_DIR, STAMPS_DIR, SIGNATURES_DIR, STATIC_AUTH_DIR]:
    folder.mkdir(parents=True, exist_ok=True)


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
# ASSET RESOLVER HELPERS
# ==============================================================================

def find_stamp_file(filename):
    """Searches for a stamp file across assets and static authenticity folders."""
    possible = [
        STAMPS_DIR / filename,
        STATIC_AUTH_DIR / filename,
        BASE_DIR / "static" / "stamps" / filename,
    ]
    for p in possible:
        if p.exists():
            return p
    return possible[0]


def find_signature_file(filename):
    """Searches for a signature file across assets and static authenticity folders."""
    possible = [
        SIGNATURES_DIR / filename,
        STATIC_AUTH_DIR / filename,
        BASE_DIR / "static" / "signatures" / filename,
    ]
    for p in possible:
        if p.exists():
            return p
    return possible[0]


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


# ==============================================================================
# VECTOR SECURITY & NFT-STYLE GRAPHICS HELPERS
# ==============================================================================

def draw_parchment_background(c, w, h, bg_hex='#FAF7F0'):
    """Draws a premium parchment/cream background."""
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
    c.rotate(30)
    c.setFillColor(HexColor('#1E1B4B') if text == 'UNIYO' else HexColor('#064E3B'))
    c.setFillAlpha(0.04)
    font_sz = 72 if w > 200 * mm else (54 if w > 140 * mm else 36)
    c.setFont(SERIF_BOLD, font_sz)
    c.drawCentredString(0, 0, text)
    c.restoreState()


def draw_anti_copy_pattern(c, w, h, margin_mm=15):
    """Draws fine anti-copy interference line grid."""
    c.saveState()
    c.setStrokeColor(Color(0.02, 0.3, 0.2, alpha=0.04))
    c.setLineWidth(0.25)
    y = margin_mm * mm
    while y < h - (margin_mm * mm):
        c.line(margin_mm * mm, y, w - (margin_mm * mm), y + 10 * mm)
        y += 4 * mm
    c.restoreState()


def draw_guilloche_pattern(c, w, h, primary_color, margin_mm=15, count=12):
    """Renders concentric vector Guilloché security lines inside margins."""
    c.saveState()
    c.setLineWidth(0.22)
    c.setStrokeColor(Color(primary_color.red, primary_color.green, primary_color.blue, alpha=0.10))
    for i in range(count):
        offset = (margin_mm + 3) * mm + (i * 0.9 * mm)
        c.rect(offset, offset, w - (2 * offset), h - (2 * offset), fill=False, stroke=True)
    c.restoreState()


def draw_bezier_corners(c, w, h, gold_color, margin_mm=15, corner_size_mm=20):
    """Draws smooth Bézier curve filigree corner ornaments."""
    c.saveState()
    c.setStrokeColor(gold_color)
    c.setLineWidth(1.6)
    
    corner_size = corner_size_mm * mm
    m = margin_mm * mm
    
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

    # Gold Accent Dots
    c.setFillColor(gold_color)
    dot_r = 1.0 * mm
    c.circle(m + 5 * mm, m + 5 * mm, dot_r, fill=True, stroke=False)
    c.circle(w - m - 5 * mm, m + 5 * mm, dot_r, fill=True, stroke=False)
    c.circle(m + 5 * mm, h - m - 5 * mm, dot_r, fill=True, stroke=False)
    c.circle(w - m - 5 * mm, h - m - 5 * mm, dot_r, fill=True, stroke=False)

    c.restoreState()


def draw_sparkle_particles(c, w, h, gold_color):
    """Draws vector sparkle particles & starbursts for VIP and Promotion certificates."""
    c.saveState()
    c.setFillColor(gold_color)
    c.setStrokeColor(gold_color)
    c.setFillAlpha(0.25)
    
    # Fixed seed for consistent rendering across identical certificate generations
    random_positions = [
        (28 * mm, h - 35 * mm, 2.5 * mm),
        (w - 28 * mm, h - 35 * mm, 2.5 * mm),
        (35 * mm, 42 * mm, 2.0 * mm),
        (w - 35 * mm, 42 * mm, 2.0 * mm),
        (w / 2.0 - 65 * mm, h / 2.0 + 30 * mm, 1.8 * mm),
        (w / 2.0 + 65 * mm, h / 2.0 - 20 * mm, 1.8 * mm),
    ]
    
    for x, y, size in random_positions:
        # 4-point star burst
        p = c.beginPath()
        p.moveTo(x, y - size)
        p.curveTo(x, y, x, y, x + size, y)
        p.curveTo(x, y, x, y, x, y + size)
        p.curveTo(x, y, x, y, x - size, y)
        p.curveTo(x, y, x, y, x, y - size)
        c.drawPath(p, fill=True, stroke=False)
        
    c.restoreState()


def draw_holographic_shimmer(c, w, h):
    """Draws diagonal holographic shimmer ribbons across the background."""
    c.saveState()
    c.setLineWidth(0.4)
    colors_list = [HexColor('#E0E7FF'), HexColor('#FEF3C7'), HexColor('#D1FAE5'), HexColor('#FCE7F3')]
    
    for i, col in enumerate(colors_list):
        c.setStrokeColor(Color(col.red, col.green, col.blue, alpha=0.15))
        offset = 40 * mm + (i * 4 * mm)
        c.line(offset, 15 * mm, offset + 80 * mm, h - 15 * mm)
        c.line(w - offset, 15 * mm, w - offset - 80 * mm, h - 15 * mm)
        
    c.restoreState()


def draw_barcode(c, text, x, y, width=38 * mm, height=10 * mm):
    """Renders a Code-128 barcode directly onto the PDF canvas."""
    try:
        bc = code128.Code128(text, barHeight=height, barWidth=0.7)
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
# TYPE CONFIGURATION MAPPER
# ==============================================================================

OTHER_TYPES = {
    'excellence', 'content_creator', 'marketing_manager', 'advertiser',
    'staff', 'special_congratulations', 'participation', 'appreciation',
    'congratulations', 'other'
}

def resolve_certificate_meta(certificate_data):
    """Resolves certificate type, title, color theme, stamps, format, and signatures."""
    raw_type = str(certificate_data.get('certificate_type', 'completion')).lower()
    rank = certificate_data.get('rank')

    if 'payment' in raw_type or 'receipt' in raw_type or 'paid' in raw_type:
        return {
            'category': 'payment',
            'orientation': 'A6_PORTRAIT',
            'title': 'PAYMENT RECEIPT',
            'subtitle': 'Ethiopian Higher Education Freshman Hub',
            'primary_color': HexColor('#064E3B'),       # Emerald Green (#064E3B)
            'gold_color': HexColor('#C5A059'),
            'primary_stamp': 'paid.png',                # Oval Ecliptical
            'secondary_stamp': 'super_admin_stamp.png', # Circular
            'dual_signatures': True,
            'reason': 'Official payment receipt and financial clearance for 1 Year Premium Access.'
        }
    elif 'vip' in raw_type or 'leaderboard' in raw_type:
        rank_val = rank if (rank and 1 <= int(rank) <= 5) else 1
        return {
            'category': 'vip',
            'orientation': 'A4_LANDSCAPE',              # A4 LANDSCAPE (297mm x 210mm)
            'title': f'VIP RANK #{rank_val} HONOR ROLL CERTIFICATE',
            'subtitle': 'Ethiopian Higher Education Freshman Hub',
            'primary_color': HexColor('#D97706'),       # Gold (#D97706)
            'gold_color': HexColor('#B8860B'),
            'primary_stamp': f'vip{rank_val}.png',
            'secondary_stamp': 'super_admin_stamp.png',
            'dual_signatures': True,
            'reason': 'For achieving elite top performance on the Monthly VIP Leaderboard across the Ethiopian Freshman Hub.'
        }
    elif 'promo' in raw_type:
        return {
            'category': 'promotion',
            'orientation': 'A4_LANDSCAPE',              # A4 LANDSCAPE (297mm x 210mm)
            'title': 'ACADEMIC PROMOTION CERTIFICATE',
            'subtitle': 'Ethiopian Higher Education Freshman Hub',
            'primary_color': HexColor('#7C2D12'),       # Bronze (#7C2D12)
            'gold_color': HexColor('#C5A059'),
            'primary_stamp': 'promotion.png',
            'secondary_stamp': 'super_admin_stamp.png',
            'dual_signatures': True,
            'reason': 'For academic promotion and scholarship excellence award in the Ethiopian Freshman Curriculum.'
        }
    elif raw_type in OTHER_TYPES:
        title_str = raw_type.replace('_', ' ').upper() + " CERTIFICATE"
        return {
            'category': 'other',
            'orientation': 'A4_PORTRAIT',               # A4 PORTRAIT (210mm x 297mm)
            'title': certificate_data.get('title', title_str).upper(),
            'subtitle': 'Ethiopian Higher Education Freshman Hub',
            'primary_color': HexColor('#1F2937'),       # Slate (#1F2937)
            'gold_color': HexColor('#C5A059'),
            'primary_stamp': 'super_admin_stamp.png',
            'secondary_stamp': None,                    # NO secondary stamp
            'dual_signatures': False,                   # Super Admin ONLY
            'reason': 'For distinguished participation, dedication, and service to the UNIYO Academic Platform.'
        }
    else:
        # Default: COMPLETION CERTIFICATE
        return {
            'category': 'completion',
            'orientation': 'A4_PORTRAIT',               # A4 PORTRAIT (210mm x 297mm)
            'title': 'CERTIFICATE OF COMPLETION',
            'subtitle': 'Ethiopian Higher Education Freshman Hub',
            'primary_color': HexColor('#4B0082'),       # Indigo (#4B0082)
            'gold_color': HexColor('#C5A059'),
            'primary_stamp': 'general.png',
            'secondary_stamp': None,                    # NO secondary stamp
            'dual_signatures': True,
            'reason': 'For successfully completing all assigned lessons and worksheets with dedication and academic excellence.'
        }


# ==============================================================================
# 1. A6 PORTRAIT PAYMENT RECEIPT GENERATOR (105mm × 148mm)
# ==============================================================================

def generate_payment_receipt_reportlab(certificate_data, qr_data_uri=None):
    """
    Generates a 100% compliant A6 Portrait Payment Receipt (105mm x 148mm).
    Fitted strictly inside 8mm margins with zero border overflow.
    """
    meta = resolve_certificate_meta(certificate_data)
    
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

    # A6 Setup: w = 105mm, h = 148mm
    c = canvas.Canvas(
        str(output_pdf),
        pagesize=A6,
        pageCompression=0,  # Max quality
        invariant=1
    )
    
    c.setTitle(f"UNIYO Payment Receipt - {full_name}")
    c.setAuthor("UNIYO LMS Financial System")
    c.setSubject("Official Payment Receipt - A6 Portrait")
    
    w, h = A6
    m = 8 * mm  # Strict 8mm margins
    
    primary_color = meta['primary_color']
    gold_color = meta['gold_color']

    # 1. Background & Security Layers
    draw_parchment_background(c, w, h, bg_hex='#FAF7F0')
    draw_watermark(c, w, h, "UNIYO PAID")
    draw_anti_copy_pattern(c, w, h, margin_mm=8)
    draw_guilloche_pattern(c, w, h, primary_color, margin_mm=8, count=4)

    # 2. Double Borders (Outer at 8mm, Inner Gold at 9.5mm)
    c.setStrokeColor(primary_color)
    c.setLineWidth(1.5)
    c.rect(m, m, w - (2 * m), h - (2 * m), fill=False, stroke=True)
    
    c.setStrokeColor(gold_color)
    c.setLineWidth(0.8)
    c.rect(m + 1.5 * mm, m + 1.5 * mm, w - (2 * m) - 3 * mm, h - (2 * m) - 3 * mm, fill=False, stroke=True)

    # Corner Filigree Ornaments
    draw_bezier_corners(c, w, h, gold_color, margin_mm=8, corner_size_mm=10)

    # 3. HEADER SECTION (Logo, Title, Subtitle)
    logo_file = BASE_DIR / 'static' / 'icons' / 'app_icon-192.png'
    draw_transparent_image(c, logo_file, (w / 2.0) - (5 * mm), h - m - 12 * mm, 10 * mm, 10 * mm)

    c.setFillColor(primary_color)
    c.setFont(SERIF_BOLD, 12)
    c.drawCentredString(w / 2.0, h - m - 16.5 * mm, meta['title'])
    
    c.setFillColor(HexColor('#555555'))
    c.setFont(SANS_FONT, 6.5)
    c.drawCentredString(w / 2.0, h - m - 20.5 * mm, meta['subtitle'])

    # 4. RECEIPT METADATA (Receipt Number & Date)
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

    # 6. FINANCIAL & SUBSCRIPTION BOX
    box_top = y_pos - 3 * mm
    box_h = 28 * mm
    box_w = w - (2 * m) - 6 * mm
    box_x = m + 3 * mm
    
    c.setFillColor(HexColor('#F0FDF4'))  # Emerald Light Tint
    c.setStrokeColor(primary_color)
    c.setLineWidth(0.8)
    c.roundRect(box_x, box_top - box_h, box_w, box_h, 2 * mm, fill=True, stroke=True)

    b_y = box_top - 6 * mm
    # Amount Paid (Large)
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

    # 7. STAMPS & SIGNATURES SECTION
    stamps_y = box_top - box_h - 14 * mm
    
    paid_stamp = find_stamp_file(meta['primary_stamp'])
    admin_stamp = find_stamp_file(meta['secondary_stamp'])
    
    draw_transparent_image(c, paid_stamp, (w / 2.0) - 18 * mm, stamps_y, 16 * mm, 14 * mm)
    draw_transparent_image(c, admin_stamp, (w / 2.0) + 2 * mm, stamps_y, 14 * mm, 14 * mm)

    # Dual Signatures
    sig_sa = find_signature_file('super_admin_signature.png')
    sig_cm = find_signature_file('signature_(content_manager).png')
    
    sig_y = stamps_y - 10 * mm
    
    # Super Admin (Left)
    draw_transparent_image(c, sig_sa, m + 3 * mm, sig_y + 3 * mm, 16 * mm, 7 * mm)
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
    draw_transparent_image(c, sig_cm, w - m - 21 * mm, sig_y + 3 * mm, 16 * mm, 7 * mm)
    c.line(w - m - 21 * mm, sig_y + 3 * mm, w - m - 3 * mm, sig_y + 3 * mm)
    c.setFont(SANS_BOLD, 5.5)
    c.setFillColor(HexColor('#111111'))
    c.drawString(w - m - 21 * mm, sig_y, "Banch Destaw")
    c.setFont(SANS_FONT, 4.5)
    c.setFillColor(HexColor('#666666'))
    c.drawString(w - m - 21 * mm, sig_y - 3 * mm, "Content Manager")

    # 8. QR CODE & BARCODE SECTION
    bottom_y = m + 4 * mm
    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=1)
        qr.add_data(verify_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color='black', back_color='white')
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        qr_image = ImageReader(qr_buffer)
        c.drawImage(qr_image, m + 2 * mm, bottom_y + 1 * mm, 13 * mm, 13 * mm, mask='auto')
    except Exception as e:
        print(f"Warning: QR Code Generation Failed: {e}")

    draw_barcode(c, cert_number, w - m - 28 * mm, bottom_y + 3.5 * mm, width=26 * mm, height=7 * mm)

    # 9. MICROTEXT SECURITY
    c.setFillColor(HexColor('#888888'))
    c.setFont(SANS_FONT, 4.2)
    c.drawCentredString(w / 2.0, m + 0.5 * mm, "UNIYO OFFICIAL PAYMENT RECEIPT • TAMPER EVIDENT FINANCIAL RECORD • VERIFY ONLINE")

    c.showPage()
    c.save()
    return output_pdf


# ==============================================================================
# 2. A4 LANDSCAPE CERTIFICATE GENERATOR (297mm × 210mm — VIP & PROMOTION)
# ==============================================================================

def generate_a4_landscape_certificate_reportlab(certificate_data, qr_data_uri=None):
    """
    Generates a 100% compliant A4 LANDSCAPE Certificate (297mm x 210mm).
    Used for VIP Leaderboard and Promotion Certificates.
    """
    meta = resolve_certificate_meta(certificate_data)
    
    full_name = certificate_data.get('full_name', 'Student Name').title()
    university = certificate_data.get('university', 'Ethiopian University')
    stream = certificate_data.get('stream', 'Natural')
    sex = certificate_data.get('sex', 'N/A')
    cert_number = certificate_data.get('certificate_number', 'UNY-VIP-2026-0001')
    issue_date = certificate_data.get('issue_date', datetime.now().strftime('%B %d, %Y'))
    verification_token = certificate_data.get('verification_token', '')
    
    cert_id = cert_number.replace('/', '_').replace('\\', '_')
    output_pdf = CERTIFICATES_DIR / f"{cert_id}.pdf"

    # A4 Landscape Setup: w = 297mm (841.89pt), h = 210mm (595.28pt)
    c = canvas.Canvas(
        str(output_pdf),
        pagesize=landscape(A4),
        pageCompression=0,  # Max print quality
        invariant=1
    )
    
    c.setTitle(f"UNIYO Certificate - {full_name}")
    c.setAuthor("UNIYO - Ethiopian Higher Education Freshman Hub")
    c.setSubject(f"{meta['title']} - {meta['category'].upper()}")
    
    w, h = landscape(A4)
    m = 15 * mm  # Strict 15mm margin
    
    primary_color = meta['primary_color']
    gold_color = meta['gold_color']

    # 1. Background, Watermark, Anti-Copy, Guilloche
    draw_parchment_background(c, w, h, bg_hex='#FAF7F0')
    draw_watermark(c, w, h, "UNIYO")
    draw_anti_copy_pattern(c, w, h, margin_mm=15)
    draw_guilloche_pattern(c, w, h, primary_color, margin_mm=15, count=14)

    # Sparkle Particles & Holographic Shimmer for VIP/Promo
    if meta['category'] == 'vip':
        draw_sparkle_particles(c, w, h, gold_color)
    if meta['category'] in ['vip', 'promotion']:
        draw_holographic_shimmer(c, w, h)

    # 2. Double Borders (Outer at 15mm, Inner Gold at 18mm)
    c.setStrokeColor(primary_color)
    c.setLineWidth(2.5)
    c.rect(m, m, w - (2 * m), h - (2 * m), fill=False, stroke=True)
    
    c.setStrokeColor(gold_color)
    c.setLineWidth(1.2)
    c.rect(m + 3 * mm, m + 3 * mm, w - (2 * m) - 6 * mm, h - (2 * m) - 6 * mm, fill=False, stroke=True)

    # Corner Filigree Ornaments
    draw_bezier_corners(c, w, h, gold_color, margin_mm=15, corner_size_mm=22)

    # 3. TOP SECTION: Logo, Serial Box, Title, Subtitle
    # Logo Top Left
    logo_file = BASE_DIR / 'static' / 'icons' / 'app_icon-192.png'
    draw_transparent_image(c, logo_file, m + 12 * mm, h - m - 24 * mm, 18 * mm, 18 * mm)

    # Serial Number Box Top Right
    serial_x = w - m - 62 * mm
    serial_y = h - m - 22 * mm
    c.setFillColor(HexColor("#FFFBEB"))
    c.setStrokeColor(HexColor("#FCD34D"))
    c.setLineWidth(1)
    c.roundRect(serial_x, serial_y, 50 * mm, 12 * mm, 2 * mm, fill=True, stroke=True)
    
    c.setFont(SANS_BOLD, 6)
    c.setFillColor(gold_color)
    c.drawString(serial_x + 3 * mm, serial_y + 8 * mm, "OFFICIAL SERIAL NUMBER")
    c.setFont(SANS_BOLD, 8)
    c.setFillColor(primary_color)
    c.drawString(serial_x + 3 * mm, serial_y + 2.5 * mm, cert_number)

    # Title & Glow
    draw_smooth_gradient(c, (w / 2.0) - 90 * mm, h - m - 32 * mm, 180 * mm, 12 * mm,
                         Color(0.98, 0.88, 0.5, alpha=0.03), Color(0.7, 0.5, 0.1, alpha=0.03))

    c.setFillColor(primary_color)
    c.setFont(SERIF_BOLD, 22)
    c.drawCentredString(w / 2.0, h - m - 28 * mm, meta['title'])
    
    c.setFillColor(HexColor('#555555'))
    c.setFont(SERIF_ITALIC, 10)
    c.drawCentredString(w / 2.0, h - m - 34 * mm, meta['subtitle'])

    # 4. MIDDLE SECTION: Presentation & Student Name
    c.setFillColor(HexColor('#666666'))
    c.setFont(SERIF_ITALIC, 11)
    c.drawCentredString(w / 2.0, h - m - 46 * mm, "This certificate is proudly presented to")

    # Student Name (Large Serif, 30pt)
    c.setFillColor(primary_color)
    c.setFont(SERIF_BOLD, 28)
    c.drawCentredString(w / 2.0, h - m - 58 * mm, full_name)

    # Gold Accent Underline
    c.setStrokeColor(gold_color)
    c.setLineWidth(1.8)
    name_w = max(c.stringWidth(full_name, SERIF_BOLD, 28) * 0.75, 110 * mm)
    c.line((w / 2.0) - (name_w / 2.0), h - m - 61 * mm, (w / 2.0) + (name_w / 2.0), h - m - 61 * mm)

    # Reason Text Box
    reason_box_y = h - m - 80 * mm
    reason_box_h = 16 * mm
    reason_box_w = w - (2 * m) - 40 * mm
    reason_box_x = (w - reason_box_w) / 2.0

    c.setFillColor(HexColor('#F8F6F0'))
    c.setStrokeColor(HexColor('#E2D9C8'))
    c.setLineWidth(0.8)
    c.roundRect(reason_box_x, reason_box_y, reason_box_w, reason_box_h, 3 * mm, fill=True, stroke=True)

    c.setFillColor(HexColor('#333333'))
    c.setFont(SERIF_FONT, 10)
    reason_str = certificate_data.get('title', meta['reason'])
    c.drawCentredString(w / 2.0, reason_box_y + 9.5 * mm, reason_str[:110])
    c.drawCentredString(w / 2.0, reason_box_y + 4.5 * mm, "demonstrating academic distinction across the Ethiopian Higher Education System.")

    # Academic Metadata Strip
    stream_str = f"{stream} Science" if not str(stream).endswith('Science') else stream
    meta_str = f"{university}   •   {stream_str}   •   Sex: {sex}"
    c.setFont(SERIF_ITALIC, 9.5)
    c.setFillColor(gold_color)
    c.drawCentredString(w / 2.0, h - m - 88 * mm, meta_str)

    # 5. CREDENTIALS PANEL (Number, Date, Type, Verify URL)
    cred_y = h - m - 114 * mm
    cred_h = 22 * mm
    cred_w = w - (2 * m) - 40 * mm
    cred_x = (w - cred_w) / 2.0

    c.setFillColor(HexColor('#FFFFFF'))
    c.setStrokeColor(primary_color)
    c.setLineWidth(1)
    c.roundRect(cred_x, cred_y, cred_w, cred_h, 3 * mm, fill=True, stroke=True)

    c.setFont(SANS_FONT, 8)
    c.setFillColor(HexColor('#555555'))
    c.drawString(cred_x + 8 * mm, cred_y + 13.5 * mm, f"CERTIFICATE NO: {cert_number}")
    c.drawString(cred_x + 95 * mm, cred_y + 13.5 * mm, f"ISSUE DATE: {str(issue_date)[:12]}")
    c.drawString(cred_x + 175 * mm, cred_y + 13.5 * mm, f"TYPE: {meta['category'].upper()}")

    verify_url = f"https://uniyo-cloud.onrender.com/verify/{verification_token}"
    c.setFont(SANS_BOLD, 8)
    c.setFillColor(primary_color)
    c.drawString(cred_x + 8 * mm, cred_y + 5 * mm, f"VERIFY ONLINE: {verify_url}")

    # 6. BOTTOM SECTION: Stamps, Signatures, QR Code, Barcode, Microtext
    bottom_y = m + 5 * mm

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
        c.drawImage(qr_image, m + 12 * mm, bottom_y + 4 * mm, 22 * mm, 22 * mm, preserveAspectRatio=True)
        c.setFont(SANS_FONT, 6.5)
        c.setFillColor(HexColor('#666666'))
        c.drawString(m + 12 * mm, bottom_y + 0.5 * mm, "Scan to Verify")
    except Exception as e:
        print(f"Warning: QR Code Generation Failed: {e}")

    # Barcode (Bottom Center-Left)
    draw_barcode(c, cert_number, m + 42 * mm, bottom_y + 12 * mm, width=42 * mm, height=12 * mm)

    # Stamps System (Bottom Center Area)
    primary_stamp_path = find_stamp_file(meta['primary_stamp'])
    sec_stamp_path = find_stamp_file(meta['secondary_stamp'])
    
    draw_transparent_image(c, primary_stamp_path, (w / 2.0) - 10 * mm, bottom_y + 2 * mm, 28 * mm, 28 * mm)
    draw_transparent_image(c, sec_stamp_path, (w / 2.0) + 22 * mm, bottom_y + 2 * mm, 26 * mm, 26 * mm)

    # Signatures System (Bottom Right Area)
    sig_sa_file = find_signature_file('super_admin_signature.png')
    sig_cm_file = find_signature_file('signature_(content_manager).png')

    sig1_x = w - m - 68 * mm
    sig2_x = w - m - 34 * mm
    sig_y = bottom_y + 4 * mm

    # Content Manager Signature (Left)
    draw_transparent_image(c, sig_cm_file, sig1_x, sig_y + 8 * mm, 28 * mm, 14 * mm)
    c.setLineWidth(0.8)
    c.setStrokeColor(HexColor("#94A3B8"))
    c.line(sig1_x, sig_y + 8 * mm, sig1_x + 28 * mm, sig_y + 8 * mm)
    c.setFont(SANS_BOLD, 6.5)
    c.setFillColor(HexColor("#0F172A"))
    c.drawString(sig1_x, sig_y + 3.5 * mm, "Prof. Tigist Hailu")
    c.setFont(SANS_FONT, 5.5)
    c.setFillColor(HexColor("#64748B"))
    c.drawString(sig1_x, sig_y - 0.5 * mm, "Content Manager")

    # Super Admin Signature (Right)
    draw_transparent_image(c, sig_sa_file, sig2_x, sig_y + 8 * mm, 28 * mm, 14 * mm)
    c.line(sig2_x, sig_y + 8 * mm, sig2_x + 28 * mm, sig_y + 8 * mm)
    c.setFont(SANS_BOLD, 6.5)
    c.setFillColor(HexColor("#0F172A"))
    c.drawString(sig2_x, sig_y + 3.5 * mm, "Dr. Solomon Tadesse")
    c.setFont(SANS_FONT, 5.5)
    c.setFillColor(HexColor("#64748B"))
    c.drawString(sig2_x, sig_y - 0.5 * mm, "Super Admin Director")

    # Microtext Security Line (Very Bottom)
    c.setFillColor(HexColor('#888888'))
    c.setFont(SANS_FONT, 5.5)
    c.drawCentredString(w / 2.0, m + 1.0 * mm,
                        "UNIYO AUTHENTIC CERTIFICATE • ETHIOPIAN HIGHER EDUCATION FRESHMAN HUB • VERIFY ONLINE • TAMPER EVIDENT")

    # 7. Save Canvas
    c.showPage()
    c.save()
    return output_pdf


# ==============================================================================
# 3. A4 PORTRAIT CERTIFICATE GENERATOR (210mm × 297mm — COMPLETION & OTHER)
# ==============================================================================

def generate_a4_portrait_certificate_reportlab(certificate_data, qr_data_uri=None):
    """
    Generates a 100% compliant A4 PORTRAIT Certificate (210mm x 297mm).
    Used for Completion and Other Certificate Types.
    """
    meta = resolve_certificate_meta(certificate_data)
    
    full_name = certificate_data.get('full_name', 'Student Name').title()
    university = certificate_data.get('university', 'Ethiopian University')
    stream = certificate_data.get('stream', 'Natural')
    sex = certificate_data.get('sex', 'N/A')
    cert_number = certificate_data.get('certificate_number', 'UNY-COMP-2026-0001')
    issue_date = certificate_data.get('issue_date', datetime.now().strftime('%B %d, %Y'))
    verification_token = certificate_data.get('verification_token', '')
    
    cert_id = cert_number.replace('/', '_').replace('\\', '_')
    output_pdf = CERTIFICATES_DIR / f"{cert_id}.pdf"

    c = canvas.Canvas(
        str(output_pdf),
        pagesize=A4,
        pageCompression=0,  # Max print quality
        invariant=1
    )
    
    c.setTitle(f"UNIYO Certificate - {full_name}")
    c.setAuthor("UNIYO - Ethiopian Higher Education Freshman Hub")
    c.setSubject(f"{meta['title']} - {meta['category'].upper()}")
    
    w, h = A4
    m = 15 * mm  # Strict 15mm margin
    
    primary_color = meta['primary_color']
    gold_color = meta['gold_color']

    # 1. Background & Security Layers
    draw_parchment_background(c, w, h, bg_hex='#FAF7F0')
    draw_watermark(c, w, h, "UNIYO")
    draw_guilloche_pattern(c, w, h, primary_color, margin_mm=15, count=14)

    # 2. Double Borders (Outer at 15mm, Inner Gold at 18mm)
    c.setStrokeColor(primary_color)
    c.setLineWidth(2.5)
    c.rect(m, m, w - (2 * m), h - (2 * m), fill=False, stroke=True)
    
    c.setStrokeColor(gold_color)
    c.setLineWidth(1.2)
    c.rect(m + 3 * mm, m + 3 * mm, w - (2 * m) - 6 * mm, h - (2 * m) - 6 * mm, fill=False, stroke=True)

    # Corner Filigree Ornaments
    draw_bezier_corners(c, w, h, gold_color, margin_mm=15, corner_size_mm=22)

    # 3. TOP SECTION: Logo, Title, Subtitle, Divider
    logo_file = BASE_DIR / 'static' / 'icons' / 'app_icon-192.png'
    draw_transparent_image(c, logo_file, (w / 2.0) - (9 * mm), h - m - 23 * mm, 18 * mm, 18 * mm)

    draw_smooth_gradient(c, (w / 2.0) - 75 * mm, h - m - 39 * mm, 150 * mm, 12 * mm,
                         Color(0.98, 0.88, 0.5, alpha=0.03), Color(0.7, 0.5, 0.1, alpha=0.03))

    c.setFillColor(primary_color)
    c.setFont(SERIF_BOLD, 22)
    c.drawCentredString(w / 2.0, h - m - 36 * mm, meta['title'])
    
    c.setFillColor(HexColor('#555555'))
    c.setFont(SERIF_ITALIC, 10.5)
    c.drawCentredString(w / 2.0, h - m - 42 * mm, meta['subtitle'])

    c.setStrokeColor(gold_color)
    c.setLineWidth(1)
    c.line((w / 2.0) - 45 * mm, h - m - 46 * mm, (w / 2.0) + 45 * mm, h - m - 46 * mm)
    c.setFillColor(gold_color)
    c.circle(w / 2.0, h - m - 46 * mm, 1.5 * mm, fill=True, stroke=False)

    # 4. MIDDLE SECTION: Student Presentation & Name
    c.setFillColor(HexColor('#666666'))
    c.setFont(SERIF_ITALIC, 11)
    c.drawCentredString(w / 2.0, h - m - 58 * mm, "This certificate is proudly presented to")

    c.setFillColor(primary_color)
    c.setFont(SERIF_BOLD, 28)
    c.drawCentredString(w / 2.0, h - m - 71 * mm, full_name)

    c.setStrokeColor(gold_color)
    c.setLineWidth(1.8)
    name_w = max(c.stringWidth(full_name, SERIF_BOLD, 28) * 0.75, 95 * mm)
    c.line((w / 2.0) - (name_w / 2.0), h - m - 74 * mm, (w / 2.0) + (name_w / 2.0), h - m - 74 * mm)

    # Reason Box
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
    reason_str = certificate_data.get('title', meta['reason'])
    c.drawCentredString(w / 2.0, reason_box_y + 9.5 * mm, reason_str[:85])
    c.drawCentredString(w / 2.0, reason_box_y + 4.5 * mm, "demonstrating academic distinction in the Ethiopian Freshman Curriculum.")

    stream_str = f"{stream} Science" if not str(stream).endswith('Science') else stream
    meta_str = f"{university}   •   {stream_str}   •   Sex: {sex}"
    c.setFont(SERIF_ITALIC, 9.5)
    c.setFillColor(gold_color)
    c.drawCentredString(w / 2.0, h - m - 102 * mm, meta_str)

    # 5. CREDENTIALS BOX
    cred_y = h - m - 132 * mm
    cred_h = 26 * mm
    cred_w = w - (2 * m) - 18 * mm
    cred_x = (w - cred_w) / 2.0

    c.setFillColor(HexColor('#FFFFFF'))
    c.setStrokeColor(primary_color)
    c.setLineWidth(1)
    c.roundRect(cred_x, cred_y, cred_w, cred_h, 3 * mm, fill=True, stroke=True)

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
    c.drawRightString(cred_x + cred_w - 6 * mm, cred_y + 5 * mm, meta['category'].upper())

    verify_url = f"https://uniyo-cloud.onrender.com/verify/{verification_token}"
    c.setFont(SANS_BOLD, 8)
    c.setFillColor(primary_color)
    c.drawCentredString(w / 2.0, cred_y - 6 * mm, f"Verify Online at: {verify_url}")

    # 6. BOTTOM SECTION: Stamps, Signatures, QR Code, Barcode, Microtext
    auth_dir = BASE_DIR / 'static' / 'Authenticity'

    # --- SIGNATURES ---
    sig_y = 84 * mm
    sig_sa_file = find_signature_file('super_admin_signature.png')

    if meta['dual_signatures']:
        # Dual Signatures Mode (Completion)
        sig_cm_file = find_signature_file('signature_(content_manager).png')
        
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
    else:
        # Single Signature Mode ('Other' type: Super Admin ONLY)
        sig_x = (w / 2.0) - 18 * mm
        draw_transparent_image(c, sig_sa_file, sig_x, sig_y + 5 * mm, 36 * mm, 14 * mm)
        c.setStrokeColor(HexColor('#94A3B8'))
        c.setLineWidth(0.8)
        c.line((w / 2.0) - 22 * mm, sig_y + 5 * mm, (w / 2.0) + 22 * mm, sig_y + 5 * mm)
        c.setFont(SANS_BOLD, 8.5)
        c.setFillColor(HexColor('#111111'))
        c.drawCentredString(w / 2.0, sig_y + 0.5 * mm, "Chalachew Agegn")
        c.setFont(SANS_FONT, 7)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(w / 2.0, sig_y - 3.5 * mm, "Super Admin Director")

    # --- PRIMARY STAMP ONLY (general.png or super_admin_stamp.png) ---
    primary_stamp_path = find_stamp_file(meta['primary_stamp'])
    draw_transparent_image(c, primary_stamp_path, (w / 2.0) - (16 * mm), 46 * mm, 32 * mm, 32 * mm)

    # --- QR CODE & BARCODE ---
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

    draw_barcode(c, cert_number, (w / 2.0) - (20 * mm), 22 * mm, width=40 * mm, height=12 * mm)

    # --- MICROTEXT SECURITY LINE ---
    c.setFillColor(HexColor('#888888'))
    c.setFont(SANS_FONT, 5.5)
    c.drawCentredString(w / 2.0, m + 1.5 * mm,
                        "UNIYO AUTHENTIC CERTIFICATE • ETHIOPIAN HIGHER EDUCATION FRESHMAN HUB • VERIFY ONLINE • TAMPER EVIDENT")

    # 7. Save Canvas
    c.showPage()
    c.save()
    return output_pdf


# ==============================================================================
# MAIN ROUTING GATEWAY
# ==============================================================================

def generate_certificate_reportlab(certificate_data, qr_data_uri=None):
    """
    Main PDF Generator Gateway.
    Routes certificates based on orientation requirements:
    - A6_PORTRAIT  -> Payment Receipts (A6 Portrait: 105mm x 148mm)
    - A4_LANDSCAPE -> VIP & Promotion Certificates (A4 Landscape: 297mm x 210mm)
    - A4_PORTRAIT  -> Completion & Other Certificates (A4 Portrait: 210mm x 297mm)
    """
    meta = resolve_certificate_meta(certificate_data)
    
    if meta['orientation'] == 'A6_PORTRAIT':
        return generate_payment_receipt_reportlab(certificate_data, qr_data_uri)
    elif meta['orientation'] == 'A4_LANDSCAPE':
        return generate_a4_landscape_certificate_reportlab(certificate_data, qr_data_uri)
    else:
        return generate_a4_portrait_certificate_reportlab(certificate_data, qr_data_uri)
