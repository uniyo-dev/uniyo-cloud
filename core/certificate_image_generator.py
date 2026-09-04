"""
UNIYO LMS - Certificate Image Generator (Enhanced)
Converts HTML certificate to PNG/JPG using Playwright
Features: Museum Quality + Banknote Security + NFT Digital Feel
"""

import os
import asyncio
from pathlib import Path
from datetime import datetime

from core.paths import CERTIFICATES_DIR, BASE_DIR
from core.helpers import logger

# ============================================
# CERTIFICATE IMAGE GENERATION
# ============================================

async def generate_certificate_image(certificate_data, qr_data_uri):
    """Generate certificate as PNG with all security features"""
    try:
        from playwright.async_api import async_playwright
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
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={'width': viewport_width, 'height': viewport_height})
            await page.goto(f'file://{temp_html}')
            await page.wait_for_timeout(2000)
            await page.screenshot(path=str(output_path), full_page=True, type='png')
            await browser.close()
        
        temp_html.unlink(missing_ok=True)
        return output_path
    
    except Exception as e:
        logger.error(f"Error generating certificate image: {e}")
        temp_html.unlink(missing_ok=True)
        return None


def build_certificate_html(certificate_data, qr_data_uri):
    """Build enhanced HTML with all security features"""
    
    full_name = certificate_data.get('full_name', '')
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
    elif cert_type == 'payment':
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
        <div class="watermark">{'UNIYO PAID' if cert_type == 'payment' else 'UNIYO'}</div>
        <div class="guilloche"></div>
        {'<div class="anti-copy"></div>' if cert_type == 'payment' else ''}
        
        <div class="header">
            <div class="title">{{ title_text }}</div>
            <div class="subtitle">Ethiopian Higher Education Freshman Hub</div>
        </div>
        
        <div class="recipient">
            <div style="font-size: {'20px' if cert_type == 'payment' else '30px'}; color: #64748b;">{'PAYMENT RECEIVED FROM' if cert_type == 'payment' else 'This certificate is proudly presented to'}</div>
            <div class="student-name">{{ full_name }}</div>
            <div class="student-details">{{ university }}</div>
            {'<div style="margin: 15px auto; display: inline-block; padding: 10px 30px; border: 3px solid #22C55E; border-radius: 50%; font-size: 30px; font-weight: 800; color: #22C55E; transform: rotate(-15deg);">✓ PAID</div>' if cert_type == 'payment' else ''}
        </div>
        
        <div class="credentials">
            <div class="credential-row">
                <span>{'Receipt Number' if cert_type == 'payment' else 'Certificate Number'}:</span>
                <strong style="font-family: 'Courier Prime', 'Courier New', monospace;">{{ cert_number }}</strong>
            </div>
            <div class="credential-row">
                <span>Verification Token:</span>
                <strong style="font-family: 'Courier Prime', 'Courier New', monospace; font-size: 18px;">{{ certificate_data.get('verification_token', '')[:30] }}...</strong>
            </div>
            {'<div class="credential-row"><span>Transaction Hash:</span><strong style="font-family: Courier New, monospace; font-size: 14px;">' + certificate_data.get('verification_token', '')[:40] + '...</strong></div>' if cert_type == 'payment' else ''}
            <div class="credential-row">
                <span>{'Date' if cert_type == 'payment' else 'Issue Date'}:</span>
                <strong>{{ issue_date }}</strong>
            </div>
            {'<div class="credential-row"><span>Amount:</span><strong style="color: #14B8A6;">200 ETB</strong></div>' if cert_type == 'payment' else ''}
            {'<div class="credential-row"><span>Payment Method:</span><strong>' + certificate_data.get('payment_method', 'N/A') + '</strong></div>' if cert_type == 'payment' else ''}
            {'<div class="credential-row"><span>Transaction Number:</span><strong>' + certificate_data.get('transaction_number', 'N/A') + '</strong></div>' if cert_type == 'payment' else ''}
            <div class="credential-row">
                <span>Certificate Type:</span>
                <strong style="color: {primary_color};">{{ cert_type.upper() }}</strong>
            </div>
        </div>
        
        <div class="footer">
            <div class="qr-section">
                <img src="{{ qr_data_uri }}" alt="QR Code">
                <div style="font-size: 20px; color: #64748b; margin-top: 8px;">Scan to Verify</div>
                {'<div class="barcode" style="margin-top: 10px;"><div style="width: 2px; height: 40px; background: #000; margin-right: 1px;"></div><div style="width: 1px; height: 40px; background: #fff; margin-right: 1px;"></div><div style="width: 2px; height: 40px; background: #000; margin-right: 1px;"></div><div style="width: 1px; height: 40px; background: #fff; margin-right: 1px;"></div><div style="width: 3px; height: 40px; background: #000; margin-right: 1px;"></div><div style="width: 1px; height: 40px; background: #fff; margin-right: 1px;"></div><div style="width: 2px; height: 40px; background: #000; margin-right: 1px;"></div><small style="font-size: 8px; font-family: Courier New, monospace;">' + cert_number + '</small></div>' if cert_type == 'payment' else ''}
            </div>
            
            <div style="text-align: center; font-size: 26px;">
                <div style="border-bottom: 3px solid {primary_color}; padding-bottom: 15px; margin-bottom: 8px;">
                    Chalachew Agegn
                </div>
                <span style="font-size: 20px; color: #64748b;">Super Admin</span>
            </div>
        </div>
        
        <div class="microtext">{'UNIYO AUTHENTIC PAYMENT RECEIPT • VERIFY ONLINE • ANTI-FRAUD PROTECTED' if cert_type == 'payment' else 'UNIYO AUTHENTIC CERTIFICATE • VERIFY ONLINE • SECURITY FEATURES INCLUDED'}</div>
    </div>
</body>
</html>
"""
    
    return html


def generate_certificate_image_sync(certificate_data, qr_data_uri):
    """Synchronous wrapper"""
    try:
        return asyncio.run(generate_certificate_image(certificate_data, qr_data_uri))
    except Exception as e:
        logger.error(f"Error in sync wrapper: {e}")
        return None
