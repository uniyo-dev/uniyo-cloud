"""
UNIYO LMS - Certificate Viewing Routes
"""

from flask import Blueprint, render_template, redirect, url_for, session, flash
from core.db import get_db
from core.auth import login_required
from core.helpers import generate_qr_data_uri
from core.certificate_image_generator import generate_certificate_image_sync

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
        student = db.query_one("SELECT full_name, university, stream FROM students WHERE id = ?", (certificate['student_id'],))
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
    
    return render_template('student_certificate.html', certificate=certificate, qr_data_uri=qr_data_uri)

@certificate_bp.route('/student/certificate/<int:certificate_id>/image', methods=['GET'])
@login_required
def view_certificate_image(certificate_id):
    """Serve certificate as PNG image (no HTML exposed)"""
    from flask import send_file
    db = get_db()
    
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
        "SELECT full_name, university, stream FROM students WHERE id = ?",
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
    image_path = generate_certificate_image_sync(certificate, qr_data_uri)
    
    if image_path and Path(image_path).exists():
        return send_file(str(image_path), mimetype='image/png')
    
    # Fallback to HTML view if image generation fails
    return redirect(url_for('certificate.view_certificate', certificate_id=certificate_id))


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
        "SELECT full_name, university, stream FROM students WHERE id = ?",
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
    
    image_path = generate_certificate_image_sync(certificate, qr_data_uri)
    
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
    return redirect(url_for('certificate.view_certificate', certificate_id=certificate_id))


@certificate_bp.route('/verify/<token>', methods=['GET'])
def verify_certificate(token):
    db = get_db()
    certificate = db.query_one("SELECT * FROM certificates WHERE verification_token = ?", (token,))
    if certificate:
        certificate = dict(certificate)
        student = db.query_one("SELECT full_name, university, stream FROM students WHERE id = ?", (certificate['student_id'],))
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
        student = db.query_one("SELECT full_name, university, stream FROM students WHERE id = ?", (certificate.get('student_id'),))
        if student:
            student = dict(student)
            certificate['full_name'] = student.get('full_name', '')
            certificate['university'] = student.get('university', '')
            certificate['stream'] = student.get('stream', '')
        
        from flask import request
        from core.helpers import generate_qr_data_uri
        from core.certificate_image_generator import generate_certificate_image_sync
        verify_url = f"{request.host_url}verify/{certificate.get('verification_token', '')}"
        qr_data_uri = generate_qr_data_uri(verify_url)
        
        html = render_template('student_certificate.html', certificate=certificate, qr_data_uri=qr_data_uri)
        return html
    return {"success": False, "error": "Certificate not found"}
