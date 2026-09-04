"""
UNIYO LMS - Certificate Viewing Routes
"""

from flask import Blueprint, render_template, redirect, url_for, session, flash
from pathlib import Path
from core.db import get_db
from core.auth import login_required
from core.helpers import generate_qr_data_uri
from core.certificate_image_generator import generate_certificate_image_sync, generate_certificate_image_with_pillow, generate_certificate_image_with_html2image

certificate_bp = Blueprint('certificate', __name__)

@certificate_bp.route('/student/certificates', methods=['GET'])
@login_required
def my_certificates():
    db = get_db()
    certificates = db.query("SELECT * FROM certificates WHERE student_id = ? ORDER BY issue_date DESC", (session['student_id'],))
    return render_template('student_certificates.html', certificates=certificates)

@certificate_bp.route('/student/certificate/<int:certificate_id>', methods=['GET'])
@login_required
def view_certificate(certificate_id):
    db = get_db()
    try:
        student_id = session.get('student_id', 0)
        certificate = db.query_one("SELECT * FROM certificates WHERE id = ? AND student_id = ?", (certificate_id, student_id))
    except Exception as e:
        flash(f"Certificate error: {e}", "danger")
        return redirect(url_for('certificate.my_certificates'))
    if certificate:
        certificate = dict(certificate)
        student = db.query_one("SELECT full_name, university, stream, sex FROM students WHERE id = ?", (certificate['student_id'],))
        if student:
            student = dict(student)
            certificate['full_name'] = student.get('full_name', '')
            certificate['university'] = student.get('university', '')
            certificate['stream'] = student.get('stream', '')
    
    if not certificate:
        flash("Certificate not found", "danger")
        return redirect(url_for('certificate.my_certificates'))
    
    from flask import request
    verify_url = f"{request.host_url}verify/{certificate['verification_token']}"
    qr_data_uri = generate_qr_data_uri(verify_url)
    
    # Redirect to image view (no HTML exposed to students)
    return redirect(url_for('certificate.view_certificate_image', certificate_id=certificate_id))

