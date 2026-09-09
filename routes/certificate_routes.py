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
        "SELECT full_name, university, stream, sex, phone FROM students WHERE id = ?",
        (certificate['student_id'],)
    )
    if student:
        student = dict(student)
        certificate['full_name'] = student.get('full_name', certificate.get('full_name', ''))
        certificate['university'] = student.get('university', certificate.get('university', ''))
        certificate['stream'] = student.get('stream', certificate.get('stream', ''))
        certificate['sex'] = student.get('sex', certificate.get('sex', ''))
        certificate['phone'] = student.get('phone', certificate.get('phone', ''))
    
    # Generate QR code
    from flask import request
    from core.helpers import generate_qr_data_uri
    verify_url = f"{request.host_url}verify/{certificate['verification_token']}"
    qr_data_uri = generate_qr_data_uri(verify_url)
    
    # Generate certificate using ReportLab (Professional PDF)
    from core.certificate_reportlab import generate_certificate_reportlab
    pdf_path = generate_certificate_reportlab(certificate, qr_data_uri)
    
    if pdf_path and Path(pdf_path).exists():
        return send_file(str(pdf_path), mimetype='application/pdf')
    
    return {'success': False, 'error': 'Certificate generation failed'}, 500


@certificate_bp.route('/student/certificate/<int:certificate_id>/download', methods=['GET'])
@login_required
def download_certificate_image(certificate_id):
    """Download certificate as PDF"""
    from flask import send_file
    db = get_db()
    
    certificate = db.query_one(
        "SELECT * FROM certificates WHERE id = ? AND student_id = ?",
        (certificate_id, session['student_id'])
    )
    
    if not certificate:
        flash("Certificate not found", "danger")
        return redirect(url_for('certificate.my_certificates'))
    
    certificate = dict(certificate)
    
    # Get requested format
    format_type = request.args.get('format', 'pdf')
    
    # Generate PDF
    from core.certificate_reportlab import generate_certificate_reportlab
    pdf_path = generate_certificate_reportlab(certificate, None)
    
    if pdf_path and Path(pdf_path).exists():
        if format_type == 'pdf':
            return send_file(
                str(pdf_path),
                as_attachment=True,
                download_name=f"UNIYO_Certificate_{certificate_id}.pdf",
                mimetype='application/pdf'
            )
        elif format_type in ['jpg', 'jpeg', 'png']:
            # Convert PDF to image
            try:
                from pdf2image import convert_from_path
                images = convert_from_path(str(pdf_path), dpi=300)
                if images:
                    img_path = CERTIFICATES_DIR / f"{certificate_id}.{format_type}"
                    images[0].save(str(img_path), format_type.upper() if format_type == 'png' else 'JPEG', quality=95)
                    mimetype = 'image/jpeg' if format_type in ['jpg', 'jpeg'] else 'image/png'
                    return send_file(
                        str(img_path),
                        as_attachment=True,
                        download_name=f"UNIYO_Certificate_{certificate_id}.{format_type}",
                        mimetype=mimetype
                    )
            except Exception as e:
                print(f"PDF to image conversion failed: {e}")
    
    flash("Could not generate certificate", "danger")
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
