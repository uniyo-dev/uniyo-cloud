"""
UNIYO LMS - Certificate Generation System
Handles certificate creation, verification, and management
Works with Turso database via get_db()
"""

import os
import qrcode
from datetime import datetime
from pathlib import Path

from core.paths import (
    CERTIFICATES_DIR,
    CERTIFICATE_QR_DIR,
    BASE_DIR
)
from core.db import get_db
from core.helpers import generate_certificate_number, generate_verification_token

# ============================================
# QR CODE GENERATION
# ============================================

def generate_qr_code(certificate_id, verification_url):
    """
    Generate QR code for certificate verification
    Returns: Path to QR code image
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    qr_filename = f"{certificate_id}.png"
    qr_path = CERTIFICATE_QR_DIR / qr_filename
    img.save(str(qr_path))
    
    return qr_path

# ============================================
# COMPLETE CERTIFICATE GENERATION
# ============================================

def generate_certificate(student_id, certificate_type="completion", title="Certificate", rank=None, month_year=None, issued_by=None):
    """
    Generate complete certificate (QR + database record)
    Returns: Certificate data dict
    """
    db = get_db()
    
    # Get student info
    student = db.query_one(
        "SELECT id, full_name, university, stream, phone FROM students WHERE id = ?",
        (student_id,)
    )
    
    if not student:
        raise ValueError("Student not found")
    
    student = dict(student)
    
    # Generate certificate identifiers
    certificate_number = generate_certificate_number(month_year, rank)
    verification_token = generate_verification_token()
    
    # Prepare verification URL
    verification_url = f"{os.getenv('APP_URL', 'http://localhost:5000')}/verify/{verification_token}"
    
    # Generate QR code
    qr_path = generate_qr_code(certificate_number, verification_url)
    
    # Insert into database
    db.execute('''
        INSERT INTO certificates (student_id, certificate_type, rank, month_year, certificate_number, verification_token, title, issue_date, issued_by, full_name, university, stream, phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        student_id,
        certificate_type,
        rank,
        month_year,
        certificate_number,
        verification_token,
        title,
        datetime.now().isoformat(),
        issued_by,
        student.get('full_name', ''),
        student.get('university', ''),
        student.get('stream', ''),
        student.get('phone', '')
    ))
    
    return {
        'certificate_id': certificate_number,
        'certificate_number': certificate_number,
        'verification_token': verification_token,
        'student_name': student.get('full_name', ''),
        'qr_path': str(qr_path),
        'verification_url': verification_url
    }

# ============================================
# CERTIFICATE VERIFICATION
# ============================================

def verify_certificate(certificate_identifier):
    """
    Verify certificate by number or token
    Returns: Certificate dict or None
    """
    db = get_db()
    
    result = db.query_one('''
        SELECT c.*, s.full_name, s.university, s.stream
        FROM certificates c
        JOIN students s ON c.student_id = s.id
        WHERE c.certificate_number = ? OR c.verification_token = ?
    ''', (certificate_identifier, certificate_identifier))
    
    if result:
        return dict(result)
    return None

# ============================================
# REVOKE CERTIFICATE
# ============================================

def revoke_certificate(certificate_id):
    """
    Revoke a certificate by ID
    Returns: True if successful
    """
    db = get_db()
    db.execute("DELETE FROM certificates WHERE id = ?", (certificate_id,))
    return True

# ============================================
# BULK CERTIFICATE ISSUANCE
# ============================================

def issue_bulk_certificates(student_ids, certificate_type="completion", title="Certificate", issued_by=None):
    """
    Generate certificates for multiple students
    Returns: List of certificate dicts
    """
    certificates = []
    for student_id in student_ids:
        try:
            cert = generate_certificate(student_id, certificate_type, title, issued_by=issued_by)
            certificates.append(cert)
        except Exception as e:
            print(f"Error generating certificate for student {student_id}: {e}")
    
    return certificates