@certificate_bp.route('/student/certificate/<int:certificate_id>/image', methods=['GET'])
@login_required
def view_certificate_image(certificate_id):
    """Serve certificate as PNG image (no HTML exposed)"""
    from flask import send_file
    import traceback
    db = get_db()
    print(f"[DEBUG] Viewing certificate image ID={certificate_id}")
    
    # Verify student owns this certificate
    certificate = db.query_one(
        "SELECT * FROM certificates WHERE id = ? AND student_id = ?",
        (certificate_id, session['student_id'])
    )
    
    if not certificate:
        flash("Certificate not found", "danger")
        return redirect(url_for('certificate.my_certificates'))
    
    certificate = dict(certificate)
    
    # Get student details
    student = db.query_one(
        "SELECT full_name, university, stream, sex FROM students WHERE id = ?",
        (certificate['student_id'],)
    )
    if student:
        student = dict(student)
        certificate['full_name'] = student.get('full_name', '')
        certificate['university'] = student.get('university', '')
        certificate['stream'] = student.get('stream', '')
    
    # Generate QR code
    from flask import request
    from core.helpers import generate_qr_data_uri
    verify_url = f"{request.host_url}verify/{certificate['verification_token']}"
    qr_data_uri = generate_qr_data_uri(verify_url)
    
    # Generate certificate image
    # Use Pillow as PRIMARY (works on all Python versions)
    # Try html2image FIRST (full CSS support)
    try:
        image_path = generate_certificate_image_with_html2image(certificate, qr_data_uri)
    except:
        image_path = None
    
    if not image_path or not Path(image_path).exists():
        image_path = generate_certificate_image_with_pillow(certificate, qr_data_uri)
    
    if image_path and Path(image_path).exists():
        return send_file(str(image_path), mimetype='image/png')
    
    # Fallback: Generate simple PNG with Pillow if Playwright fails
    try:
        from PIL import Image, ImageDraw, ImageFont
        from core.paths import CERTIFICATES_DIR
        
        cert_number = certificate.get('certificate_number', 'UNKNOWN')
        cert_id = cert_number.replace('/', '_').replace('\\', '_')
        fallback_path = CERTIFICATES_DIR / f"{cert_id}_fallback.png"
        
        # Create simple certificate with Pillow
        img = Image.new('RGB', (1240, 1748), '#fffdf9')
        draw = ImageDraw.Draw(img)
        
        # Border
        draw.rectangle([20, 20, 1220, 1728], outline='#6D28D9', width=5)
        draw.rectangle([30, 30, 1210, 1718], outline='#F59E0B', width=2)
        
        # Title
        title = certificate.get('title', 'Certificate')
        name = certificate.get('full_name', 'Student')
        university = certificate.get('university', '')
        cert_num = certificate.get('certificate_number', '')
        
        # Use default font
        # Try multiple font paths for cross-platform compatibility
        font_large = None
        font_medium = None
        font_small = None
        
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/TTF/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/TTF/DejaVuSans.ttf',
            '/System/Library/Fonts/Helvetica.ttc',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
        ]
        
        for font_path in font_paths:
            if Path(font_path).exists():
                try:
                    font_large = ImageFont.truetype(font_path, 60)
                    font_medium = ImageFont.truetype(font_path.replace('Bold', ''), 40)
                    font_small = ImageFont.truetype(font_path.replace('Bold', ''), 30)
                    break
                except:
                    continue
        
        if font_large is None:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw text
        draw.text((620, 100), title, fill='#6D28D9', font=font_large, anchor='mm')
        draw.text((620, 300), 'This certificate is presented to', fill='#64748b', font=font_small, anchor='mm')
        draw.text((620, 400), name, fill='#1e1b4b', font=font_large, anchor='mm')
        draw.text((620, 500), university, fill='#64748b', font=font_medium, anchor='mm')
        draw.text((620, 700), f'Certificate Number: {cert_num}', fill='#334155', font=font_small, anchor='mm')
        draw.text((620, 750), f'Issue Date: {certificate.get("issue_date", "")}', fill='#334155', font=font_small, anchor='mm')
        
        img.save(str(fallback_path))
        
        if fallback_path.exists():
            return send_file(str(fallback_path), mimetype='image/png')
    except Exception as e:
        print(f"Fallback generation failed: {e}")
    
    # No HTML fallback - return error if image generation completely fails
    return {"success": False, "error": "Certificate image generation failed"}, 500


