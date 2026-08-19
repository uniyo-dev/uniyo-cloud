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
    certificate = db.query_one('''
        SELECT c.*, s.full_name, s.university, s.stream FROM certificates c
        JOIN students s ON c.student_id = s.id WHERE c.id = ? AND c.student_id = ?
    ''', (certificate_id, session['student_id']))
    
    if not certificate:
        flash("Certificate not found", "danger")
        return redirect(url_for('certificate.my_certificates'))
    
    verify_url = f"http://192.168.43.1:5000/verify/{certificate['verification_token']}"
    qr_data_uri = generate_qr_data_uri(verify_url)
    
    return render_template('student_certificate.html', certificate=certificate, qr_data_uri=qr_data_uri)

@certificate_bp.route('/verify/<token>', methods=['GET'])
def verify_certificate(token):
    db = get_db()
    certificate = db.query_one('''
        SELECT c.*, s.full_name, s.university, s.stream FROM certificates c
        JOIN students s ON c.student_id = s.id WHERE c.verification_token = ?
    ''', (token,))
    
    if not certificate:
        return render_template('verification_invalid.html'), 404
    
    return render_template('verification_valid.html', certificate=certificate)
