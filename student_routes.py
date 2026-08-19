"""
UNIYO LMS - Student Routes Blueprint
"""

from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from datetime import datetime

from core.db import get_db
from core.auth import login_required, authenticate_student, create_student_session, terminate_student_session
from core.helpers import logger, hash_password, save_student_photo
from core.validators import validate_registration
from core.constants import UNIVERSITIES_LIST, UNIVERSITY_SHORT_NAMES

student_bp = Blueprint('student', __name__)

@student_bp.route('/', methods=['GET'])
def index():
    if 'student_id' in session:
        return redirect(url_for('student.home'))
    return redirect(url_for('student.login'))

@student_bp.route('/student/login', methods=['GET', 'POST'])
def login():
    if 'student_id' in session:
        return redirect(url_for('student.home'))
    
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')
        
        if not identifier or not password:
            flash("Please enter your phone number and password", "danger")
            return redirect(url_for('student.login'))
        
        student, message = authenticate_student(identifier, password)
        
        if not student:
            flash(message, "danger")
            return redirect(url_for('student.login'))
        
        success, session_message = create_student_session(student['id'], request)
        
        if not success:
            flash(session_message, "danger")
            return redirect(url_for('student.login'))
        
        db = get_db()
        db.execute('''
            UPDATE students SET last_login = ?, login_count = login_count + 1 WHERE id = ?
        ''', (datetime.now().isoformat(), student['id']))
        
        flash(f"Welcome back, {student['first_name']}!", "success")
        return redirect(url_for('student.home'))
    
    return render_template('student_login.html')

@student_bp.route('/student/register', methods=['GET', 'POST'])
def register():
    if 'student_id' in session:
        return redirect(url_for('student.home'))
    
    if request.method == 'POST':
        form_data = {
            'first_name': request.form.get('first_name', '').strip(),
            'father_name': request.form.get('father_name', '').strip(),
            'sex': request.form.get('sex', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'university': request.form.get('university', '').strip(),
            'stream': request.form.get('stream', '').strip(),
            'password': request.form.get('password', ''),
            'confirm_password': request.form.get('confirm_password', ''),
            'telegram_username': request.form.get('telegram_username', '').strip(),
            'email': request.form.get('email', '').strip(),
        }
        
        is_valid, errors = validate_registration(form_data)
        
        if not is_valid:
            for error in errors:
                flash(error, "danger")
            return redirect(url_for('student.register'))
        
        db = get_db()
        existing_phone = db.query_one("SELECT id FROM students WHERE phone = ?", (form_data['phone'],))
        
        if existing_phone:
            flash("This phone number is already registered. Please login.", "danger")
            return redirect(url_for('student.register'))
        
        full_name = f"{form_data['first_name']} {form_data['father_name']}"
        password_hash = hash_password(form_data['password'])
        
        photo_filename = 'default.png'
        if 'photo' in request.files:
            photo_file = request.files['photo']
            if photo_file and photo_file.filename:
                try:
                    photo_filename = save_student_photo(photo_file)
                except:
                    photo_filename = 'default.png'
        
        telegram_username = form_data['telegram_username']
        if telegram_username:
            telegram_username = telegram_username.replace('@', '').strip()
        
        try:
            db.execute('''
                INSERT INTO students (first_name, father_name, full_name, sex, phone, university, stream, password_hash, photo, email, telegram_username, subscription_status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'free', ?)
            ''', (form_data['first_name'], form_data['father_name'], full_name, form_data['sex'], form_data['phone'], form_data['university'], form_data['stream'], password_hash, photo_filename, form_data['email'] or None, telegram_username or None, datetime.now().isoformat()))
            
            logger.info(f"New student registered: {full_name}")
            flash("Registration successful! Please login to access your courses.", "success")
            return redirect(url_for('student.login'))
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            flash("Registration failed. Please try again.", "danger")
            return redirect(url_for('student.register'))
    
    return render_template('student_register.html', universities=UNIVERSITIES_LIST)

@student_bp.route('/student/logout', methods=['GET'])
@login_required
def logout():
    terminate_student_session()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('student.login'))

