"""
UNIYO LMS - Common Certificate Utilities
Shared functions for certificate generation
"""

from pathlib import Path
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from core.paths import BASE_DIR

# Font names (fallback to Helvetica if custom fonts not available)
FONTS_DIR = BASE_DIR / 'assets' / 'fonts'

if FONTS_DIR.exists():
    try:
        pdfmetrics.registerFont(TTFont('AlexBrush', str(FONTS_DIR / 'AlexBrush-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('Cinzel', str(FONTS_DIR / 'Cinzel-Bold.ttf')))
        pdfmetrics.registerFont(TTFont('Montserrat', str(FONTS_DIR / 'Montserrat-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('Playfair', str(FONTS_DIR / 'PlayfairDisplay-Bold.ttf')))
        pdfmetrics.registerFont(TTFont('GreatVibes', str(FONTS_DIR / 'GreatVibes-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('Tangerine', str(FONTS_DIR / 'Tangerine-Bold.ttf')))
    except:
        pass

# Font constants with fallbacks
registered_fonts = pdfmetrics.getRegisteredFontNames()

SANS_FONT = 'Montserrat' if 'Montserrat' in registered_fonts else 'Helvetica'
SANS_BOLD = 'Montserrat-Bold' if 'Montserrat-Bold' in registered_fonts else 'Helvetica-Bold'
SERIF_FONT = 'Playfair' if 'Playfair' in registered_fonts else 'Times-Roman'
SERIF_BOLD = 'Playfair' if 'Playfair' in registered_fonts else 'Times-Bold'
SERIF_ITALIC = 'Times-Italic'
SCRIPT_FONT = 'AlexBrush' if 'AlexBrush' in registered_fonts else 'Helvetica'

def resolve_certificate_meta(certificate_data):
    """Resolve certificate type metadata (colors, titles, stamps)"""
    cert_type = certificate_data.get('certificate_type', 'completion').lower()
    
    meta = {
        'category': 'other',
        'title': 'Certificate of Recognition',
        'subtitle': 'Ethiopian Higher Education Freshman Hub',
        'primary_color': HexColor('#6D28D9'),
        'gold_color': HexColor('#C5A059'),
        'primary_stamp': 'general.png',
        'secondary_stamp': 'super_admin_stamp.png',
        'reason': 'In recognition of your achievement.'
    }
    
    if 'vip' in cert_type or 'leaderboard' in cert_type:
        meta.update({
            'category': 'vip',
            'title': 'VIP Monthly Leadership Award',
            'subtitle': 'Outstanding Performance in VIP Competition',
            'primary_color': HexColor('#F59E0B'),
            'gold_color': HexColor('#D4AF37'),
            'primary_stamp': 'vip1.png',
            'secondary_stamp': 'super_admin_stamp.png',
            'reason': 'For outstanding performance in the VIP Monthly Competition.'
        })
    elif 'promotion' in cert_type:
        meta.update({
            'category': 'promotion',
            'title': 'Promotion Certificate',
            'subtitle': 'Outstanding Contribution to UNIYO',
            'primary_color': HexColor('#F97316'),
            'gold_color': HexColor('#C5A059'),
            'primary_stamp': 'promotion.png',
            'secondary_stamp': 'super_admin_stamp.png',
            'reason': 'In recognition of outstanding contribution to promoting UNIYO.'
        })
    elif 'payment' in cert_type or 'paid' in cert_type or 'receipt' in cert_type:
        meta.update({
            'category': 'payment',
            'title': 'Payment Receipt',
            'subtitle': 'Office of Student Accounts',
            'primary_color': HexColor('#14B8A6'),
            'gold_color': HexColor('#C5A059'),
            'primary_stamp': 'paid.png',
            'secondary_stamp': 'super_admin_stamp.png',
            'reason': 'For payment of UNIYO Premium Subscription.'
        })
    elif 'completion' in cert_type:
        meta.update({
            'category': 'completion',
            'title': 'Certificate of Completion',
            'subtitle': 'Ethiopian Higher Education Freshman Hub',
            'primary_color': HexColor('#4B0082'),
            'gold_color': HexColor('#C5A059'),
            'primary_stamp': 'general.png',
            'secondary_stamp': None,
            'reason': 'For successfully completing all lessons and worksheets.'
        })
    elif 'excellence' in cert_type:
        meta.update({
            'category': 'excellence',
            'title': 'Certificate of Excellence',
            'subtitle': 'Outstanding Academic Achievement',
            'primary_color': HexColor('#D4AF37'),
            'gold_color': HexColor('#C5A059'),
            'primary_stamp': 'super_admin_stamp.png',
            'secondary_stamp': None,
            'reason': 'For outstanding academic excellence.'
        })
    
    return meta

def find_stamp_file(stamp_name):
    """Find stamp file in Authenticity folder"""
    if not stamp_name:
        return None
    auth_dir = BASE_DIR / 'static' / 'Authenticity'
    stamp_path = auth_dir / stamp_name
    if stamp_path.exists():
        return str(stamp_path)
    # Fallback to assets/certificates/stamps
    alt_dir = BASE_DIR / 'assets' / 'certificates' / 'stamps'
    alt_path = alt_dir / stamp_name
    if alt_path.exists():
        return str(alt_path)
    return None

def find_signature_file(sig_name):
    """Find signature file in Authenticity folder"""
    auth_dir = BASE_DIR / 'static' / 'Authenticity'
    sig_path = auth_dir / sig_name
    if sig_path.exists():
        return str(sig_path)
    return None

def draw_transparent_image(c, image_path, x, y, width, height):
    """Draw image with transparency mask"""
    if image_path and Path(image_path).exists():
        try:
            img = ImageReader(str(image_path))
            c.drawImage(img, x, y, width, height, preserveAspectRatio=True, mask='auto')
            return True
        except:
            pass
    return False

def draw_parchment_background(c, w, h, bg_hex='#FAF7F0'):
    """Draw parchment-style background"""
    c.setFillColor(HexColor(bg_hex))
    c.rect(0, 0, w, h, fill=True, stroke=False)

def draw_watermark(c, w, h, text="UNIYO", font_size=60, alpha=0.04):
    """Draw diagonal watermark"""
    c.saveState()
    c.translate(w/2, h/2)
    c.rotate(35)
    c.setFillColor(HexColor('#4B0082'))
    c.setFillAlpha(alpha)
    c.setFont(SERIF_BOLD if SERIF_BOLD != 'Helvetica-Bold' else 'Helvetica-Bold', font_size)
    c.drawCentredString(0, 0, text)
    c.setFillAlpha(1)
    c.restoreState()

def draw_anti_copy_pattern(c, w, h, margin_mm=15):
    """Draw anti-copy pattern"""
    m = margin_mm * mm
    c.saveState()
    c.setStrokeColor(HexColor('#CCCCCC'))
    c.setStrokeAlpha(0.1)
    c.setLineWidth(0.3)
    step = 5 * mm
    x = m
    while x < w - m:
        c.line(x, m, x, h - m)
        x += step
    y = m
    while y < h - m:
        c.line(m, y, w - m, y)
        y += step
    c.restoreState()

def draw_guilloche_pattern(c, w, h, color, margin_mm=15, count=14):
    """Draw guilloche pattern (concentric lines)"""
    m = margin_mm * mm
    c.saveState()
    c.setStrokeColor(color)
    c.setStrokeAlpha(0.03)
    c.setLineWidth(0.3)
    for i in range(count):
        offset = i * 1.5 * mm
        c.rect(m + offset, m + offset, w - 2*m - 2*offset, h - 2*m - 2*offset, fill=False, stroke=True)
    c.restoreState()

def draw_bezier_corners(c, w, h, color, margin_mm=15, corner_size_mm=22):
    """Draw decorative bezier corners"""
    m = margin_mm * mm
    size = corner_size_mm * mm
    c.setStrokeColor(color)
    c.setLineWidth(1.5)
    
    # Top-left
    c.line(m, h - m - size, m, h - m)
    c.line(m, h - m, m + size, h - m)
    c.arc(m, h - m - size, m + size, h - m, 90, 180)
    
    # Top-right
    c.line(w - m - size, h - m, w - m, h - m)
    c.line(w - m, h - m, w - m, h - m - size)
    c.arc(w - m - size, h - m - size, w - m, h - m, 0, 90)
    
    # Bottom-left
    c.line(m, m + size, m, m)
    c.line(m, m, m + size, m)
    c.arc(m, m, m + size, m + size, 180, 270)
    
    # Bottom-right
    c.line(w - m - size, m, w - m, m)
    c.line(w - m, m, w - m, m + size)
    c.arc(w - m - size, m, w - m, m + size, 270, 360)

def draw_sparkle_particles(c, w, h, gold_color):
    """Draw sparkle particles for VIP certificates"""
    import random
    c.saveState()
    c.setFillColor(gold_color)
    c.setFillAlpha(0.3)
    random.seed(42)  # Reproducible sparkles
    for _ in range(30):
        x = random.uniform(30*mm, w - 30*mm)
        y = random.uniform(30*mm, h - 30*mm)
        size = random.uniform(0.5, 1.5) * mm
        c.circle(x, y, size, fill=True, stroke=False)
    c.restoreState()

def draw_holographic_shimmer(c, w, h):
    """Draw holographic shimmer effect"""
    c.saveState()
    c.setStrokeColor(Color(1, 1, 1, alpha=0.05))
    c.setLineWidth(2)
    for i in range(0, int(w), 20):
        c.line(i, 0, i - 50, h)
    c.restoreState()

def draw_smooth_gradient(c, x, y, width, height, color1, color2):
    """Draw smooth gradient fill"""
    steps = 50
    for i in range(steps):
        ratio = i / steps
        r = color1.red + (color2.red - color1.red) * ratio
        g = color1.green + (color2.green - color1.green) * ratio
        b = color1.blue + (color2.blue - color1.blue) * ratio
        alpha = color1.alpha + (color2.alpha - color1.alpha) * ratio
        c.setFillColor(Color(r, g, b, alpha=alpha))
        segment_height = height / steps
        c.rect(x, y + i * segment_height, width, segment_height, fill=True, stroke=False)

def draw_barcode(c, data, x, y, width=42*mm, height=12*mm):
    """Draw simple barcode"""
    import random
    c.saveState()
    c.setFillColor(HexColor('#000000'))
    random.seed(data if isinstance(data, str) else str(data))
    bar_x = x
    total_width = 0
    while total_width < width:
        bar_w = random.choice([1, 2]) * 0.4 * mm
        c.rect(bar_x, y, bar_w, height, fill=True, stroke=False)
        bar_x += bar_w + 0.3 * mm
        total_width += bar_w + 0.3 * mm
    c.restoreState()
