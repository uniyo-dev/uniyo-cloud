"""
UNIYO LMS - Certificate Viewing Routes
"""

from flask import Blueprint, render_template, redirect, url_for, session, flash
from core.db import get_db
from core.auth import login_required
from core.helpers import generate_qr_data_uri

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
        certificate = db.query_one("SELECT * FROM certificates WHERE id = ? AND student_id = ?", (certificate_id, session['student_id']))
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
    
    return render_template('stu_cert_view.html', certificate=certificate, qr_data_uri=qr_data_uri)

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
