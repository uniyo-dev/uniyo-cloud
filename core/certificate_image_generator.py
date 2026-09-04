"""
UNIYO LMS - Certificate Image Generator (Enhanced)
Converts HTML certificate to PNG/JPG using Playwright
Features: Museum Quality + Banknote Security + NFT Digital Feel
"""

import os
from pathlib import Path
from datetime import datetime

from core.paths import CERTIFICATES_DIR, BASE_DIR
from core.helpers import logger

# ============================================
# CERTIFICATE IMAGE GENERATION
# ============================================

def generate_certificate_image(certificate_data, qr_data_uri):
    """Generate certificate as PNG with all security features (SYNC version)"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error("Playwright not installed")
        return None
    
    cert_number = certificate_data.get('certificate_number', 'UNKNOWN')
    cert_id = cert_number.replace('/', '_').replace('\\', '_')
    output_path = CERTIFICATES_DIR / f"{cert_id}.png"
    
    html_content = build_certificate_html(certificate_data, qr_data_uri)
    
    temp_html = CERTIFICATES_DIR / f"temp_{cert_id}.html"
    temp_html.write_text(html_content, encoding='utf-8')
    
    try:
        # Set dimensions based on certificate type
        cert_type = certificate_data.get('certificate_type', 'completion')
        if cert_type == 'payment':
            viewport_width = 1240   # A6 at 300 DPI
            viewport_height = 1748  # A6 at 300 DPI
        else:
            viewport_width = 2480   # A4 at 300 DPI
            viewport_height = 3508  # A4 at 300 DPI
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': viewport_width, 'height': viewport_height})
            page.goto(f'file://{temp_html}')
            page.wait_for_timeout(2000)
            page.screenshot(path=str(output_path), full_page=True, type='png')
            browser.close()
        
        temp_html.unlink(missing_ok=True)
        return output_path
    
    except Exception as e:
        logger.error(f"Error generating certificate image: {e}")
        temp_html.unlink(missing_ok=True)
        return None


def build_certificate_html(certificate_data, qr_data_uri, logo_path=None, verification_url=None):
    """Build enhanced HTML with all security features"""
    
    from core.paths import BASE_DIR
    if logo_path is None:
        logo_path = str(BASE_DIR / 'static' / 'images' / 'logo.svg')
    if verification_url is None:
        verification_url = certificate_data.get('verification_url', 'https://uniyo-cloud.onrender.com/verify')
    
    full_name = certificate_data.get('full_name', '')
    sex = certificate_data.get('sex', '')
    university = certificate_data.get('university', '')
    stream = certificate_data.get('stream', '')
    cert_number = certificate_data.get('certificate_number', '')
    cert_type = certificate_data.get('certificate_type', 'completion')
    title = certificate_data.get('title', 'Certificate')
    issue_date = certificate_data.get('issue_date', '')
    rank = certificate_data.get('rank', None)
    
    # ============================================
    # TYPE-SPECIFIC CONFIGURATIONS
    # ============================================
    
    if cert_type == 'vip_leaderboard':
        primary_color = '#F59E0B'
        secondary_color = '#B45309'
        accent_color = '#FCD34D'
        bg_gradient = 'linear-gradient(135deg, #fffdf9 0%, #fffbeb 25%, #fff8e1 50%, #fffbeb 75%, #fffdf9 100%)'
        title_text = 'OFFICIAL VIP MONTHLY LEADERSHIP AWARD'
        has_gold_foil = True
        has_sparkles = True
        has_color_shift = True
        border_style = 'double'
    # Stamp configuration (based on certificate type)
    from core.paths import BASE_DIR
    auth_dir = BASE_DIR / 'static' / 'Authenticity'
    
    if cert_type == 'vip_leaderboard':
        # VIP: Primary = rank-specific, Secondary = super_admin_stamp
        vip_rank = rank if rank and rank <= 5 else 1
        primary_stamp = str(auth_dir / f'vip{vip_rank}.png')
        secondary_stamp = str(auth_dir / 'super_admin_stamp.png')
        has_secondary_stamp = True
    elif cert_type == 'payment':
        # Payment: Primary = paid.png (ecliptical), Secondary = super_admin_stamp
        primary_stamp = str(auth_dir / 'paid.png')
        secondary_stamp = str(auth_dir / 'super_admin_stamp.png')
        has_secondary_stamp = True
    elif cert_type == 'promotion':
        # Promotion: Primary = promotion.png, Secondary = super_admin_stamp
        primary_stamp = str(auth_dir / 'promotion.png')
        secondary_stamp = str(auth_dir / 'super_admin_stamp.png')
        has_secondary_stamp = True
    elif cert_type in ['other', 'excellence', 'content_creator', 'marketing_manager', 'advertiser', 'staff', 'special_congratulations', 'participation', 'appreciation', 'congratulations']:
        # Other: Primary = super_admin_stamp only
        primary_stamp = str(auth_dir / 'super_admin_stamp.png')
        secondary_stamp = None
        has_secondary_stamp = False
    else:
        # Completion (lessons/worksheets): Primary = general.png
        primary_stamp = str(auth_dir / 'general.png')
        secondary_stamp = None
        has_secondary_stamp = False
    
    # Signature files
    super_admin_signature = str(auth_dir / 'super_admin_signature.png')
    super_admin_name = str(auth_dir / 'chalalchew_agegn_(super_admin_name).png')
    content_manager_signature = str(auth_dir / 'signature_(content_manager).png')
    content_manager_name = str(auth_dir / 'banch_destaw_(content_manager_name).png')
    
    if cert_type == 'payment':
        primary_color = '#14B8A6'
        secondary_color = '#0D9488'
        accent_color = '#5EEAD4'
        bg_gradient = 'linear-gradient(135deg, #fffdf9 0%, #f0fdf4 25%, #ecfdf5 50%, #f0fdf4 75%, #fffdf9 100%)'
        title_text = 'PAYMENT RECEIPT'
        has_gold_foil = False
        has_sparkles = False
        has_color_shift = False
        border_style = 'solid'
    elif cert_type == 'promotion':
        primary_color = '#F97316'
        secondary_color = '#C2410C'
        accent_color = '#FDBA74'
        bg_gradient = 'linear-gradient(135deg, #fffdf9 0%, #fef3c7 25%, #fffbeb 50%, #fef3c7 75%, #fffdf9 100%)'
        title_text = 'PROMOTION CERTIFICATE'
        has_gold_foil = False
        has_sparkles = True
        has_color_shift = False
        border_style = 'solid'
    elif cert_type == 'other':
        primary_color = '#38BDF8'
        secondary_color = '#0284C7'
        accent_color = '#7DD3FC'
        bg_gradient = 'linear-gradient(135deg, #fffdf9 0%, #eff6ff 25%, #f0f9ff 50%, #eff6ff 75%, #fffdf9 100%)'
        title_text = title.upper()
        has_gold_foil = False
        has_sparkles = False
        has_color_shift = True
        border_style = 'solid'
    else:  # completion - MUSEUM QUALITY
        primary_color = '#6D28D9'
        secondary_color = '#4C1D95'
        accent_color = '#D8B4FE'
        bg_gradient = 'linear-gradient(160deg, #fffdf9 0%, #f8f5ff 20%, #fffdf9 40%, #f5f0ff 60%, #fffdf9 80%, #f8f5ff 100%)'
        title_text = 'OFFICIAL COURSE COMPLETION CERTIFICATE'
        has_gold_foil = False
        has_sparkles = False
        has_color_shift = True
        border_style = 'double'
    
    # ============================================
    # BUILD HTML WITH ALL FEATURES
    # ============================================
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&family=Georgia:wght@400;700&family=Playfair+Display:wght@700;800&family=Courier+Prime&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            width: {'1240' if cert_type == 'payment' else '2480'}px;
            min-height: {'1748' if cert_type == 'payment' else '3508'}px;
            background: {primary_color};
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Poppins', 'Georgia', serif;
            position: relative;
        }}
        
        .certificate {{
            width: {'1050' if cert_type == 'payment' else '2200'}px;
            min-height: {'1480' if cert_type == 'payment' else '3100'}px;
            background: {bg_gradient};
            border: {border_style} 16px {primary_color};
            position: relative;
            padding: {'50px 60px' if cert_type == 'payment' else '80px 100px'};
            box-shadow: 
                0 0 0 6px {secondary_color},
                0 0 0 12px {accent_color},
                0 20px 40px rgba(0,0,0,0.25),
                0 40px 80px rgba(0,0,0,0.2),
                0 60px 120px rgba(0,0,0,0.15),
                0 80px 160px rgba(0,0,0,0.1),
                inset 0 0 100px rgba(0,0,0,0.03);
            transform: perspective(2000px) rotateX(0.5deg);
        }}
        
        /* Museum Paper Texture */
        .certificate::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: url("data:image/svg+xml,%3Csvg width='200' height='200' viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23noise)' opacity='0.05'/%3E%3C/svg%3E");
            pointer-events: none;
            z-index: 1;
        }}
        
        /* Inner Border Frame */
        .certificate::after {{
            content: '';
            position: absolute;
            top: {'20px' if cert_type == 'payment' else '40px'};
            left: {'20px' if cert_type == 'payment' else '40px'};
            right: {'20px' if cert_type == 'payment' else '40px'};
            bottom: {'20px' if cert_type == 'payment' else '40px'};
            border: {('2px' if cert_type == 'payment' else '3px')} solid {secondary_color};
            pointer-events: none;
            z-index: 1;
        }}
        
        /* Corner Ornaments */
        .corner-ornament {{
            position: absolute;
            width: 50px;
            height: 50px;
            z-index: 2;
            pointer-events: none;
        }}
        .corner-ornament::before {{
            content: '';
            position: absolute;
            width: 50px;
            height: 50px;
            border-color: {primary_color};
            border-style: solid;
            border-width: 0;
        }}
        .corner-ornament.tl::before {{ top: 15px; left: 15px; border-top-width: 5px; border-left-width: 5px; }}
        .corner-ornament.tr::before {{ top: 15px; right: 15px; border-top-width: 5px; border-right-width: 5px; }}
        .corner-ornament.bl::before {{ bottom: 15px; left: 15px; border-bottom-width: 5px; border-left-width: 5px; }}
        .corner-ornament.br::before {{ bottom: 15px; right: 15px; border-bottom-width: 5px; border-right-width: 5px; }}
        .corner-ornament::after {{
            content: '◆';
            position: absolute;
            font-size: 14px;
            color: {accent_color};
        }}
        .corner-ornament.tl::after {{ top: 5px; left: 5px; }}
        .corner-ornament.tr::after {{ top: 5px; right: 5px; }}
        .corner-ornament.bl::after {{ bottom: 5px; left: 5px; }}
        .corner-ornament.br::after {{ bottom: 5px; right: 5px; }}

        /* Watermark */
        .watermark {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-30deg);
            font-size: 180px;
            font-weight: 800;
            color: rgba(0,0,0,0.03);
            letter-spacing: 30px;
            pointer-events: none;
            z-index: 0;
        }}
        
        /* Guilloché Pattern */
        .guilloche {{
            position: absolute;
            top: 60px;
            left: 60px;
            right: 60px;
            bottom: 60px;
            background-image: repeating-radial-gradient(
                circle at 50% 50%,
                transparent 0,
                rgba(0,0,0,0.02) 1px,
                transparent 2px,
                transparent 20px
            );
            pointer-events: none;
            z-index: 0;
        }}
        
        .gold-foil {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(245,158,11,0.08), rgba(252,211,77,0.15));
            pointer-events: none;
            z-index: 1;
        }}
        
        .sparkle {{
            position: absolute;
            width: 6px;
            height: 6px;
            background: #FCD34D;
            border-radius: 50%;
            pointer-events: none;
            z-index: 1;
            box-shadow: 0 0 10px #F59E0B;
        }}
        
        .holographic {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(255,255,255,0.03), rgba(109,40,217,0.05));
            pointer-events: none;
            z-index: 1;
        }}

            position: absolute;
            top: 60px;
            left: 60px;
            right: 60px;
            bottom: 60px;
            background-image: repeating-radial-gradient(
                circle at 50% 50%,
                transparent 0,
                rgba(0,0,0,0.02) 1px,
                transparent 2px,
                transparent 20px
            );
            pointer-events: none;
            z-index: 0;
        }}
        
        /* Gold Foil Effect (VIP only) */
        {''
        if has_gold_foil else ''}
        
        /* Sparkle Particles (VIP & Promo) */
        {''
        if has_sparkles else ''}
        
        .header {{
            text-align: center;
            margin-bottom: 60px;
            position: relative;
            z-index: 2;
        }}
        
        .title {{
            font-size: {'32px' if cert_type == 'payment' else '56px'};
            font-weight: 800;
            color: {primary_color};
            letter-spacing: 6px;
            text-transform: uppercase;
            margin-bottom: 20px;
            {'background: linear-gradient(135deg, #14B8A6, #0D9488, #14B8A6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;' if cert_type == 'payment' else ('background: linear-gradient(135deg, #6D28D9, #F59E0B, #14B8A6, #6D28D9); -webkit-background-clip: text; -webkit-text-fill-color: transparent;' if has_color_shift else '')}
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }}
        
        .subtitle {{
            font-size: 28px;
            color: #64748b;
            letter-spacing: 4px;
        }}
        
        .recipient {{
            text-align: center;
            margin: 80px 0;
            position: relative;
            z-index: 2;
        }}
        
        .student-name {{
            font-size: {'45px' if cert_type == 'payment' else '90px'};
            font-weight: 700;
            color: #1e1b4b;
            font-family: 'Playfair Display', 'Georgia', serif;
            border-bottom: 5px solid {primary_color};
            display: inline-block;
            padding: 15px 60px;
            margin: 30px 0;
            text-shadow: 
                2px 2px 0px rgba(0,0,0,0.05),
                4px 4px 8px rgba(0,0,0,0.1);
            letter-spacing: 2px;
        }}
        
        .student-details {{
            font-size: 32px;
            color: #64748b;
        }}
        
        .credentials {{
            margin: 60px auto;
            max-width: 1600px;
            background: rgba(0,0,0,0.02);
            border-radius: 16px;
            padding: 30px 50px;
            font-size: 24px;
            position: relative;
            z-index: 2;
        }}
        
        .credential-row {{
            display: flex;
            justify-content: space-between;
            margin: 15px 0;
            color: #334155;
        }}
        
        .footer {{
            display: flex;
            justify-content: space-around;
            align-items: center;
            margin-top: 80px;
            position: relative;
            z-index: 2;
        }}
        
        .qr-section {{
            text-align: center;
        }}
        
        .qr-section img {{
            width: 180px;
            height: 180px;
            border: 4px solid {primary_color};
            border-radius: 8px;
        }}
        
        /* Microtext Security */
        .microtext {{
            position: absolute;
            bottom: 55px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 10px;
            letter-spacing: 3px;
            color: rgba(0,0,0,0.15);
            white-space: nowrap;
            font-family: 'Courier Prime', 'Courier New', monospace;
            z-index: 2;
        }}
        
        /* Barcode (Payment) */
        .barcode {{
            display: flex;
            align-items: center;
            height: 50px;
            margin: 10px auto;
            width: 300px;
            position: relative;
            z-index: 2;
        }}
    </style>
</head>
<body>
    <div class="certificate">
        <div class="corner-ornament tl"></div>
        <div class="corner-ornament tr"></div>
        <div class="corner-ornament bl"></div>
        <div class="corner-ornament br"></div>
        <div class="watermark">{'UNIYO PAID' if cert_type == 'payment' else 'UNIYO'}</div>
        <div class="guilloche"></div>
        {'<div class="gold-foil"></div>' if has_gold_foil else ''}
        {'<div class="holographic"></div>' if has_color_shift else ''}
        {'<div class="sparkle" style="top: 15%; left: 10%;"></div><div class="sparkle" style="top: 25%; right: 15%;"></div><div class="sparkle" style="top: 45%; left: 20%;"></div><div class="sparkle" style="top: 65%; right: 10%;"></div><div class="sparkle" style="top: 75%; left: 15%;"></div>' if has_sparkles else ''}
        {'<div class="anti-copy"></div>' if cert_type == 'payment' else ''}
        
        <div class="header">
            <img src="file://{logo_path}" alt="UNIYO" style="height: 80px; object-fit: contain; margin-bottom: 20px;">
            <div class="title">{title_text}</div>
            <div class="subtitle">Ethiopian Higher Education Freshman Hub</div>
        </div>
        
        <div class="recipient">
            <div style="font-size: {'20px' if cert_type == 'payment' else '30px'}; color: #64748b;">{'PAYMENT RECEIVED FROM' if cert_type == 'payment' else 'This certificate is proudly presented to'}</div>
            <div class="student-name">{full_name}</div>
            {'''
            <div style="max-width: 1400px; margin: 25px auto; padding: 15px 30px; background: rgba(0,0,0,0.03); border-radius: 10px; font-size: ''' + ('16px' if cert_type == 'payment' else '22px') + '''; color: #334155; text-align: center; line-height: 1.6;">
                ''' + ('For payment of 200 ETB for UNIYO Premium Subscription (1 Year Access).' if cert_type == 'payment' else
                'For outstanding performance in the UNIYO VIP Monthly Competition, ranking #' + str(rank or 1) + ' among students nationwide.' if cert_type == 'vip_leaderboard' else
                'In recognition of outstanding contribution to promoting UNIYO across Ethiopian universities.' if cert_type == 'promotion' else
                'For outstanding academic excellence and exceptional performance in your studies.' if cert_type == 'excellence' else
                'In recognition of exceptional contribution to creating high-quality educational content for UNIYO students.' if cert_type == 'content_creator' else
                'In recognition of exceptional leadership in promoting UNIYO to Ethiopian students nationwide.' if cert_type == 'marketing_manager' else
                'In recognition of exceptional contribution to advertising and promoting UNIYO across Ethiopia.' if cert_type == 'advertiser' else
                'In recognition of outstanding service and dedication to the UNIYO learning platform.' if cert_type == 'staff' else
                'In recognition of your hard work and dedication. Congratulations on your achievement!' if cert_type in ['congratulations', 'special_congratulations'] else
                'For active participation in the UNIYO community and dedication to learning.' if cert_type == 'participation' else
                'In recognition of outstanding contribution and dedication to the UNIYO learning community.' if cert_type == 'appreciation' else
                'For successfully completing lessons and worksheets with dedication and academic excellence.') + '''
            </div>
            '''}
            <div class="student-details">{university} • {stream} Science • {sex}</div>
            {'<div style="margin: 15px auto; display: inline-block; padding: 10px 30px; border: 3px solid #22C55E; border-radius: 50%; font-size: 30px; font-weight: 800; color: #22C55E; transform: rotate(-15deg);">✓ PAID</div>' if cert_type == 'payment' else ''}
        </div>
        
        <div class="credentials">
            <div class="credential-row">
                <span>{'Receipt Number' if cert_type == 'payment' else 'Certificate Number'}:</span>
                <strong style="font-family: 'Courier Prime', 'Courier New', monospace;">{cert_number}</strong>
            </div>
            <div class="credential-row">
                <span>Verification Token:</span>
                <strong style="font-family: 'Courier Prime', 'Courier New', monospace; font-size: 18px;">{certificate_data.get('verification_token', '')[:30]}...</strong>
            </div>
            {'<div class="credential-row"><span>Transaction Hash:</span><strong style="font-family: Courier New, monospace; font-size: 14px;">' + certificate_data.get('verification_token', '')[:40] + '...</strong></div>' if cert_type == 'payment' else ''}
            <div class="credential-row">
                <span>{'Date' if cert_type == 'payment' else 'Issue Date'}:</span>
                <strong>{issue_date}</strong>
            </div>
            {'<div class="credential-row"><span>Amount:</span><strong style="color: #14B8A6;">200 ETB</strong></div>' if cert_type == 'payment' else ''}
            {'<div class="credential-row"><span>Payment Method:</span><strong>' + certificate_data.get('payment_method', 'N/A') + '</strong></div>' if cert_type == 'payment' else ''}
            {'<div class="credential-row"><span>Transaction Number:</span><strong>' + certificate_data.get('transaction_number', 'N/A') + '</strong></div>' if cert_type == 'payment' else ''}
            <div class="credential-row">
                <span>Certificate Type:</span>
                <strong style="color: {primary_color};">{cert_type.upper()}</strong>
            </div>
            <div style="text-align: center; margin-top: 15px; font-size: 14px; color: #64748b;">
                🔍 Verify at: <strong style="color: {primary_color};">{verification_url}</strong>
            </div>
        </div>
        
        <!-- PRIMARY STAMP: Center at Bottom -->
        <div style="display: flex; justify-content: center; margin: 20px 0 10px 0; position: relative; z-index: 3;">
            <img src="file://{primary_stamp}" alt="Primary Stamp" style="width: 90px; height: 90px; object-fit: contain; border-radius: 50%;">
        </div>
        
        <!-- SECONDARY STAMP: Right side, 35% from bottom, in FRONT -->
        {'<div style="position: absolute; bottom: 35%; right: 150px; z-index: 5; opacity: 0.85;"><img src="file://' + secondary_stamp + '" alt="Secondary Stamp" style="width: 70px; height: 70px; object-fit: contain; border-radius: 50%;"></div>' if has_secondary_stamp else ''}
        
        <div class="footer">
            <div class="qr-section">
                <img src="{qr_data_uri}" alt="QR Code">
                <div style="font-size: 20px; color: #64748b; margin-top: 8px;">Scan to Verify</div>
                <div class="barcode" style="margin-top: 10px; display: flex; align-items: center; justify-content: center; height: 40px;">
                    <div style="width: 2px; height: 35px; background: #000; margin-right: 1px;"></div>
                    <div style="width: 1px; height: 35px; background: #fff; margin-right: 1px;"></div>
                    <div style="width: 2px; height: 35px; background: #000; margin-right: 1px;"></div>
                    <div style="width: 1px; height: 35px; background: #fff; margin-right: 1px;"></div>
                    <div style="width: 3px; height: 35px; background: #000; margin-right: 1px;"></div>
                    <div style="width: 1px; height: 35px; background: #fff; margin-right: 1px;"></div>
                    <div style="width: 2px; height: 35px; background: #000; margin-right: 1px;"></div>
                </div>
                <small style="font-size: 10px; font-family: 'Courier New', monospace; color: #334155;">{cert_number}</small>
                {'<div class="barcode" style="margin-top: 10px;"><div style="width: 2px; height: 40px; background: #000; margin-right: 1px;"></div><div style="width: 1px; height: 40px; background: #fff; margin-right: 1px;"></div><div style="width: 2px; height: 40px; background: #000; margin-right: 1px;"></div><div style="width: 1px; height: 40px; background: #fff; margin-right: 1px;"></div><div style="width: 3px; height: 40px; background: #000; margin-right: 1px;"></div><div style="width: 1px; height: 40px; background: #fff; margin-right: 1px;"></div><div style="width: 2px; height: 40px; background: #000; margin-right: 1px;"></div><small style="font-size: 8px; font-family: Courier New, monospace;">' + cert_number + '</small></div>' if cert_type == 'payment' else ''}
            </div>
            
            <div style="text-align: center; font-size: 20px;">
                <img src="file://{super_admin_signature}" alt="Signature" style="height: 30px; object-fit: contain;">
                <img src="file://{super_admin_name}" alt="Name" style="height: 22px; object-fit: contain; margin-top: 2px;">
                <div style="font-size: 14px; color: #64748b; margin-top: 4px;">Super Admin</div>
            </div>
            {'<div style="text-align: center; font-size: 20px;"><img src="file://' + content_manager_signature + '" alt="Signature" style="height: 30px; object-fit: contain;"><img src="file://' + content_manager_name + '" alt="Name" style="height: 22px; object-fit: contain; margin-top: 2px;"><div style="font-size: 14px; color: #64748b; margin-top: 4px;">Content Manager</div></div>' if cert_type not in ['other', 'excellence', 'content_creator', 'marketing_manager', 'advertiser', 'staff', 'special_congratulations', 'participation', 'appreciation', 'congratulations'] else ''}
        </div>
        
        <div class="microtext">{'UNIYO AUTHENTIC PAYMENT RECEIPT • VERIFY ONLINE • ANTI-FRAUD PROTECTED' if cert_type == 'payment' else 'UNIYO AUTHENTIC CERTIFICATE • VERIFY ONLINE • SECURITY FEATURES INCLUDED'}</div>
    </div>
</body>
</html>
"""
    
    return html




