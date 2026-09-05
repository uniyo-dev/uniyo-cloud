"""Completion & Other Certificate Generator - A4 Portrait (210mm x 297mm)"""
from .common import *

# ==============================================================================
# 3. A4 PORTRAIT CERTIFICATE GENERATOR (210mm × 297mm — COMPLETION & OTHER)
# ==============================================================================

def generate_a4_portrait_certificate_reportlab(certificate_data, qr_data_uri=None):
    """
    Generates a 100% compliant A4 PORTRAIT Certificate (210mm x 297mm).
    Used for Completion and Other Certificate Types.
    DOUBLED STAMP SIZES (54mm).
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
        pageCompression=0,
        invariant=1
    )
    
    c.setTitle(f"UNIYO Certificate - {full_name}")
    c.setAuthor("UNIYO - Ethiopian Higher Education Freshman Hub")
    c.setSubject(f"{meta['title']} - {meta['category'].upper()}")
    
    w, h = A4  # 210mm x 297mm
    m = 15 * mm  # Strict 15mm margin
    
    primary_color = meta['primary_color']
    gold_color = meta['gold_color']

    # 1. Background & Security Layers
    draw_parchment_background(c, w, h, bg_hex='#FAF7F0')
    draw_watermark(c, w, h, "UNIYO")
    draw_guilloche_pattern(c, w, h, primary_color, margin_mm=15, count=14)

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

    # 4. Middle Section
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

    # 5. Credentials Box
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

    # ==========================================================================
    # 6. STAMPS SYSTEM (EQUAL SIZE, DOUBLED TO 52mm, CENTERED AT BOTTOM)
    # ==========================================================================
    stamp_size = 52 * mm  # Doubled Stamp Size for A4 Portrait
    
    primary_stamp_path = find_stamp_file(meta['primary_stamp'])
    draw_transparent_image(c, primary_stamp_path, (w / 2.0) - (stamp_size / 2.0), 38 * mm, stamp_size, stamp_size)

    # 7. Signatures System
    sig_y = 88 * mm
    sig_sa_file = find_signature_file('super_admin_signature.png')

    if meta['dual_signatures']:
        sig_cm_file = find_signature_file('signature_(content_manager).png')
        
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

        draw_transparent_image(c, sig_cm_file, w - m - 44 * mm, sig_y + 5 * mm, 30 * mm, 12 * mm)
        c.line(w - m - 44 * mm, sig_y + 5 * mm, w - m - 8 * mm, sig_y + 5 * mm)
        c.setFont(SANS_BOLD, 8)
        c.setFillColor(HexColor('#111111'))
        c.drawString(w - m - 44 * mm, sig_y + 0.5 * mm, "Banch Destaw")
        c.setFont(SANS_FONT, 7)
        c.setFillColor(HexColor('#666666'))
        c.drawString(w - m - 44 * mm, sig_y - 3.5 * mm, "Content Manager")
    else:
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

    # 8. QR Code & Barcode
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

    c.setFillColor(HexColor('#888888'))
    c.setFont(SANS_FONT, 5.5)
    c.drawCentredString(w / 2.0, m + 1.5 * mm,
                        "UNIYO AUTHENTIC CERTIFICATE • ETHIOPIAN HIGHER EDUCATION FRESHMAN HUB • VERIFY ONLINE • TAMPER EVIDENT")

    c.showPage()
    c.save()
    return output_pdf

