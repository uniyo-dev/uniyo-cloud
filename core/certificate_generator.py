"""
UNIYO LMS - Certificate Generation System
Handles PDF creation, QR codes, and verification
"""

import os
import json
import qrcode
from datetime import datetime
from pathlib import Path
from flask import render_template, url_for, current_app
import sqlite3
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from core.paths import (
    CERTIFICATES_DIR,
    CERTIFICATE_PDF_DIR,
    CERTIFICATE_QR_DIR,
    BASE_DIR
)

# ============================================
# QR CODE GENERATION
# ============================================

def generate_qr_code(certificate_id, verification_url):
    """
    Generate QR code for certificate verification
    Returns: Path to QR code image
    """
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to file
    qr_filename = f"{certificate_id}.png"
    qr_path = CERTIFICATE_QR_DIR / qr_filename
    img.save(str(qr_path))
    
    return qr_path

# ============================================
# PDF CERTIFICATE GENERATION
# ============================================

def generate_pdf_certificate(certificate_data):
    """
    Generate PDF certificate from template
    certificate_data: dict with student, course, certificate info
    """
    # Prepare file path
    pdf_filename = f"{certificate_data['certificate_id']}.pdf"
    pdf_path = CERTIFICATE_PDF_DIR / pdf_filename
    
    # Create PDF
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=landscape(A4),
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Story list for PDF content
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=48,
        alignment=TA_CENTER,
        textColor=colors.Color(0.10, 0.14, 0.49),  # #1a237e
        spaceAfter=20
    )
    
    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Heading1'],
        fontSize=42,
        alignment=TA_CENTER,
        textColor=colors.Color(0.10, 0.14, 0.49),
        spaceAfter=30
    )
    
    course_style = ParagraphStyle(
        'CourseStyle',
        parent=styles['Heading2'],
        fontSize=28,
        alignment=TA_CENTER,
        textColor=colors.Color(0.05, 0.28, 0.63),  # #0d47a1
        spaceAfter=20
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=10
    )
    
    # Build PDF content
    story.append(Paragraph("🎓 CERTIFICATE OF COMPLETION", title_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("This certificate is presented to", body_style))
    story.append(Paragraph(certificate_data['student_name'], name_style))
    
    story.append(Paragraph("For successfully completing the course", body_style))
    story.append(Paragraph(certificate_data['course_name'], course_style))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        f"With a grade of <b>{certificate_data.get('grade', 'Pass')}</b> · Completed on {certificate_data['completion_date']}",
        body_style
    ))
    
    story.append(Spacer(1, 40))
    
    # Footer with signatures
    story.append(Paragraph(
        f"Instructor: {certificate_data.get('instructor_name', 'UNIYO LMS')}",
        body_style
    ))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        f"Certificate ID: {certificate_data['certificate_id']}",
        body_style
    ))
    story.append(Paragraph(
        f"Issued on: {certificate_data['issue_date']}",
        body_style
    ))
    
    # Build PDF
    doc.build(story)
    
    return pdf_path

# ============================================
# HTML CERTIFICATE GENERATION
# ============================================

def generate_html_certificate(certificate_data, qr_path):
    """
    Generate HTML version of certificate (for preview/email)
    """
    # Convert QR path to URL
    qr_url = f"/static/qr/{certificate_data['certificate_id']}.png"
    
    # Render template
    html_content = render_template(
        'certificate_template.html',
        student_name=certificate_data['student_name'],
        course_name=certificate_data['course_name'],
        completion_date=certificate_data['completion_date'],
        grade=certificate_data.get('grade', 'Pass'),
        instructor_name=certificate_data.get('instructor_name', 'UNIYO LMS'),
        certificate_id=certificate_data['certificate_id'],
        issue_date=certificate_data['issue_date'],
        verify_url=certificate_data['verification_url'],
        qr_code_url=qr_url
    )
    
    # Save HTML
    html_path = CERTIFICATES_DIR / f"{certificate_data['certificate_id']}.html"
    with open(html_path, 'w') as f:
        f.write(html_content)
    
    return html_path

