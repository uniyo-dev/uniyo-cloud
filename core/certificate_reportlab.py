"""
UNIYO LMS - EXCLUSIVE PERFECT PDF Certificate Generator
Professional printing quality using ReportLab
Exact A4 Portrait: 210mm x 297mm (Printable Area: 180mm x 267mm inside 15mm margins)
100% Compliance with all PDF, Security, Transparency, and Layout Requirements
"""

import os
import math
from pathlib import Path
from io import BytesIO
from datetime import datetime

# ReportLab Core Imports
from reportlab.lib.pagesizes import A4
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
# HELPER FUNCTIONS (Gradients, Vectors, Images, Security)
# ==============================================================================

def draw_parchment_background(c, w, h):
    """Draws a premium parchment/cream background (not pure white)."""
    c.saveState()
    c.setFillColor(HexColor('#FAF7F0'))  # Soft cream parchment tone
    c.rect(0, 0, w, h, fill=True, stroke=False)
    c.restoreState()


def draw_smooth_gradient(c, x, y, width, height, color1, color2, vertical=True):
    """Renders a smooth gradient for VIP gold foil / premium title effects."""
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


def draw_guilloche_pattern(c, w, h, primary_color, gold_color):
    """Draws fine concentric vector Guilloché border lines strictly inside margins."""
    c.saveState()
    c.setLineWidth(0.25)
    c.setStrokeColor(Color(primary_color.red, primary_color.green, primary_color.blue, alpha=0.12))
    
    steps = 12
    for i in range(steps):
        offset = 18 * mm + (i * 1.2 * mm)
        c.rect(offset, offset, w - (2 * offset), h - (2 * offset), fill=False, stroke=True)
        
    c.restoreState()


def draw_bezier_corners(c, w, h, primary_color, gold_color):
    """Draws smooth Bézier curve filigree corners (not sharp L-shapes)."""
    c.saveState()
    c.setStrokeColor(gold_color)
    c.setLineWidth(2)
    
    corner_size = 20 * mm
    m = 15 * mm  # Margin boundary
    
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


def draw_watermark(c, w, h, text="UNIYO"):
    """Draws a subtle 4% opacity diagonal watermark."""
    c.saveState()
    c.translate(w / 2.0, h / 2.0)
    c.rotate(32)
    c.setFillColor(HexColor('#0B192C'))
    c.setFillAlpha(0.04)
    c.setFont(SERIF_BOLD, 72)
    c.drawCentredString(0, 0, text)
    c.restoreState()


def draw_anti_copy_pattern(c, w, h):
    """Draws fine anti-copy interference lines (Payment type only)."""
    c.saveState()
    c.setStrokeColor(Color(0.0, 0.4, 0.3, alpha=0.05))
    c.setLineWidth(0.3)
    y = 20 * mm
    while y < h - 20 * mm:
        c.line(20 * mm, y, w - 20 * mm, y + 15 * mm)
        y += 4 * mm
    c.restoreState()


def draw_microtext_security(c, w, y_pos):
    """Renders tiny microtext security string inside margin boundaries."""
    c.saveState()
    c.setFillColor(HexColor('#888888'))
    c.setFont(SANS_FONT, 5.5)
    micro_str = "UNIYO AUTHENTIC CERTIFICATE • ETHIOPIAN HIGHER EDUCATION FRESHMAN HUB • VERIFY ONLINE • HIGH-SECURITY DOCUMENT"
    c.drawCentredString(w / 2.0, y_pos, micro_str)
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


def draw_barcode(c, text, x, y, width=44 * mm, height=14 * mm):
    """Renders a Code-128 barcode directly onto the canvas."""
    try:
        bc = code128.Code128(text, barHeight=height, barWidth=0.85)
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
# MAIN CERTIFICATE GENERATOR FUNCTION
# ==============================================================================