@student_bp.route('/student/home', methods=['GET'])
@login_required
def home():
    db = get_db()
    student = db.query_one("SELECT * FROM students WHERE id = ?", (session['student_id'],))
    
    if not student:
        terminate_student_session()
        return redirect(url_for('student.login'))
    
    courses = db.query('''
        SELECT c.*, COUNT(DISTINCT l.id) as total_lessons
        FROM courses c
        LEFT JOIN lessons l ON l.course_code = c.code AND l.is_active = 1
        WHERE c.is_active = 1 AND (c.stream = 'Common' OR c.stream = ?)
        GROUP BY c.code
        ORDER BY c.semester, c.code
    ''', (student['stream'],))
    
    announcements = db.query("SELECT * FROM announcements WHERE is_active = 1 ORDER BY created_at DESC LIMIT 5")
    
    latest_payment = db.query_one("SELECT * FROM payments WHERE student_id = ? ORDER BY submitted_at DESC LIMIT 1", (session['student_id'],))
    
    notifications = db.query("SELECT * FROM notifications WHERE student_id = ? AND is_read = 0 ORDER BY created_at DESC LIMIT 10", (session['student_id'],))
    
    return render_template('student_home.html', student=student, courses=courses, announcements=announcements, latest_payment=latest_payment, notifications=notifications)

@student_bp.route('/student/payment/submit', methods=['POST'])
@login_required
def submit_payment():
    db = get_db()
    student = db.query_one("SELECT * FROM students WHERE id = ?", (session['student_id'],))
    
    payment_method = request.form.get('payment_method')
    transaction_number = request.form.get('transaction_number', '').strip()
    amount = request.form.get('amount', 200)
    
    valid_methods = ['telebirr', 'cbe', 'abyssinia', 'abay', 'awash']
    if payment_method not in valid_methods:
        flash("Invalid payment method", "danger")
        return redirect(url_for('student.home'))
    
    if not transaction_number:
        flash("Transaction number is required", "danger")
        return redirect(url_for('student.home'))
    
    existing = db.query_one("SELECT id FROM payments WHERE transaction_number = ?", (transaction_number.upper(),))
    if existing:
        flash("This transaction number has already been submitted", "warning")
        return redirect(url_for('student.home'))
    
    from core.helpers import save_payment_screenshot
    screenshot_filename = None
    if 'payment_screenshot' in request.files:
        screenshot_file = request.files['payment_screenshot']
        if screenshot_file and screenshot_file.filename:
            screenshot_filename = save_payment_screenshot(screenshot_file, student['id'])
    
    db.execute('''
        INSERT INTO payments (student_id, payment_method, transaction_number, amount, payment_status, screenshot_path, submitted_at)
        VALUES (?, ?, ?, ?, 'pending', ?, ?)
    ''', (student['id'], payment_method, transaction_number.upper(), amount, screenshot_filename, datetime.now().isoformat()))
    
    db.execute("UPDATE students SET subscription_status = 'pending' WHERE id = ?", (student['id'],))
    
    db.execute('''
        INSERT INTO notifications (student_id, message, type, created_at)
        VALUES (?, 'Your payment has been submitted. Admin will verify and approve your access.', 'payment', ?)
    ''', (student['id'], datetime.now().isoformat()))
    
    # Send Telegram notification to admin
    try:
        from core.telegram_bot import notify_admin_payment
        notify_admin_payment(
            student['full_name'],
            student['phone'],
            transaction_number,
            payment_method
        )
    except:
        pass
    
    flash("Payment submitted successfully!", "success")
    return redirect(url_for('student.home'))

@student_bp.route('/student/settings', methods=['GET'])
@login_required
def settings():
    db = get_db()
    student = db.query_one("SELECT * FROM students WHERE id = ?", (session['student_id'],))
    return render_template('student_settings.html', student=student)