# ============================================
# COMPLETE CERTIFICATE GENERATION
# ============================================

def generate_certificate(student_id, course_id, grade="Pass", instructor_name="UNIYO LMS"):
    """
    Generate complete certificate (QR + PDF + HTML)
    Returns: Certificate data dict
    """
    from core.db import db
    
    # Get student and course info
    student = db.query_one(
        "SELECT id, full_name, email FROM users WHERE id = ? AND role = 'student'",
        (student_id,)
    )
    
    course = db.query_one(
        "SELECT id, title FROM courses WHERE id = ?",
        (course_id,)
    )
    
    if not student or not course:
        raise ValueError("Student or course not found")
    
    # Generate certificate ID
    cert_id = f"UNIYO-{datetime.now().strftime('%Y%m')}-{student_id:04d}-{course_id:04d}"
    
    # Prepare data
    verification_url = f"{os.getenv('APP_URL', 'http://localhost:5000')}/verify/{cert_id}"
    
    certificate_data = {
        'certificate_id': cert_id,
        'student_name': student['full_name'],
        'student_email': student['email'],
        'course_name': course['title'],
        'completion_date': datetime.now().strftime('%B %d, %Y'),
        'issue_date': datetime.now().strftime('%B %d, %Y'),
        'grade': grade,
        'instructor_name': instructor_name,
        'verification_url': verification_url
    }
    
    # Generate QR code
    qr_path = generate_qr_code(cert_id, verification_url)
    
    # Generate PDF
    pdf_path = generate_pdf_certificate(certificate_data)
    
    # Generate HTML
    html_path = generate_html_certificate(certificate_data, qr_path)
    
    # Save to database
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO certificates (
            certificate_id,
            student_id,
            course_id,
            issue_date,
            pdf_path,
            qr_path,
            verification_url,
            status,
            grade
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cert_id,
        student_id,
        course_id,
        datetime.now().isoformat(),
        str(pdf_path),
        str(qr_path),
        verification_url,
        'active',
        grade
    ))
    conn.commit()
    
    return certificate_data

# ============================================
# CERTIFICATE VERIFICATION
# ============================================

def verify_certificate(certificate_id):
    """
    Verify certificate and return status
    """
    from core.db import db
    
    result = db.query_one(
        """
        SELECT c.*, u.full_name as student_name, cr.title as course_name
        FROM certificates c
        JOIN users u ON c.student_id = u.id
        JOIN courses cr ON c.course_id = cr.id
        WHERE c.certificate_id = ? AND c.status = 'active'
        """,
        (certificate_id,)
    )
    
    if result:
        return dict(result)
    return None

# ============================================
# REVOKE CERTIFICATE
# ============================================

def revoke_certificate(certificate_id):
    """
    Revoke a certificate
    """
    from core.db import db
    
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE certificates SET status = 'revoked' WHERE certificate_id = ?",
        (certificate_id,)
    )
    conn.commit()
    
    return cursor.rowcount > 0

# ============================================
# BULK CERTIFICATE ISSUANCE
# ============================================

def issue_bulk_certificates(course_id, grade="Pass", instructor_name="UNIYO LMS"):
    """
    Generate certificates for all students who completed a course
    """
    from core.db import db
    
    # Get all enrolled students who completed
    students = db.query(
        """
        SELECT u.id, u.full_name
        FROM enrollments e
        JOIN users u ON e.student_id = u.id
        WHERE e.course_id = ? AND e.status = 'completed'
        """,
        (course_id,)
    )
    
    certificates = []
    for student in students:
        try:
            cert = generate_certificate(
                student['id'],
                course_id,
                grade,
                instructor_name
            )
            certificates.append(cert)
        except Exception as e:
            print(f"Error generating certificate for {student['full_name']}: {e}")
    
    return certificates
