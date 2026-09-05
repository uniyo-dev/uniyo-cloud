"""VIP & Promotion Certificate Generator - A4 Landscape (297mm x 210mm)"""
from .common import *

# ==============================================================================
# 2. A4 LANDSCAPE CERTIFICATE GENERATOR (297mm × 210mm — VIP & PROMOTION)
# ==============================================================================

def generate_a4_landscape_certificate_reportlab(certificate_data, qr_data_uri=None):
    """
    Generates a 100% compliant A4 LANDSCAPE Certificate (297mm x 210mm).
    DOUBLED STAMP SIZES (56mm), EQUAL SIZES, 35% HEIGHT SECONDARY STAMP PLACEMENT.
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

    c = canvas.Canvas(
        str(output_pdf),
        pagesize=landscape(A4),
        pageCompression=0,
        invariant=1
    )
    
    c.setTitle(f"UNIYO Certificate - {full_name}")
    c.setAuthor("UNIYO - Ethiopian Higher Education Freshman Hub")
    c.setSubject(f"{meta['title']} - {meta['category'].upper()}")
    
    w, h = landscape(A4) # 297mm x 210mm
    m = 15 * mm  # Strict 15mm margin
    
    primary_color = meta['primary_color']
    gold_color = meta['gold_color']

    # 1. Background & Security Layers
    draw_parchment_background(c, w, h, bg_hex='#FAF7F0')
    draw_watermark(c, w, h, "UNIYO")
    draw_anti_copy_pattern(c, w, h, margin_mm=15)
    draw_guilloche_pattern(c, w, h, primary_color, margin_mm=15, count=14)

    if meta['category'] == 'vip':
        draw_sparkle_particles(c, w, h, gold_color)
    if meta['category'] in ['vip', 'promotion']:
        draw_holographic_shimmer(c, w, h)

    # 2. Double Borders
    c.setStrokeColor(primary_color)
    c.setLineWidth(2.5)
    c.rect(m, m, w - (2 * m), h - (2 * m), fill=False, stroke=True)
    
    c.setStrokeColor(gold_color)
    c.setLineWidth(1.2)
    c.rect(m + 3 * mm, m + 3 * mm, w - (2 * m) - 6 * mm, h - (2 * m) - 6 * mm, fill=False, stroke=True)

    draw_bezier_corners(c, w, h, gold_color, margin_mm=15, corner_size_mm=22)

    # 3. Top Section
    logo_file = BASE_DIR / 'static' / 'icons' / 'app_icon-192.png'
    draw_transparent_image(c, logo_file, m + 12 * mm, h - m - 24 * mm, 18 * mm, 18 * mm)

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

    draw_smooth_gradient(c, (w / 2.0) - 90 * mm, h - m - 32 * mm, 180 * mm, 12 * mm,
                         Color(0.98, 0.88, 0.5, alpha=0.03), Color(0.7, 0.5, 0.1, alpha=0.03))

    c.setFillColor(primary_color)
    c.setFont(SERIF_BOLD, 22)
    c.drawCentredString(w / 2.0, h - m - 28 * mm, meta['title'])
    
    c.setFillColor(HexColor('#555555'))
    c.setFont(SERIF_ITALIC, 10)
    c.drawCentredString(w / 2.0, h - m - 34 * mm, meta['subtitle'])

    # 4. Middle Section
    c.setFillColor(HexColor('#666666'))
    c.setFont(SERIF_ITALIC, 11)
    c.drawCentredString(w / 2.0, h - m - 46 * mm, "This certificate is proudly presented to")

    c.setFillColor(primary_color)
    c.setFont(SERIF_BOLD, 28)
    c.drawCentredString(w / 2.0, h - m - 58 * mm, full_name)

    c.setStrokeColor(gold_color)
    c.setLineWidth(1.8)
    name_w = max(c.stringWidth(full_name, SERIF_BOLD, 28) * 0.75, 110 * mm)
    c.line((w / 2.0) - (name_w / 2.0), h - m - 61 * mm, (w / 2.0) + (name_w / 2.0), h - m - 61 * mm)

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

    stream_str = f"{stream} Science" if not str(stream).endswith('Science') else stream
    meta_str = f"{university}   •   {stream_str}   •   Sex: {sex}"
    c.setFont(SERIF_ITALIC, 9.5)
    c.setFillColor(gold_color)
    c.drawCentredString(w / 2.0, h - m - 88 * mm, meta_str)

    # 5. Credentials Panel
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

    # ==========================================================================
    # 6. STAMPS SYSTEM (EQUAL SIZE, DOUBLED TO 54mm, 35% HEIGHT SECONDARY PLACEMENT)
    # ==========================================================================
    stamp_size = 54 * mm  # Doubled Stamp Size for A4 Landscape
    
    primary_stamp_path = find_stamp_file(meta['primary_stamp'])
    sec_stamp_path = find_stamp_file(meta['secondary_stamp'])
    
    # Primary Stamp: Horizontally Centered at Bottom
    primary_stamp_x = (w / 2.0) - (stamp_size / 2.0)
    primary_stamp_y = m + 4 * mm
    draw_transparent_image(c, primary_stamp_path, primary_stamp_x, primary_stamp_y, stamp_size, stamp_size)
    
    # Secondary Stamp: Positioned at 35% Height from Bottom on the Right Side
    secondary_stamp_x = w - m - stamp_size - 12 * mm
    secondary_stamp_y = h * 0.35  # Exactly 35% from bottom
    draw_transparent_image(c, sec_stamp_path, secondary_stamp_x, secondary_stamp_y, stamp_size, stamp_size)

    # 7. Signatures System (Bottom Right Area)
    sig_sa_file = find_signature_file('super_admin_signature.png')
    sig_cm_file = find_signature_file('signature_(content_manager).png')

    sig1_x = w - m - 68 * mm
    sig2_x = w - m - 34 * mm
    sig_y = m + 8 * mm

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

    draw_transparent_image(c, sig_sa_file, sig2_x, sig_y + 8 * mm, 28 * mm, 14 * mm)
    c.line(sig2_x, sig_y + 8 * mm, sig2_x + 28 * mm, sig_y + 8 * mm)
    c.setFont(SANS_BOLD, 6.5)
    c.setFillColor(HexColor("#0F172A"))
    c.drawString(sig2_x, sig_y + 3.5 * mm, "Dr. Solomon Tadesse")
    c.setFont(SANS_FONT, 5.5)
    c.setFillColor(HexColor("#64748B"))
    c.drawString(sig2_x, sig_y - 0.5 * mm, "Super Admin Director")

    # 8. QR Code & Barcode
    bottom_y = m + 5 * mm
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

    draw_barcode(c, cert_number, m + 42 * mm, bottom_y + 12 * mm, width=42 * mm, height=12 * mm)

    c.setFillColor(HexColor('#888888'))
    c.setFont(SANS_FONT, 5.5)
    c.drawCentredString(w / 2.0, m + 1.0 * mm,
                        "UNIYO AUTHENTIC CERTIFICATE • ETHIOPIAN HIGHER EDUCATION FRESHMAN HUB • VERIFY ONLINE • TAMPER EVIDENT")

    c.showPage()
    c.save()
    return output_pdf