def generate_certificate_image_with_pillow(certificate_data, qr_data_uri):
    """Generate certificate image using Pillow (always works on any Python)"""
    from PIL import Image, ImageDraw, ImageFont
    from core.paths import CERTIFICATES_DIR
    
    cert_type = certificate_data.get('certificate_type', 'completion')
    full_name = certificate_data.get('full_name', 'Student')
    university = certificate_data.get('university', '')
    stream = certificate_data.get('stream', '')
    sex = certificate_data.get('sex', '')
    cert_number = certificate_data.get('certificate_number', 'UNKNOWN')
    title = certificate_data.get('title', 'Certificate')
    issue_date = certificate_data.get('issue_date', '')
    
    cert_id = cert_number.replace('/', '_').replace('\\', '_')
    output_path = CERTIFICATES_DIR / f"{cert_id}.png"
    
    # Set dimensions based on type
    if cert_type == 'payment':
        width, height = 1240, 1748
    else:
        width, height = 2480, 3508
    
    # Create image
    img = Image.new('RGB', (width, height), '#fffdf9')
    draw = ImageDraw.Draw(img)
    
    # Colors
    if cert_type == 'vip_leaderboard':
        primary = '#F59E0B'
    elif cert_type == 'payment':
        primary = '#14B8A6'
    elif cert_type == 'promotion':
        primary = '#F97316'
    else:
        primary = '#6D28D9'
    
    # Double border
    draw.rectangle([30, 30, width-30, height-30], outline=primary, width=8)
    draw.rectangle([50, 50, width-50, height-50], outline='#F59E0B', width=3)
    
    # Try to load fonts
    try:
        font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 80)
        font_medium = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 40)
        font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 30)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Title
    draw.text((width//2, 150), title, fill=primary, font=font_large, anchor='mm')
    
    # Student name
    draw.text((width//2, height//2 - 100), full_name, fill='#1e1b4b', font=font_large, anchor='mm')
    
    # University
    details = university
    if stream:
        details += f" • {stream} Science"
    if sex:
        details += f" • {sex}"
    draw.text((width//2, height//2 + 50), details, fill='#64748b', font=font_medium, anchor='mm')
    
    # Certificate number
    draw.text((width//2, height - 300), f"Certificate Number: {cert_number}", fill='#334155', font=font_small, anchor='mm')
    draw.text((width//2, height - 250), f"Date: {issue_date}", fill='#334155', font=font_small, anchor='mm')
    
    # Microtext
    draw.text((width//2, height - 100), "UNIYO AUTHENTIC CERTIFICATE • VERIFY ONLINE", fill='#94a3b8', font=font_small, anchor='mm')
    
    img.save(str(output_path))
    return output_path


def generate_certificate_image_sync(certificate_data, qr_data_uri):
    """Synchronous wrapper"""
    import traceback
    try:
        return generate_certificate_image(certificate_data, qr_data_uri)
    except Exception as e:
        print(f"[PLAYWRIGHT ERROR]: {e}")
        traceback.print_exc()
        logger.error(f"Error in sync wrapper: {e}")
        return None