def generate_certificate_reportlab(certificate_data, qr_data_uri=None):
    """
    Generate PERFECT A4 PDF Certificate (210mm x 297mm Portrait)
    All elements fit strictly inside 15mm margins.
    """
    raw_type = certificate_data.get('certificate_type', 'completion').lower()
    
    # Normalize Certificate Types
    if 'vip' in raw_type:
        cert_type = 'vip'
    elif 'payment' in raw_type or 'paid' in raw_type:
        cert_type = 'payment'
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

    # 1. Canvas Setup - Exact A4 Portrait (210mm x 297mm)
    c = canvas.Canvas(
        str(output_pdf),
        pagesize=A4,  # w=210mm (595.28pt), h=297mm (841.89pt)
        pageCompression=0,  # No compression = max vector quality
        invariant=1
    )
    
    c.setTitle(f"UNIYO Certificate - {full_name}")
    c.setAuthor("UNIYO - Ethiopian Higher Education Freshman Hub")
    c.setSubject(f"{title} - {cert_type.upper()}")
    
    w, h = A4  # w = 210mm, h = 297mm
    
    # 2. Color Scheme Setup
    colors_map = {
        'vip': HexColor('#0B192C'),        # Deep Navy / Gold
        'completion': HexColor('#1E3A8A'), # Imperial Blue
        'payment': HexColor('#064E3B'),    # Emerald Green
        'promotion': HexColor('#7C2D12'),  # Warm Bronze
        'other': HexColor('#1F2937'),      # Slate Dark
    }
    primary_color = colors_map.get(cert_type, HexColor('#0B192C'))
    gold_color = HexColor('#C5A059')       # Muted Warm Gold

    # 3. Background & Security Patterns
    draw_parchment_background(c, w, h)
    
    if cert_type == 'vip':
        draw_smooth_gradient(c, 0, 0, w, h, Color(0.98, 0.88, 0.5, alpha=0.03), Color(0.7, 0.5, 0.1, alpha=0.03))
    elif cert_type == 'payment':
        draw_anti_copy_pattern(c, w, h)
        
    draw_watermark(c, w, h, "UNIYO")
    draw_guilloche_pattern(c, w, h, primary_color, gold_color)
    
    # 4. Borders (Strictly inside 15mm margins)
    # Outer Border at 15mm
    c.setStrokeColor(primary_color)
    c.setLineWidth(2.5)
    c.rect(15 * mm, 15 * mm, w - 30 * mm, h - 30 * mm, fill=False, stroke=True)
    
    # Inner Gold Border at 18mm
    c.setStrokeColor(gold_color)
    c.setLineWidth(1.2)
    c.rect(18 * mm, 18 * mm, w - 36 * mm, h - 36 * mm, fill=False, stroke=True)
    
    # Smooth Bézier Corner Filigrees
    draw_bezier_corners(c, w, h, primary_color, gold_color)

    # 5. TOP SECTION (Logo, Title, Subtitle)
    # Logo
    logo_file = BASE_DIR / 'static' / 'icons' / 'app_icon-192.png'
    if not draw_transparent_image(c, logo_file, (w / 2.0) - (8 * mm), h - 38 * mm, 16 * mm, 16 * mm):
        # Fallback Vector Shield Logo
        c.saveState()
        c.setFillColor(primary_color)
        c.rect((w / 2.0) - (7 * mm), h - 37 * mm, 14 * mm, 14 * mm, fill=True, stroke=False)
        c.restoreState()

    # Title
    c.setFillColor(primary_color)
    c.setFont(SERIF_BOLD, 20)
    c.drawCentredString(w / 2.0, h - 46 * mm, title.upper())
    
    # Subtitle
    c.setFillColor(HexColor('#555555'))
    c.setFont(SERIF_ITALIC, 10)
    c.drawCentredString(w / 2.0, h - 52 * mm, "Ethiopian Higher Education Freshman Hub")

    # 6. MIDDLE SECTION (Student Attestation & Name)
    c.setFillColor(HexColor('#666666'))
    c.setFont(SERIF_ITALIC, 11)
    c.drawCentredString(w / 2.0, h - 63 * mm, "This certificate is proudly presented to")

    # Student Name (Large, Prominent)
    c.setFillColor(primary_color)
    c.setFont(SERIF_BOLD, 24)
    c.drawCentredString(w / 2.0, h - 75 * mm, full_name)

    # Gold Accent Rule under Name
    c.setStrokeColor(gold_color)
    c.setLineWidth(1.5)
    name_w = max(c.stringWidth(full_name, SERIF_BOLD, 24) * 0.75, 90 * mm)
    c.line((w / 2.0) - (name_w / 2.0), h - 78 * mm, (w / 2.0) + (name_w / 2.0), h - 78 * mm)

    # Reason Text
    c.setFillColor(HexColor('#333333'))
    c.setFont(SERIF_FONT, 10)
    reason = "For successfully completing lessons and worksheets with dedication."
    if cert_type == 'vip':
        reason = "For achieving elite performance on the Monthly VIP Leaderboard."
    elif cert_type == 'payment':
        reason = "For official payment verification and academic portal clearance."
    elif cert_type == 'promotion':
        reason = "For academic promotion and scholarship excellence award."
    c.drawCentredString(w / 2.0, h - 87 * mm, reason)

    # Academic Details Strip
    details = university
    if stream:
        details += f" • {stream} Science"
    if sex:
        details += f" • {sex}"
    c.setFillColor(HexColor('#555555'))
    c.setFont(SANS_FONT, 9)
    c.drawCentredString(w / 2.0, h - 94 * mm, details)

    # 7. CREDENTIALS SECTION PANEL
    cred_top = h - 100 * mm
    c.setFillColor(HexColor('#FAF9F5'))
    c.setStrokeColor(primary_color)
    c.setLineWidth(1)
    c.roundRect(22 * mm, cred_top - 28 * mm, w - 44 * mm, 28 * mm, 3 * mm, fill=True, stroke=True)

    y_line = cred_top - 7 * mm
    c.setFont(SANS_FONT, 8.5)
    
    # Row 1
    c.setFillColor(HexColor('#555555'))
    c.drawString(28 * mm, y_line, "Certificate Number:")
    c.setFillColor(HexColor('#111111'))
    c.drawRightString(w - 28 * mm, y_line, cert_number)

    # Row 2
    y_line -= 6.5 * mm
    c.setFillColor(HexColor('#555555'))
    c.drawString(28 * mm, y_line, "Issue Date:")
    c.setFillColor(HexColor('#111111'))
    c.drawRightString(w - 28 * mm, y_line, str(issue_date)[:10])

    # Row 3
    y_line -= 6.5 * mm
    c.setFillColor(HexColor('#555555'))
    c.drawString(28 * mm, y_line, "Type:")
    c.setFillColor(primary_color)
    c.drawRightString(w - 28 * mm, y_line, cert_type.upper())

    # Verify URL Line
    y_line -= 6.5 * mm
    verify_url = f"https://uniyo-cloud.onrender.com/verify/{verification_token}"
    c.setFillColor(primary_color)
    c.setFont(SANS_BOLD, 7.5)
    c.drawCentredString(w / 2.0, y_line, f"Verify at: {verify_url}")

    # 8. BOTTOM SECTION (Signatures, Stamps, Barcode, QR Code, Microtext)
    
    # --- SIGNATURES (y = 125mm to 148mm) ---
    auth_dir = BASE_DIR / 'static' / 'Authenticity'
    
    # Super Admin Signature (Left)
    sig_sa_file = auth_dir / 'super_admin_signature.png'
    if not sig_sa_file.exists():
        sig_sa_file = auth_dir / 'super_admin.png'
        
    if cert_type == 'other':
        # Single Signature Centered
        sig_x = (w / 2.0) - (16 * mm)
        draw_transparent_image(c, sig_sa_file, sig_x, 134 * mm, 32 * mm, 12 * mm)
        c.setStrokeColor(HexColor('#999999'))
        c.setLineWidth(0.8)
        c.line((w / 2.0) - (20 * mm), 133 * mm, (w / 2.0) + (20 * mm), 133 * mm)
        c.setFont(SANS_BOLD, 8)
        c.setFillColor(HexColor('#111111'))
        c.drawCentredString(w / 2.0, 128 * mm, "Chalachew Agegn")
        c.setFont(SANS_FONT, 7)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(w / 2.0, 124 * mm, "Super Admin Director")
    else:
        # Dual Signatures
        # Super Admin (Left)
        draw_transparent_image(c, sig_sa_file, 24 * mm, 134 * mm, 30 * mm, 12 * mm)
        c.setStrokeColor(HexColor('#999999'))
        c.setLineWidth(0.8)
        c.line(22 * mm, 133 * mm, 58 * mm, 133 * mm)
        c.setFont(SANS_BOLD, 8)
        c.setFillColor(HexColor('#111111'))
        c.drawCentredString(40 * mm, 128 * mm, "Chalachew Agegn")
        c.setFont(SANS_FONT, 7)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(40 * mm, 124 * mm, "Super Admin Director")

        # Content Manager (Right)
        sig_cm_file = auth_dir / 'signature_(content_manager).png'
        if not sig_cm_file.exists():
            sig_cm_file = auth_dir / 'content_manager.png'
            
        draw_transparent_image(c, sig_cm_file, w - 54 * mm, 134 * mm, 30 * mm, 12 * mm)
        c.line(w - 58 * mm, 133 * mm, w - 22 * mm, 133 * mm)
        c.setFont(SANS_BOLD, 8)
        c.setFillColor(HexColor('#111111'))
        c.drawCentredString(w - 40 * mm, 128 * mm, "Banch Destaw")
        c.setFont(SANS_FONT, 7)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(w - 40 * mm, 124 * mm, "Content Manager")

    # --- STAMPS SYSTEM (y = 72mm to 112mm) ---
    # Determine Primary Stamp
    if cert_type == 'vip':
        rank_val = rank if (rank and 1 <= rank <= 5) else 1
        primary_stamp_file = auth_dir / f'vip{rank_val}.png'
    elif cert_type == 'payment':
        primary_stamp_file = auth_dir / 'paid.png'
    elif cert_type == 'promotion':
        primary_stamp_file = auth_dir / 'promotion.png'
    else:
        primary_stamp_file = auth_dir / 'general.png'

    secondary_stamp_file = auth_dir / 'super_admin_stamp.png'
    has_secondary = cert_type in ['vip', 'payment', 'promotion'] and secondary_stamp_file.exists()

    if has_secondary:
        # Primary Stamp Left of Center
        draw_transparent_image(c, primary_stamp_file, (w / 2.0) - (42 * mm), 72 * mm, 38 * mm, 38 * mm)
        # Secondary Stamp Right of Center
        draw_transparent_image(c, secondary_stamp_file, (w / 2.0) + (4 * mm), 72 * mm, 38 * mm, 38 * mm)
    else:
        # Single Primary Stamp Centered
        draw_transparent_image(c, primary_stamp_file, (w / 2.0) - (19 * mm), 72 * mm, 38 * mm, 38 * mm)

    # --- BARCODE (y = 42mm to 56mm, Centered) ---
    draw_barcode(c, cert_number, (w / 2.0) - (22 * mm), 42 * mm, width=44 * mm, height=14 * mm)

    # --- QR CODE (y = 22mm to 46mm, Bottom-Left) ---
    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=1)
        qr.add_data(verify_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color='black', back_color='white')
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        qr_image = ImageReader(qr_buffer)
        c.drawImage(qr_image, 22 * mm, 24 * mm, 22 * mm, 22 * mm, preserveAspectRatio=True)
        c.setFont(SANS_FONT, 6.5)
        c.setFillColor(HexColor('#666666'))
        c.drawCentredString(33 * mm, 20 * mm, "Scan to Verify")
    except Exception as e:
        print(f"Warning: QR Code Generation Failed: {e}")

    # --- MICROTEXT SECURITY LINE (y = 16mm, Bottom-Center) ---
    draw_microtext_security(c, w, 16 * mm)

    # 9. Save PDF Canvas
    c.showPage()
    c.save()
    
    return output_pdf