"""
UNIYO LMS - Admin Certificate Management Routes
Provides additional certificate management endpoints
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, session
from datetime import datetime

from core.db import get_db
from core.auth import admin_required
from core.certificate_generator import (
    generate_certificate,
    verify_certificate,
    revoke_certificate,
    issue_bulk_certificates
)
from core.helpers import logger

admin_certificates_bp = Blueprint('admin_certificates', __name__, url_prefix='/admin/certificates-v2')

# ============================================
# LIST CERTIFICATES
# ============================================

@admin_certificates_bp.route('/', methods=['GET'])
@admin_required
def index():
    """View all certificates"""
    db = get_db()
    certificates = db.query('''
        SELECT c.*, s.full_name as student_name, s.university
        FROM certificates c
        JOIN students s ON c.student_id = s.id
        ORDER BY c.issue_date DESC
    ''')
    
    return render_template('admin/certificates.html', certificates=certificates)

# ============================================
# ISSUE CERTIFICATE FORM
# ============================================

@admin_certificates_bp.route('/issue', methods=['GET', 'POST'])
@admin_required
def issue():
    """Issue a certificate to a student"""
    db = get_db()
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        certificate_type = request.form.get('certificate_type', 'completion')
        title = request.form.get('title', 'Certificate')
        rank = request.form.get('rank') or None
        month_year = request.form.get('month_year') or None
        
        try:
            cert_data = generate_certificate(
                int(student_id),
                certificate_type,
                title,
                rank,
                month_year,
                session.get('admin_id')
            )
            flash(f"Certificate issued successfully! Number: {cert_data['certificate_number']}", 'success')
            return redirect(url_for('admin_certificates.index'))
        except Exception as e:
            flash(f"Error issuing certificate: {str(e)}", 'danger')
    
    # GET: Show form
    students = db.query("SELECT id, full_name, phone FROM students ORDER BY full_name")
    
    return render_template('admin/issue_certificate.html', students=students)

# ============================================
# BULK ISSUE CERTIFICATES
# ============================================

@admin_certificates_bp.route('/bulk-issue', methods=['POST'])
@admin_required
def bulk_issue():
    """Issue certificates to multiple students"""
    db = get_db()
    
    student_ids = request.form.getlist('student_ids')
    certificate_type = request.form.get('certificate_type', 'completion')
    title = request.form.get('title', 'Certificate')
    
    try:
        certificates = issue_bulk_certificates(
            [int(sid) for sid in student_ids],
            certificate_type,
            title
        )
        flash(f"Issued {len(certificates)} certificates", 'success')
    except Exception as e:
        flash(f"Error issuing certificates: {str(e)}", 'danger')
    
    return redirect(url_for('admin_certificates.index'))

# ============================================
# VIEW CERTIFICATE
# ============================================

@admin_certificates_bp.route('/view/<certificate_id>', methods=['GET'])
@admin_required
def view(certificate_id):
    """View certificate details"""
    db = get_db()
    
    cert = db.query_one('''
        SELECT c.*, s.full_name as student_name, s.university, s.stream
        FROM certificates c
        JOIN students s ON c.student_id = s.id
        WHERE c.certificate_number = ? OR c.id = ?
    ''', (certificate_id, certificate_id))
    
    if not cert:
        flash('Certificate not found', 'danger')
        return redirect(url_for('admin_certificates.index'))
    
    from core.helpers import generate_qr_data_uri
    
    cert = dict(cert)
    verify_url = f"{request.host_url}verify/{cert.get('verification_token', '')}"
    qr_data_uri = generate_qr_data_uri(verify_url)
    
    return render_template('admin_certificate_view.html', certificate=cert, qr_data_uri=qr_data_uri)

# ============================================
# REVOKE CERTIFICATE
# ============================================

@admin_certificates_bp.route('/revoke/<certificate_id>', methods=['POST'])
@admin_required
def revoke(certificate_id):
    """Revoke a certificate"""
    try:
        revoke_certificate(certificate_id)
        flash('Certificate revoked successfully', 'success')
    except Exception as e:
        flash(f'Error revoking certificate: {str(e)}', 'danger')
    
    return redirect(url_for('admin_certificates.index'))

# ============================================
# DOWNLOAD CERTIFICATE
# ============================================

@admin_certificates_bp.route('/download/<certificate_id>', methods=['GET'])
@admin_required
def download(certificate_id):
    """Download certificate image"""
    from core.paths import CERTIFICATE_QR_DIR
    
    qr_path = CERTIFICATE_QR_DIR / f"{certificate_id}.png"
    
    if qr_path.exists():
        return send_file(str(qr_path), as_attachment=True)
    
    flash('Certificate file not found', 'danger')
    return redirect(url_for('admin_certificates.index'))
