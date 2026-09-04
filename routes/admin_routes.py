"""
UNIYO LMS - Admin Routes Blueprint
"""

from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from datetime import datetime, timedelta
from pathlib import Path

from core.db import get_db
from core.auth import admin_required, role_required, authenticate_admin, create_admin_session, terminate_admin_session
from core.helpers import logger, hash_password, verify_password, generate_certificate_number, generate_verification_token
from core.constants import ADMIN_ROLES
from routes.vip_routes import get_monthly_leaderboard

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'admin_id' in session:
        return redirect(url_for('admin.home'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        admin, message = authenticate_admin(username, password)
        
        if not admin:
            flash(message, "danger")
            return redirect(url_for('admin.login'))
        
        create_admin_session(admin['id'], request)
        
        db = get_db()
        db.execute('''
            INSERT INTO audit_logs (admin_id, action, target_table, details, ip_address, created_at)
            VALUES (?, 'LOGIN', 'admins', ?, ?, ?)
        ''', (admin['id'], f"Admin {admin['full_name']} logged in", request.remote_addr, datetime.now().isoformat()))
        
        flash(f"Welcome, {admin['full_name']}!", "success")
        return redirect(url_for('admin.home'))
    
    return render_template('admin_login.html')

@admin_bp.route('/logout', methods=['GET'])
@admin_required
def logout():
    terminate_admin_session()
    flash("Logged out successfully.", "success")
    return redirect(url_for('admin.login'))

@admin_bp.route('/home', methods=['GET'])
@admin_required
def home():
    db = get_db()
    admin = db.query_one("SELECT * FROM admins WHERE id = ?", (session['admin_id'],))
    admin = dict(admin) if admin else None
    
    stats = {
        'total_students': db.query_value("SELECT COUNT(*) FROM students"),
        'premium_students': db.query_value("SELECT COUNT(*) FROM students WHERE subscription_status = 'premium'"),
        'pending_payments': db.query_value("SELECT COUNT(*) FROM payments WHERE payment_status = 'pending'"),
        'total_revenue': db.query_value("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE payment_status = 'approved'"),
        'total_lessons': db.query_value("SELECT COUNT(*) FROM lessons WHERE is_active = 1"),
        'total_worksheets': db.query_value("SELECT COUNT(*) FROM worksheets WHERE is_active = 1"),
    }
    
    return render_template('admin_home.html', admin=admin, stats=stats, admin_roles=ADMIN_ROLES)

@admin_bp.route('/content', methods=['GET'])
@admin_required
def content_management():
    db = get_db()
    lessons = db.query("SELECT * FROM lessons ORDER BY chapter_number, part_number")
    worksheets = db.query("SELECT * FROM worksheets ORDER BY chapter_number")
    # ALL VIPs (scanned - for scheduler badge)
    all_vip_questions = db.query("SELECT * FROM vip_questions ORDER BY chapter_number, week_number")
    
    # SCHEDULED VIPs only (for block - has start_time)
    vip_questions = db.query("SELECT * FROM vip_questions WHERE start_time IS NOT NULL AND start_time != '' ORDER BY chapter_number, week_number")
    
    # Past Exams
    past_exams = db.query("SELECT * FROM past_exams ORDER BY year DESC")
    
    # Count UNSCHEDULED VIPs
    pending_vips = db.query_value("SELECT COUNT(*) FROM vip_questions WHERE start_time IS NULL OR start_time = ''")
    
    # Get VIP stats (attempts, scores)
    vip_stats = {}
    for vip in vip_questions:
        attempts = db.query_value(
            "SELECT COUNT(*) FROM vip_attempts WHERE vip_question_id = ?",
            (vip['id'],)
        )
        best_score = db.query_one(
            "SELECT MAX(score) as best, MAX(total) as total FROM vip_attempts WHERE vip_question_id = ?",
            (vip['id'],)
        )
        leaderboard = []
        
        vip_stats[vip['id']] = {
            'attempts': attempts or 0,
            'best_score': best_score['best'] if best_score else None,
            'total': best_score['total'] if best_score else None,
            'leaderboard': leaderboard
        }
    
    # Count pending VIPs (inactive)
    pending_vips = db.query_value("SELECT COUNT(*) FROM vip_questions WHERE is_active = 0")
    
    # Count active VIPs
    active_vips_count = db.query_value("SELECT COUNT(*) FROM vip_questions WHERE is_active = 1")
    
    # Count total attempts across all VIPs
    total_attempts = db.query_value("SELECT COUNT(*) FROM vip_attempts")
    
    return render_template('admin_content.html', past_exams=past_exams, lessons=lessons, worksheets=worksheets, vip_questions=vip_questions, all_vip_questions=all_vip_questions, vip_stats=vip_stats, pending_vips=pending_vips, active_vips_count=active_vips_count, total_attempts=total_attempts)

@admin_bp.route('/content/scan', methods=['POST'])
@admin_required
def scan_content():
    from init_database import scan_content_folder
    from core.db import Database
    
    # Use a FRESH database connection
    db = Database()
    db.connect()
    
    try:
        added = scan_content_folder(db)
        db.checkpoint()
        flash(f"Scan complete! Added {added} new files.", "success")
    except Exception as e:
        flash(f"Scan error: {e}", "danger")
    finally:
        db.close()
    
    return redirect(url_for('admin.content_management'))

@admin_bp.route('/content/lesson/<int:lesson_id>/publish', methods=['POST'])
@admin_required
def publish_lesson(lesson_id):
    db = get_db()
    db.execute("UPDATE lessons SET is_active = 1 WHERE id = ?", (lesson_id,))
    flash("Lesson published!", "success")
    return redirect(url_for('admin.content_management'))

@admin_bp.route('/payments', methods=['GET'])
@admin_required
def payments():
    db = get_db()
    payments_list = db.query('''
        SELECT p.*, s.full_name, s.phone, s.telegram_username, s.university
        FROM payments p JOIN students s ON p.student_id = s.id
        ORDER BY CASE p.payment_status WHEN 'pending' THEN 0 ELSE 1 END, p.submitted_at DESC
    ''')
    return render_template('admin_payments.html', payments=payments_list)

@admin_bp.route('/payments/<int:payment_id>/approve', methods=['POST'])
@admin_required
def approve_payment(payment_id):
    db = get_db()
    payment = db.query_one("SELECT * FROM payments WHERE id = ?", (payment_id,))
    if not payment:
        flash("Payment not found", "danger")
        return redirect(url_for('admin.payments'))
    
    db.execute("UPDATE payments SET payment_status = 'approved', reviewed_at = ?, reviewed_by = ? WHERE id = ?", (datetime.now().isoformat(), session['admin_id'], payment_id))
    
    subscription_expires = (datetime.now() + timedelta(days=365)).isoformat()
    db.execute("UPDATE students SET subscription_status = 'premium', subscription_expires = ? WHERE id = ?", (subscription_expires, payment['student_id']))
    
    db.execute('''
        INSERT INTO notifications (student_id, message, type, created_at)
        VALUES (?, 'Your payment has been approved! You now have premium access.', 'payment', ?)
    ''', (payment['student_id'], datetime.now().isoformat()))
    
    # Send Telegram notification to student
    try:
        from core.telegram_bot import notify_student_approved
        student = db.query_one("SELECT * FROM students WHERE id = ?", (payment['student_id'],))
        if student and student['telegram_username']:
            # Note: We need telegram_id, not username
            # Bot can't send to username directly, only chat_id
            pass
    except:
        pass
    
    # Check if receipt should be skipped
    skip_receipt = request.form.get('skip_receipt', '0')
    
    if skip_receipt == '1':
        flash("Payment approved (receipt skipped)", "success")
        return redirect(url_for('admin.payments'))
    

    # Check if receipt should be skipped
    

    # Check if receipt should be skipped
    

    # Auto-generate payment receipt certificate
    try:
        from core.helpers import generate_certificate_number, generate_verification_token
        cert_number = generate_certificate_number()
        token = generate_verification_token()
        
        student_info = db.query_one("SELECT full_name, university, phone FROM students WHERE id = ?", (payment['student_id'],))
        if student_info:
            student_info = dict(student_info)
        
        db.execute('''
            INSERT INTO certificates (student_id, certificate_type, certificate_number, verification_token, title, issue_date, full_name, university, phone, amount, payment_method, transaction_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (payment['student_id'], 'payment', cert_number, token, 'Payment Receipt', datetime.now().isoformat(), student_info.get('full_name', ''), student_info.get('university', ''), student_info.get('phone', ''), 200, payment['payment_method'], payment['transaction_number']))
        
        flash("Payment approved and receipt issued!", "success")
    except Exception as e:
        flash("Payment approved but receipt failed: " + str(e), "warning")
    
    return redirect(url_for('admin.payments'))

@admin_bp.route('/payments/<int:payment_id>/reject', methods=['POST'])
@admin_required
def reject_payment(payment_id):
    db = get_db()
    rejection_reason = request.form.get('rejection_reason', 'No reason provided')
    payment = db.query_one("SELECT * FROM payments WHERE id = ?", (payment_id,))
    
    db.execute("UPDATE payments SET payment_status = 'rejected', reviewed_at = ?, reviewed_by = ?, rejection_reason = ? WHERE id = ?", (datetime.now().isoformat(), session['admin_id'], rejection_reason, payment_id))
    db.execute("UPDATE students SET subscription_status = 'free' WHERE id = ?", (payment['student_id'],))
    
    db.execute('''
        INSERT INTO notifications (student_id, message, type, created_at)
        VALUES (?, ?, 'payment', ?)
    ''', (payment['student_id'], f'Your payment was rejected. Reason: {rejection_reason}', datetime.now().isoformat()))
    
    flash("Payment rejected.", "warning")
    return redirect(url_for('admin.payments'))

@admin_bp.route('/students', methods=['GET'])
@admin_required
def students():
    db = get_db()
    students_list = db.query("SELECT * FROM students ORDER BY created_at DESC")
    return render_template('admin_students.html', students=students_list)

@admin_bp.route('/students/<int:student_id>/toggle', methods=['POST'])
@admin_required
def toggle_student(student_id):
    db = get_db()
    student = db.query_one("SELECT * FROM students WHERE id = ?", (student_id,))
    new_status = 0 if student['is_active'] == 1 else 1
    db.execute("UPDATE students SET is_active = ? WHERE id = ?", (new_status, student_id))
    flash(f"Student {'activated' if new_status == 1 else 'deactivated'}.", "success")
    return redirect(url_for('admin.students'))

@admin_bp.route('/certificates', methods=['GET'])
@admin_required
def certificates():
    db = get_db()
    certificates_list = db.query('''
        SELECT c.*, s.full_name, s.university FROM certificates c
        JOIN students s ON c.student_id = s.id ORDER BY c.issue_date DESC
    ''')
    all_students = db.query("SELECT id, full_name, phone FROM students ORDER BY full_name")
    return render_template('admin_certificates.html', certificates=certificates_list, all_students=all_students, current_month=datetime.now().strftime('%Y-%m'))

@admin_bp.route('/announcements', methods=['GET'])
@admin_required
def announcements():
    db = get_db()
    announcements_list = db.query("SELECT * FROM announcements ORDER BY created_at DESC")
    return render_template('admin_announcements.html', announcements=announcements_list)

@admin_bp.route('/announcements/create', methods=['POST'])
@admin_required
def create_announcement():
    db = get_db()
    title = request.form.get('title', '')
    message = request.form.get('message', '')
    priority = request.form.get('priority', 'normal')
    
    if not title or not message:
        flash("Title and message are required", "danger")
        return redirect(url_for('admin.announcements'))
    
    db.execute('''
        INSERT INTO announcements (title, message, priority, is_active, created_at)
        VALUES (?, ?, ?, 1, ?)
    ''', (title, message, priority, datetime.now().isoformat()))
    
    flash("Announcement posted!", "success")
    return redirect(url_for('admin.announcements'))

@admin_bp.route('/content/lesson/<int:lesson_id>/unpublish', methods=['POST'])
@admin_required
def unpublish_lesson(lesson_id):
    db = get_db()
    db.execute("UPDATE lessons SET is_active = 0 WHERE id = ?", (lesson_id,))
    flash("Lesson unpublished.", "warning")
    return redirect(url_for('admin.content_management'))

@admin_bp.route('/content/worksheet/<int:worksheet_id>/publish', methods=['POST'])
@admin_required
def publish_worksheet(worksheet_id):
    db = get_db()
    db.execute("UPDATE worksheets SET is_active = 1 WHERE id = ?", (worksheet_id,))
    flash("Worksheet published!", "success")
    return redirect(url_for('admin.content_management'))

@admin_bp.route('/content/worksheet/<int:worksheet_id>/unpublish', methods=['POST'])
@admin_required
def unpublish_worksheet(worksheet_id):
    db = get_db()
    db.execute("UPDATE worksheets SET is_active = 0 WHERE id = ?", (worksheet_id,))
    flash("Worksheet unpublished.", "warning")
    return redirect(url_for('admin.content_management'))

# ============================================
# VIP QUESTION MANAGEMENT
# ============================================

@admin_bp.route('/vip/schedule', methods=['POST'])
@admin_required
def schedule_vip():
    """Schedule or update VIP question timing"""
    db = get_db()
    
    vip_id = request.form.get('vip_id')
    start_date = request.form.get('start_date')
    start_time = request.form.get('start_time')
    duration_hours = request.form.get('duration_hours')
    month_number = request.form.get('month_number', 1)
    
    if not start_date or not start_time or not duration_hours:
        flash("Please provide date, time, and duration", "danger")
        return redirect(url_for('admin.content_management'))
    
    try:
        # Combine date and time
        start_str = f"{start_date} {start_time}"
        start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
        duration = int(duration_hours)
        end_dt = start_dt + timedelta(hours=duration)
        
        if vip_id:
            # Update existing
            db.execute('''
                UPDATE vip_questions 
                SET start_time = ?, end_time = ?, duration_hours = ?, is_active = 1
                WHERE id = ?
            ''', (start_dt.isoformat(), end_dt.isoformat(), duration, vip_id))
            flash(f"VIP question updated! Starts: {start_dt.strftime('%B %d at %I:%M %p')}", "success")
        else:
            # Create new
            course_code = request.form.get('course_code', 'Econ1011')
            week_number = request.form.get('week_number', 1)
            title = request.form.get('title', f'VIP Week {week_number}')
            question_file = request.form.get('question_file', f'VIP_{course_code}_week{week_number}.json')
            
            db.execute('''
                INSERT INTO vip_questions (course_code, week_number, month_number, title, question_file, start_time, end_time, duration_hours, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            ''', (course_code, week_number, month_number, title, question_file, start_dt.isoformat(), end_dt.isoformat(), duration, datetime.now().isoformat()))
            flash(f"VIP question scheduled! Starts: {start_dt.strftime('%B %d at %I:%M %p')}", "success")
        
    except Exception as e:
        flash(f"Error scheduling VIP: {e}", "danger")
    
    return redirect(url_for('admin.content_management'))

@admin_bp.route('/vip/<int:vip_id>/toggle', methods=['POST'])
@admin_required
def toggle_vip(vip_id):
    """Toggle VIP question active status"""
    db = get_db()
    
    vip = db.query_one("SELECT * FROM vip_questions WHERE id = ?", (vip_id,))
    if vip:
        new_status = 0 if vip['is_active'] == 1 else 1
        db.execute("UPDATE vip_questions SET is_active = ? WHERE id = ?", (new_status, vip_id))
        flash(f"VIP question {'activated' if new_status == 1 else 'deactivated'}.", "success")
    
    return redirect(url_for('admin.content_management'))

@admin_bp.route('/vip/<int:vip_id>/delete', methods=['POST'])
@admin_required
def delete_vip(vip_id):
    """Delete VIP question"""
    db = get_db()
    
    vip = db.query_one("SELECT * FROM vip_questions WHERE id = ?", (vip_id,))
    if vip:
        db.execute("DELETE FROM vip_attempts WHERE vip_question_id = ?", (vip_id,))
        db.execute("DELETE FROM vip_questions WHERE id = ?", (vip_id,))
        flash(f"VIP question deleted: {vip['title']}", "warning")
    
    return redirect(url_for('admin.content_management'))

@admin_bp.route('/vip/<int:vip_id>/unschedule', methods=['POST'])
@admin_required
def unschedule_vip(vip_id):
    """Remove VIP from block (unschedule) but keep in database for re-scheduling"""
    db = get_db()
    
    vip = db.query_one("SELECT * FROM vip_questions WHERE id = ?", (vip_id,))
    if vip:
        db.execute("UPDATE vip_questions SET is_active = 0, start_time = NULL, end_time = NULL WHERE id = ?", (vip_id,))
        flash(f"VIP unscheduled: {vip['title']}. It can be re-scheduled anytime.", "warning")
    
    return redirect(url_for('admin.content_management'))

@admin_bp.route('/content/past-exam/<int:exam_id>/publish', methods=['POST'])
@admin_required
def publish_past_exam(exam_id):
    db = get_db()

    exam = db.query_one("SELECT id FROM past_exams WHERE id = ?", (exam_id,))
    if not exam:
        flash("Exam not found!", "danger")
        return redirect(url_for('admin.content_management'))

    description = request.form.get('description', '')
    about = request.form.get('about', '')
    topics_covered = request.form.get('topics_covered', '')
    difficulty_level = request.form.get('difficulty_level', 'Medium')
    marks_description = request.form.get('marks_description', '')

    try:
        time_limit_minutes = int(request.form.get('time_limit_minutes', 120))
    except:
        time_limit_minutes = 120

    try:
        total_questions = int(request.form.get('total_questions', 0))
    except:
        total_questions = 0

    try:
        semester = int(request.form.get('semester', 1))
    except:
        semester = 1

    db.execute('''
        UPDATE past_exams
        SET is_active = 1,
            description = ?,
            about = ?,
            topics_covered = ?,
            difficulty_level = ?,
            time_limit_minutes = ?,
            total_questions = ?,
            semester = ?,
            marks_description = ?
        WHERE id = ?
    ''', (description, about, topics_covered, difficulty_level, time_limit_minutes, total_questions, semester, marks_description, exam_id))

    flash("Past exam published successfully!", "success")
    return redirect(url_for('admin.content_management'))

@admin_bp.route('/content/past-exam/<int:exam_id>/unpublish', methods=['POST'])
@admin_required
def unpublish_past_exam(exam_id):
    db = get_db()
    db.execute("UPDATE past_exams SET is_active = 0 WHERE id = ?", (exam_id,))
    flash("Past exam unpublished.", "warning")
    return redirect(url_for('admin.content_management'))


# ============================================
# ADMIN PASSWORD CHANGE
# ============================================

@admin_bp.route('/change-password', methods=['POST'])
@admin_required
def change_password():
    """Change admin password"""
    db = get_db()
    
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    admin = db.query_one("SELECT * FROM admins WHERE id = ?", (session['admin_id'],))
    
    if not admin:
        flash("Admin not found", "danger")
        return redirect(url_for('admin.home'))
    
    admin = dict(admin)
    if not verify_password(admin['password_hash'], current_password):
        flash("Current password is incorrect", "danger")
        return redirect(url_for('admin.home'))
    
    if len(new_password) < 8:
        flash("New password must be at least 8 characters", "danger")
        return redirect(url_for('admin.home'))
    
    if new_password != confirm_password:
        flash("New passwords do not match", "danger")
        return redirect(url_for('admin.home'))
    
    new_hash = hash_password(new_password)
    update_sql = "UPDATE admins SET password_hash = '" + new_hash + "', must_change_password = 0 WHERE id = " + str(session['admin_id'])
    db.execute(update_sql)
    
    audit_query = "INSERT INTO audit_logs (admin_id, action, target_table, target_id, details, created_at) VALUES (?, 'CHANGE_PASSWORD', 'admins', ?, 'Admin changed password', ?)"
    db.execute(audit_query, (session['admin_id'], session['admin_id'], datetime.now().isoformat()))
    
    flash("Password changed successfully!", "success")
    return redirect(url_for('admin.home'))


@admin_bp.route('/certificates/issue', methods=['POST'])
@admin_required
def issue_certificate():
    """Issue a new certificate to a student"""
    db = get_db()
    
    student_id = request.form.get('student_id')
    certificate_type = request.form.get('certificate_type', 'completion')
    title = request.form.get('title', 'Course Completion Certificate')
    rank = request.form.get('rank', None)
    month_year = request.form.get('month_year', None)
    
    if not student_id:
        flash("Please select a student", "danger")
        return redirect(url_for('admin.certificates'))
    
    # For VIP certificates, validate the rank against the actual monthly leaderboard
    # For VIP certificates, validate the rank against the actual monthly leaderboard
    vip_types = ['vip_leaderboard']
    if certificate_type in vip_types:
        if not month_year:
            flash("Month/Year is required for VIP certificates", "danger")
            return redirect(url_for('admin.certificates'))
        
        try:
            leaderboard = get_monthly_leaderboard(month_year)
            actual_rank = None
            for entry in leaderboard:
                if str(entry.get('student_id')) == str(student_id):
                    actual_rank = entry.get('rank')
                    break
            
            if actual_rank is None:
                flash("This student is not in the VIP leaderboard for this month", "danger")
                return redirect(url_for('admin.certificates'))
            
            rank = actual_rank
            flash(f"Rank auto-validated: #{rank} from leaderboard", "info")
        except Exception as e:
            flash(f"Could not validate rank: {e}", "warning")
    elif certificate_type in ['content_creator', 'marketing_manager', 'advertiser', 'staff', 'special_congratulations', 'excellence']:
        # These types don't require rank or month - admin can issue freely
        rank = request.form.get('rank', None) or None
    else:
        rank = None
    
    certificate_number = generate_certificate_number(month_year, rank)
    verification_token = generate_verification_token()
    
    # Get student details for the certificate
    student = db.query_one("SELECT full_name, university, stream FROM students WHERE id = ?", (student_id,))
    student = dict(student) if student else {}
    
    sql = "INSERT INTO certificates (student_id, certificate_type, rank, month_year, certificate_number, verification_token, title, issue_date, issued_by, full_name, university, stream) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    db.execute(sql, (student_id, certificate_type, rank, month_year, certificate_number, verification_token, title, datetime.now().isoformat(), session['admin_id'], student.get('full_name', ''), student.get('university', ''), student.get('stream', '')))
    
    sql2 = "INSERT INTO notifications (student_id, message, type, created_at) VALUES (?, 'You have received a new certificate!', 'certificate', ?)"
    db.execute(sql2, (student_id, datetime.now().isoformat()))
    
    flash("Certificate issued successfully!", "success")
    return redirect(url_for('admin.certificates'))


@admin_bp.route('/certificates/<int:certificate_id>/preview', methods=['GET'])
@admin_required
def preview_certificate(certificate_id):
    """Admin certificate preview with 3D tilt"""
    db = get_db()
    certificate = db.query_one("SELECT * FROM certificates WHERE id = ?", (certificate_id,))
    
    if not certificate:
        flash("Certificate not found", "danger")
        return redirect(url_for('admin.certificates'))
    
    certificate = dict(certificate)
    student = db.query_one("SELECT full_name, university, stream FROM students WHERE id = ?", (certificate.get('student_id'),))
    if student:
        student = dict(student)
        certificate['full_name'] = student.get('full_name', '')
        certificate['university'] = student.get('university', '')
        certificate['stream'] = student.get('stream', '')
    
    from flask import request
    from core.helpers import generate_qr_data_uri
    verify_url = f"{request.host_url}verify/{certificate.get('verification_token', '')}"
    qr_data_uri = generate_qr_data_uri(verify_url)
    
    return render_template('admin_certificate_preview.html', certificate=certificate, qr_data_uri=qr_data_uri)


@admin_bp.route('/certificates/<int:certificate_id>/view', methods=['GET'])
@admin_required
def view_certificate(certificate_id):
    """Admin view certificate"""
    db = get_db()
    try:
        certificate = db.query_one("SELECT * FROM certificates WHERE id = ?", (certificate_id,))
        if certificate:
            certificate = dict(certificate)
            student = db.query_one("SELECT full_name, university, stream FROM students WHERE id = ?", (certificate.get('student_id'),))
            if student:
                student = dict(student)
                certificate['full_name'] = student.get('full_name', '')
                certificate['university'] = student.get('university', '')
                certificate['stream'] = student.get('stream', '')
    except Exception as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for('admin.certificates'))
    
    if not certificate:
        flash("Certificate not found", "danger")
        return redirect(url_for('admin.certificates'))
    
    from flask import request
    from core.helpers import generate_qr_data_uri
    verify_url = f"{request.host_url}verify/{certificate.get('verification_token', '')}"
    qr_data_uri = generate_qr_data_uri(verify_url)
    
    return render_template('student_certificate.html', certificate=certificate, qr_data_uri=qr_data_uri)


@admin_bp.route('/api/certificates/<int:certificate_id>/image', methods=['GET'])
@admin_required
def api_certificate_image(certificate_id):
    """Serve full certificate as PNG image for admin viewing"""
    from flask import send_file
    from core.paths import CERTIFICATES_DIR
    
    db = get_db()
    certificate = db.query_one("SELECT * FROM certificates WHERE id = ?", (certificate_id,))
    
    if not certificate:
        return {"success": False, "error": "Certificate not found"}
    
    certificate = dict(certificate)
    
    # Check if PNG already exists
    cert_number = certificate.get('certificate_number', 'UNKNOWN')
    cert_id = cert_number.replace('/', '_').replace('\\', '_')
    image_path = CERTIFICATES_DIR / f"{cert_id}.png"
    
    if image_path.exists():
        return send_file(str(image_path), mimetype='image/png')
    
    # Generate if not exists
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
    
    image_path = generate_certificate_image_sync(certificate, qr_data_uri)
    
    if image_path and Path(image_path).exists():
        return send_file(str(image_path), mimetype='image/png')
    
    # Fallback: Generate with Pillow
    try:
        from PIL import Image, ImageDraw, ImageFont
        from core.paths import CERTIFICATES_DIR
        
        cert_number = certificate.get('certificate_number', 'UNKNOWN')
        cert_id = cert_number.replace('/', '_').replace('\\', '_')
        fallback_path = CERTIFICATES_DIR / f"{cert_id}_fallback.png"
        
        img = Image.new('RGB', (1240, 1748), '#fffdf9')
        draw = ImageDraw.Draw(img)
        
        draw.rectangle([20, 20, 1220, 1728], outline='#6D28D9', width=5)
        draw.rectangle([30, 30, 1210, 1718], outline='#F59E0B', width=2)
        
        try:
            font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 60)
            font_medium = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 40)
            font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 30)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        title = certificate.get('title', 'Certificate')
        name = certificate.get('full_name', 'Student')
        university = certificate.get('university', '')
        cert_num = certificate.get('certificate_number', '')
        
        draw.text((620, 100), title, fill='#6D28D9', font=font_large, anchor='mm')
        draw.text((620, 300), 'This certificate is presented to', fill='#64748b', font=font_small, anchor='mm')
        draw.text((620, 400), name, fill='#1e1b4b', font=font_large, anchor='mm')
        draw.text((620, 500), university, fill='#64748b', font=font_medium, anchor='mm')
        draw.text((620, 700), f'Certificate Number: {cert_num}', fill='#334155', font=font_small, anchor='mm')
        
        img.save(str(fallback_path))
        
        if fallback_path.exists():
            return send_file(str(fallback_path), mimetype='image/png')
    except Exception as e:
        print(f"Admin fallback failed: {e}")
    
    return {"success": False, "error": "Could not generate certificate image"}


@admin_bp.route('/api/certificates/<int:certificate_id>', methods=['GET'])
@admin_required
def api_certificate(certificate_id):
    """API endpoint for certificate popup"""
    db = get_db()
    certificate = db.query_one("SELECT * FROM certificates WHERE id = ?", (certificate_id,))
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
        verify_url = f"{request.host_url}verify/{certificate.get('verification_token', '')}"
        qr_data_uri = generate_qr_data_uri(verify_url)
        
        html = render_template('student_certificate.html', certificate=certificate, qr_data_uri=qr_data_uri)
        return html
    return {"success": False, "error": "Certificate not found"}


@admin_bp.route('/certificates/<int:certificate_id>/delete', methods=['POST'])
@admin_required
def delete_certificate(certificate_id):
    """Delete a certificate"""
    db = get_db()
    cert = db.query_one("SELECT * FROM certificates WHERE id = ?", (certificate_id,))
    if cert:
        cert = dict(cert)
        db.execute("DELETE FROM certificates WHERE id = ?", (certificate_id,))
        flash("Certificate deleted", "success")
    else:
        flash("Certificate not found", "danger")
    return redirect(url_for('admin.certificates'))


@admin_bp.route('/payments/<int:payment_id>/issue-receipt', methods=['POST'])
@admin_required
def issue_receipt(payment_id):
    """Issue receipt for an already-approved payment"""
    db = get_db()
    payment = db.query_one("SELECT * FROM payments WHERE id = ?", (payment_id,))
    if not payment:
        flash("Payment not found", "danger")
        return redirect(url_for('admin.payments'))
    
    try:
        from core.helpers import generate_certificate_number, generate_verification_token
        cert_number = generate_certificate_number()
        token = generate_verification_token()
        
        student_info = db.query_one("SELECT full_name, university, phone FROM students WHERE id = ?", (payment['student_id'],))
        if student_info:
            student_info = dict(student_info)
        else:
            student_info = {}
        
        amount = request.form.get('amount', payment.get('amount', 200))
        receipt_method = request.form.get('payment_method', payment['payment_method'])
        receipt_transaction = request.form.get('transaction_number', payment['transaction_number'])
        receipt_title = request.form.get('title', 'Payment Receipt')
        
        db.execute('''
            INSERT INTO certificates (student_id, certificate_type, certificate_number, verification_token, title, issue_date, full_name, university, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (payment['student_id'], 'payment', cert_number, token, receipt_title, datetime.now().isoformat(), student_info.get('full_name', ''), student_info.get('university', ''), student_info.get('phone', '')))
        
        flash("Receipt issued successfully!", "success")
    except Exception as e:
        flash(f"Failed to issue receipt: {e}", "danger")
    
    return redirect(url_for('admin.payments'))
