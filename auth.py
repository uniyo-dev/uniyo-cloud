"""
UNIYO LMS - Authentication & Session Management
"""

from functools import wraps
from datetime import datetime, timedelta
from flask import session, redirect, url_for, flash, request, jsonify
import secrets

from core.db import get_db
from core.helpers import hash_password, verify_password, generate_session_token

SESSION_TIMEOUT_HOURS = 12

def create_student_session(student_id, request):
    db = get_db()
    existing_sessions = db.query('''
        SELECT * FROM active_sessions WHERE student_id = ? AND is_active = 1
    ''', (student_id,))
    
    current_time = datetime.now()
    valid_sessions = []
    
    for existing_session in existing_sessions:
        last_activity = datetime.fromisoformat(existing_session['last_activity'])
        if (current_time - last_activity) < timedelta(hours=SESSION_TIMEOUT_HOURS):
            valid_sessions.append(existing_session)
        else:
            db.execute("UPDATE active_sessions SET is_active = 0 WHERE id = ?", (existing_session['id'],))
    
    if valid_sessions:
        return False, "This account is already logged in on another device. Please logout from that device first."
    
    session_token = generate_session_token()
    db.execute('''
        INSERT INTO active_sessions (student_id, session_token, device_info, ip_address, created_at, last_activity)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (student_id, session_token, request.user_agent.string, request.remote_addr, current_time.isoformat(), current_time.isoformat()))
    
    session['student_id'] = student_id
    session['session_token'] = session_token
    session['login_time'] = current_time.isoformat()
    session.permanent = True
    
    return True, "Session created"

def validate_student_session():
    if 'student_id' not in session or 'session_token' not in session:
        return False, "No session found"
    
    db = get_db()
    active_session = db.query_one('''
        SELECT * FROM active_sessions WHERE student_id = ? AND session_token = ? AND is_active = 1
    ''', (session['student_id'], session['session_token']))
    
    if not active_session:
        session.clear()
        return False, "Session terminated"
    
    last_activity = datetime.fromisoformat(active_session['last_activity'])
    current_time = datetime.now()
    
    if (current_time - last_activity) > timedelta(hours=SESSION_TIMEOUT_HOURS):
        db.execute("UPDATE active_sessions SET is_active = 0 WHERE id = ?", (active_session['id'],))
        session.clear()
        return False, "Session expired"
    
    db.execute("UPDATE active_sessions SET last_activity = ? WHERE id = ?", (current_time.isoformat(), active_session['id']))
    return True, "Session valid"

def terminate_student_session():
    if 'student_id' in session and 'session_token' in session:
        db = get_db()
        db.execute("UPDATE active_sessions SET is_active = 0 WHERE student_id = ? AND session_token = ?", (session.get('student_id'), session.get('session_token')))
    session.clear()

def create_admin_session(admin_id, request):
    session['admin_id'] = admin_id
    session['admin_login_time'] = datetime.now().isoformat()
    session.permanent = True
    return True, "Admin session created"

def terminate_admin_session():
    session.pop('admin_id', None)
    session.pop('admin_login_time', None)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            flash("Please login to access this page.", "warning")
            return redirect(url_for('student.login'))
        valid, message = validate_student_session()
        if not valid:
            flash(message, "danger")
            return redirect(url_for('student.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash("Please login as administrator.", "warning")
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def premium_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            flash("Please login to access this content.", "warning")
            return redirect(url_for('student.login'))
        valid, message = validate_student_session()
        if not valid:
            flash(message, "danger")
            return redirect(url_for('student.login'))
        db = get_db()
        student = db.query_one("SELECT subscription_status, subscription_expires FROM students WHERE id = ?", (session['student_id'],))
        if not student:
            session.clear()
            return redirect(url_for('student.login'))
        if student['subscription_status'] != 'premium':
            flash("This content requires premium access. Please upgrade your account.", "warning")
            return redirect(url_for('student.home'))
        if student['subscription_expires']:
            expires = datetime.fromisoformat(student['subscription_expires'])
            if expires < datetime.now():
                db.execute("UPDATE students SET subscription_status = 'expired' WHERE id = ?", (session['student_id'],))
                flash("Your premium subscription has expired. Please renew.", "warning")
                return redirect(url_for('student.home'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'admin_id' not in session:
                flash("Please login as administrator.", "warning")
                return redirect(url_for('admin.login'))
            db = get_db()
            admin = db.query_one("SELECT role FROM admins WHERE id = ?", (session['admin_id'],))
            if not admin:
                session.clear()
                return redirect(url_for('admin.login'))
            if admin['role'] not in required_roles:
                flash("You don't have permission to access this page.", "danger")
                return redirect(url_for('admin.home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def authenticate_student(identifier, password):
    db = get_db()
    student = db.query_one('''
        SELECT * FROM students WHERE phone = ? AND is_active = 1
    ''', (identifier,))
    if not student:
        return None, "Invalid credentials"
    if student['subscription_status'] == 'blocked':
        return None, "Your account has been blocked. Please contact admin."
    if not verify_password(student['password_hash'], password):
        return None, "Invalid credentials"
    return student, "Authentication successful"

def authenticate_admin(username, password):
    db = get_db()
    admin = db.query_one("SELECT * FROM admins WHERE username = ?", (username,))
    if not admin:
        return None, "Invalid credentials"
    if not verify_password(admin['password_hash'], password):
        return None, "Invalid credentials"
    return admin, "Authentication successful"

def get_current_student():
    if 'student_id' not in session:
        return None
    db = get_db()
    return db.query_one("SELECT * FROM students WHERE id = ?", (session['student_id'],))

def get_current_admin():
    if 'admin_id' not in session:
        return None
    db = get_db()
    return db.query_one("SELECT * FROM admins WHERE id = ?", (session['admin_id'],))

def has_permission(permission):
    admin = get_current_admin()
    if not admin:
        return False
    from core.constants import ADMIN_ROLES
    role_permissions = ADMIN_ROLES.get(admin['role'], {}).get('permissions', {})
    return role_permissions.get(permission, False)

def generate_reset_token():
    return secrets.token_urlsafe(32)

def save_reset_token(student_id, token):
    db = get_db()
    expiry = (datetime.now() + timedelta(hours=24)).isoformat()
    db.execute("UPDATE students SET reset_token = ?, reset_token_expiry = ? WHERE id = ?", (token, expiry, student_id))

def verify_reset_token(token):
    db = get_db()
    student = db.query_one("SELECT * FROM students WHERE reset_token = ?", (token,))
    if not student:
        return None, "Invalid reset token"
    if student['reset_token_expiry']:
        expiry = datetime.fromisoformat(student['reset_token_expiry'])
        if expiry < datetime.now():
            return None, "Reset token has expired"
    return student, "Token valid"

def clear_reset_token(student_id):
    db = get_db()
    db.execute("UPDATE students SET reset_token = NULL, reset_token_expiry = NULL WHERE id = ?", (student_id,))