@certificate_bp.route('/student/certificate/<int:certificate_id>/download', methods=['GET'])
@login_required
def download_certificate_image(certificate_id):
    """Download certificate as PNG or JPG"""
    from flask import send_file, request
    db = get_db()
    format_type = request.args.get('format', 'png')
    
    certificate = db.query_one(
        "SELECT * FROM certificates WHERE id = ? AND student_id = ?",
        (certificate_id, session['student_id'])
    )
    
    if not certificate:
        flash("Certificate not found", "danger")
        return redirect(url_for('certificate.my_certificates'))
    
    certificate = dict(certificate)
    
    # Check if image already exists
    cert_number = certificate.get('certificate_number', 'UNKNOWN')
    cert_id = cert_number.replace('/', '_').replace('\\', '_')
    from core.paths import CERTIFICATES_DIR
    image_path = CERTIFICATES_DIR / f"{cert_id}.png"
    
    if image_path.exists():
        download_name = f"UNIYO_Certificate_{cert_id}.{format_type}"
        mimetype = 'image/jpeg' if format_type == 'jpg' else 'image/png'
        
        # For JPG, convert PNG to JPG
        if format_type == 'jpg':
            from PIL import Image as PILImage
            jpg_path = CERTIFICATES_DIR / f"{cert_id}.jpg"
            if not jpg_path.exists() or jpg_path.stat().st_size == 0:
                img = PILImage.open(str(image_path))
                img = img.convert('RGB')
                img.save(str(jpg_path), 'JPEG', quality=95)
            return send_file(str(jpg_path), as_attachment=True, download_name=download_name, mimetype=mimetype)
        
        return send_file(str(image_path), as_attachment=True, download_name=download_name, mimetype=mimetype)
    
    # Generate if not exists
    student = db.query_one(
        "SELECT full_name, university, stream, sex FROM students WHERE id = ?",
        (certificate['student_id'],)
    )
    if student:
        student = dict(student)
        certificate['full_name'] = student.get('full_name', '')
        certificate['university'] = student.get('university', '')
        certificate['stream'] = student.get('stream', '')
    
    from flask import request
    from core.helpers import generate_qr_data_uri
    verify_url = f"{request.host_url}verify/{certificate['verification_token']}"
    qr_data_uri = generate_qr_data_uri(verify_url)
    
    # Use Pillow as PRIMARY (works on all Python versions)
    # Try html2image FIRST (full CSS support)
    try:
        image_path = generate_certificate_image_with_html2image(certificate, qr_data_uri)
    except:
        image_path = None
    
    if not image_path or not Path(image_path).exists():
        image_path = generate_certificate_image_with_pillow(certificate, qr_data_uri)
    
    if image_path and Path(image_path).exists():
        download_name = f"UNIYO_Certificate_{cert_id}.{format_type}"
        mimetype = 'image/jpeg' if format_type == 'jpg' else 'image/png'
        
        if format_type == 'jpg':
            from PIL import Image as PILImage
            jpg_path = CERTIFICATES_DIR / f"{cert_id}.jpg"
            if not jpg_path.exists() or jpg_path.stat().st_size == 0:
                img = PILImage.open(str(image_path))
                img = img.convert('RGB')
                img.save(str(jpg_path), 'JPEG', quality=95)
            return send_file(str(jpg_path), as_attachment=True, download_name=download_name, mimetype=mimetype)
        
        return send_file(str(image_path), as_attachment=True, download_name=download_name, mimetype=mimetype)
    
    flash("Could not generate certificate image", "danger")
    return redirect(url_for('certificate.my_certificates'))


@certificate_bp.route('/verify/<token>', methods=['GET'])
def verify_certificate(token):
    db = get_db()
    certificate = db.query_one("SELECT * FROM certificates WHERE verification_token = ?", (token,))
    if certificate:
        certificate = dict(certificate)
        student = db.query_one("SELECT full_name, university, stream, sex FROM students WHERE id = ?", (certificate['student_id'],))
        if student:
            student = dict(student)
            certificate['full_name'] = student.get('full_name', '')
            certificate['university'] = student.get('university', '')
            certificate['stream'] = student.get('stream', '')
    
    if not certificate:
        return render_template('verification_invalid.html'), 404
    
    return render_template('verification_valid.html', certificate=certificate)


@certificate_bp.route('/student/api/certificate/<int:certificate_id>', methods=['GET'])
@login_required
def api_student_certificate(certificate_id):
    """Student API endpoint for certificate popup"""
    db = get_db()
    student_id = session.get('student_id', 0)
    certificate = db.query_one("SELECT * FROM certificates WHERE id = ? AND student_id = ?", (certificate_id, student_id))
    if certificate:
        certificate = dict(certificate)
        student = db.query_one("SELECT full_name, university, stream, sex FROM students WHERE id = ?", (certificate.get('student_id'),))
        if student:
            student = dict(student)
            certificate['full_name'] = student.get('full_name', '')
            certificate['university'] = student.get('university', '')
            certificate['stream'] = student.get('stream', '')
        
        from flask import request
        from core.helpers import generate_qr_data_uri
        from core.certificate_image_generator import generate_certificate_image_sync, generate_certificate_image_with_pillow, generate_certificate_image_with_html2image
        verify_url = f"{request.host_url}verify/{certificate.get('verification_token', '')}"
        qr_data_uri = generate_qr_data_uri(verify_url)
        
        return {"success": True, "redirect": f"/student/certificate/{certificate_id}/image"}
    return {"success": False, "error": "Certificate not found"}
