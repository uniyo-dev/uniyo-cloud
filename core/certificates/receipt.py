"""Payment Receipt Generator - A6 Portrait (105mm x 148mm)"""
from .common import *

# ==============================================================================
# 1. A6 PORTRAIT PAYMENT RECEIPT GENERATOR (105mm × 148mm)
# ==============================================================================

def generate_payment_receipt_reportlab(certificate_data, qr_data_uri=None):
    """
    Generates a 100% compliant A6 Portrait Payment Receipt (105mm x 148mm).
    FIXED: Barcode strictly inside 8mm border, doubled stamp size, 35% height secondary stamp placement.
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

    c = canvas.Canvas(
        str(output_pdf),
        pagesize=A6,
        pageCompression=0,
        invariant=1
    )
    
    c.setTitle(f"UNIYO Payment Receipt - {full_name}")
    c.setAuthor("UNIYO LMS Financial System")
    c.setSubject("Official Payment Receipt - A6 Portrait")
    
    w, h = A6  # 105mm x 148mm
    m = 8 * mm # Strict 8mm Margin
    
    primary_color = meta['primary_color']
    gold_color = meta['gold_color']

    # 1. Background & Security
    draw_parchment_background(c, w, h, bg_hex='#FAF7F0')
    draw_watermark(c, w, h, "UNIYO PAID")
    draw_anti_copy_pattern(c, w, h, margin_mm=8)
    draw_guilloche_pattern(c, w, h, primary_color, margin_mm=8, count=4)

    # 2. Outer & Inner Borders
    c.setStrokeColor(primary_color)
    c.setLineWidth(1.5)
    c.rect(m, m, w - (2 * m), h - (2 * m), fill=False, stroke=True)
    
    c.setStrokeColor(gold_color)
    c.setLineWidth(0.8)
    c.rect(m + 1.5 * mm, m + 1.5 * mm, w - (2 * m) - 3 * mm, h - (2 * m) - 3 * mm, fill=False, stroke=True)

    draw_bezier_corners(c, w, h, gold_color, margin_mm=8, corner_size_mm=10)

    # 3. Header Section
    logo_file = BASE_DIR / 'static' / 'icons' / 'app_icon-192.png'
    draw_transparent_image(c, logo_file, (w / 2.0) - (5 * mm), h - m - 11 * mm, 10 * mm, 10 * mm)

    c.setFillColor(primary_color)
    c.setFont(SERIF_BOLD, 11)
    c.drawCentredString(w / 2.0, h - m - 15 * mm, meta['title'])
    
    c.setFillColor(HexColor('#555555'))
    c.setFont(SANS_FONT, 6)
    c.drawCentredString(w / 2.0, h - m - 18.5 * mm, meta['subtitle'])

    # 4. Receipt Metadata
    y_pos = h - m - 23 * mm
    c.setFont(SANS_BOLD, 6.5)
    c.setFillColor(primary_color)
    c.drawString(m + 3 * mm, y_pos, f"Receipt: {cert_number}")
    c.setFont(SANS_FONT, 6.5)
    c.setFillColor(HexColor('#333333'))
    c.drawRightString(w - m - 3 * mm, y_pos, f"Date: {str(issue_date)[:10]}")
    
    y_pos -= 2.5 * mm
    c.setStrokeColor(HexColor('#CBD5E1'))
    c.setLineWidth(0.5)
    c.line(m + 2.5 * mm, y_pos, w - m - 2.5 * mm, y_pos)

    # 5. Customer Details
    y_pos -= 4 * mm
    c.setFont(SANS_BOLD, 6)
    c.setFillColor(primary_color)
    c.drawString(m + 3 * mm, y_pos, "RECEIVED FROM:")
    
    y_pos -= 4 * mm
    c.setFont(SERIF_BOLD, 9.5)
    c.setFillColor(HexColor('#111111'))
    c.drawString(m + 3 * mm, y_pos, full_name)
    
    y_pos -= 3.5 * mm
    c.setFont(SANS_FONT, 6.5)
    c.setFillColor(HexColor('#444444'))
    c.drawString(m + 3 * mm, y_pos, f"{university}  •  Ph: {phone}")

    # 6. Financial Box
    box_top = y_pos - 3 * mm
    box_h = 25 * mm
    box_w = w - (2 * m) - 4 * mm
    box_x = m + 2 * mm
    
    c.setFillColor(HexColor('#F0FDF4'))
    c.setStrokeColor(primary_color)
    c.setLineWidth(0.8)
    c.roundRect(box_x, box_top - box_h, box_w, box_h, 2 * mm, fill=True, stroke=True)

    b_y = box_top - 5.5 * mm
    c.setFont(SANS_BOLD, 10.5)
    c.setFillColor(primary_color)
    c.drawString(box_x + 3 * mm, b_y, f"AMOUNT: {amount_paid}")
    
    c.setFont(SANS_BOLD, 8.5)
    c.setFillColor(HexColor('#16A34A'))
    c.drawRightString(box_x + box_w - 3 * mm, b_y, "✓ PAID")

    b_y -= 5 * mm
    c.setFont(SANS_FONT, 6.5)
    c.setFillColor(HexColor('#333333'))
    c.drawString(box_x + 3 * mm, b_y, f"Method: {payment_method}")
    c.drawRightString(box_x + box_w - 3 * mm, b_y, f"Trans: {transaction_id}")

    b_y -= 5 * mm
    c.setFont(SANS_BOLD, 7)
    c.setFillColor(primary_color)
    c.drawString(box_x + 3 * mm, b_y, f"Subscription: {subscription_plan}")

    b_y -= 4.5 * mm
    verify_url = f"https://uniyo-cloud.onrender.com/verify/{verification_token}"
    c.setFont(SANS_FONT, 5.5)
    c.setFillColor(HexColor('#555555'))
    c.drawString(box_x + 3 * mm, b_y, f"Verify: {verify_url[:40]}...")

    # ==========================================================================
    # 7. STAMPS SYSTEM (EQUAL SIZE, DOUBLED TO 30mm, 35% HEIGHT SECONDARY PLACEMENT)
    # ==========================================================================
    stamp_size = 28 * mm  # Doubled stamp size for A6
    
    paid_stamp = find_stamp_file(meta['primary_stamp'])
    admin_stamp = find_stamp_file(meta['secondary_stamp'])
    
    # Primary Stamp: Horizontally Centered at Bottom
    primary_stamp_x = (w / 2.0) - (stamp_size / 2.0)
    primary_stamp_y = 22 * mm
    draw_transparent_image(c, paid_stamp, primary_stamp_x, primary_stamp_y, stamp_size, stamp_size)
    
    # Secondary Stamp: Positioned at 35% Height from Bottom toward the Right
    secondary_stamp_x = w - m - stamp_size - 1.5 * mm
    secondary_stamp_y = h * 0.35  # Exactly 35% from bottom
    draw_transparent_image(c, admin_stamp, secondary_stamp_x, secondary_stamp_y, stamp_size, stamp_size)

    # 8. Signatures
    sig_sa = find_signature_file('super_admin_signature.png')
    sig_cm = find_signature_file('signature_(content_manager).png')
    
    sig_y = 48 * mm
    
    # Super Admin (Left)
    draw_transparent_image(c, sig_sa, m + 2 * mm, sig_y + 3 * mm, 16 * mm, 7 * mm)
    c.setStrokeColor(HexColor('#999999'))
    c.setLineWidth(0.5)
    c.line(m + 2 * mm, sig_y + 3 * mm, m + 20 * mm, sig_y + 3 * mm)
    c.setFont(SANS_BOLD, 5.5)
    c.setFillColor(HexColor('#111111'))
    c.drawString(m + 2 * mm, sig_y, "Chalachew Agegn")
    c.setFont(SANS_FONT, 4.5)
    c.setFillColor(HexColor('#666666'))
    c.drawString(m + 2 * mm, sig_y - 2.5 * mm, "Super Admin")

    # Content Manager (Right)
    draw_transparent_image(c, sig_cm, w - m - 20 * mm, sig_y + 3 * mm, 16 * mm, 7 * mm)
    c.line(w - m - 20 * mm, sig_y + 3 * mm, w - m - 2 * mm, sig_y + 3 * mm)
    c.setFont(SANS_BOLD, 5.5)
    c.setFillColor(HexColor('#111111'))
    c.drawString(w - m - 20 * mm, sig_y, "Banch Destaw")
    c.setFont(SANS_FONT, 4.5)
    c.setFillColor(HexColor('#666666'))
    c.drawString(w - m - 20 * mm, sig_y - 2.5 * mm, "Content Manager")

    # ==========================================================================
    # 9. BOTTOM FOOTER AREA (QR, BARCODE, MICROTEXT — STRICTLY INSIDE 8mm BORDER)
    # ==========================================================================
    # [A] Microtext: Printed at 9.5mm from bottom (1.5mm SAFELY inside 8mm margin)
    c.setFillColor(HexColor('#888888'))
    c.setFont(SANS_FONT, 4.2)
    c.drawCentredString(w / 2.0, 9.5 * mm, "UNIYO OFFICIAL PAYMENT RECEIPT • TAMPER EVIDENT FINANCIAL RECORD • VERIFY ONLINE")

    # [B] Code-128 Barcode: Centered at x=38.5mm, y=12mm (Sits cleanly between 12mm and 19mm)
    draw_barcode(c, cert_number, (w / 2.0) - (14 * mm), 12 * mm, width=28 * mm, height=7 * mm)

    # [C] QR Code: Bottom Left at x=10mm, y=22mm (13mm x 13mm)
    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=1)
        qr.add_data(verify_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color='black', back_color='white')
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        qr_image = ImageReader(qr_buffer)
        c.drawImage(qr_image, m + 2 * mm, 22 * mm, 13 * mm, 13 * mm, mask='auto')
    except Exception as e:
        print(f"Warning: QR Code Generation Failed: {e}")

    # Save PDF Canvas
    c.showPage()
    c.save()
    return output_pdf

