"""
UNIYO LMS - Admin Certificate Management Routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from core.db import db
from core.certificate_generator import (
    generate_certificate,
    verify_certificate,
    revoke_certificate,
    issue_bulk_certificates
)
from core.validators import admin_required
from datetime import datetime

admin_certificates_bp = Blueprint('admin_certificates', __name__, url_prefix='/admin/certificates')

# ============================================
# LIST CERTIFICATES
# ============================================

@admin_certificates_bp.route('/')
@login_required
@admin_required
def index():
    """View all certificates"""
    certificates = db.query("""
        SELECT 
            c.*,
            u.full_name as student_name,
            cr.title as course_name
        FROM certificates c
        JOIN users u ON c.student_id = u.id
        JOIN courses cr ON c.course_id = cr.id
        ORDER BY c.issue_date DESC
    """)
    
    return render_template('admin/certificates.html', certificates=certificates)

# ============================================
# ISSUE CERTIFICATE FORM
# ============================================

@admin_certificates_bp.route('/issue', methods=['GET', 'POST'])
@login_required
@admin_required
def issue():
    """Issue a certificate to a student"""
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        course_id = request.form.get('course_id')
        grade = request.form.get('grade', 'Pass')
        instructor_name = request.form.get('instructor_name', current_user.full_name)
        
        try:
            cert_data = generate_certificate(
                int(student_id),
                int(course_id),
                grade,
                instructor_name
            )
            flash(f"Certificate issued successfully! ID: {cert_data['certificate_id']}", 'success')
            return redirect(url_for('admin_certificates.index'))
        except Exception as e:
            flash(f"Error issuing certificate: {str(e)}", 'danger')
    
    # GET: Show form
    students = db.query("SELECT id, full_name, email FROM users WHERE role = 'student' ORDER BY full_name")
    courses = db.query("SELECT id, title FROM courses ORDER BY title")
    
    return render_template('admin/issue_certificate.html', 
                         students=students, 
                         courses=courses)

# ============================================
# BULK ISSUE CERTIFICATES
# ============================================

@admin_certificates_bp.route('/bulk-issue', methods=['POST'])
@login_required
@admin_required
def bulk_issue():
    """Issue certificates to all students who completed a course"""
    course_id = request.form.get('course_id')
    grade = request.form.get('grade', 'Pass')
    instructor_name = request.form.get('instructor_name', current_user.full_name)
    
    try:
        certificates = issue_bulk_certificates(
            int(course_id),
            grade,
            instructor_name
        )
        flash(f"Issued {len(certificates)} certificates for course", 'success')
    except Exception as e:
        flash(f"Error issuing certificates: {str(e)}", 'danger')
    
    return redirect(url_for('admin_certificates.index'))

# ============================================
# VIEW CERTIFICATE
# ============================================

@admin_certificates_bp.route('/view/<certificate_id>')
@login_required
@admin_required
def view(certificate_id):
    """View certificate details"""
    cert = db.query_one("""
        SELECT 
            c.*,
            u.full_name as student_name,
            u.email as student_email,
            cr.title as course_name
        FROM certificates c
        JOIN users u ON c.student_id = u.id
        JOIN courses cr ON c.course_id = cr.id
        WHERE c.certificate_id = ?
    """, (certificate_id,))
    
    if not cert:
        flash('Certificate not found', 'danger')
        return redirect(url_for('admin_certificates.index'))
    
    return render_template('admin/view_certificate.html', cert=cert)

# ============================================
# REVOKE CERTIFICATE
# ============================================

@admin_certificates_bp.route('/revoke/<certificate_id>', methods=['POST'])
@login_required
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

@admin_certificates_bp.route('/download/<certificate_id>')
@login_required
def download(certificate_id):
    """Download certificate PDF"""
    cert = db.query_one(
        "SELECT pdf_path FROM certificates WHERE certificate_id = ?",
        (certificate_id,)
    )
    
    if not cert or not cert['pdf_path']:
        flash('Certificate file not found', 'danger')
        return redirect(url_for('admin_certificates.index'))
    
    from core.paths import BASE_DIR
    pdf_path = BASE_DIR / cert['pdf_path']
    
    if not pdf_path.exists():
        flash('Certificate file not found on server', 'danger')
        return redirect(url_for('admin_certificates.index'))
    
    return send_file(str(pdf_path), as_attachment=True)
