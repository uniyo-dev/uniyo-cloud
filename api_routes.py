"""
UNIYO LMS - API Routes Blueprint
"""

from flask import Blueprint, jsonify, request, session
from datetime import datetime
import json

from core.db import get_db
from core.auth import login_required

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health', methods=['GET'])
def health():
    db = get_db()
    try:
        db.query_one("SELECT 1")
        db_status = "connected"
    except:
        db_status = "error"
    return jsonify({"success": True, "status": "healthy", "database": db_status, "timestamp": datetime.now().isoformat()})

@api_bp.route('/news', methods=['GET'])
def get_news():
    db = get_db()
    announcements = db.query('''
        SELECT id, title, message, priority, created_at FROM announcements
        WHERE is_active = 1 ORDER BY created_at DESC LIMIT 10
    ''')
    return jsonify({"success": True, "announcements": [dict(a) for a in announcements]})

@api_bp.route('/lessons/<int:lesson_id>/progress', methods=['POST'])
@login_required
def save_progress(lesson_id):
    db = get_db()
    data = request.get_json()
    progress_percent = data.get('progress_percent', 0)
    last_position = data.get('last_position', 0)
    is_completed = data.get('is_completed', 0)
    
    db.execute('''
        INSERT OR REPLACE INTO lesson_progress (student_id, lesson_id, progress_percent, last_position, is_completed, completed_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session['student_id'], lesson_id, progress_percent, last_position, is_completed, datetime.now().isoformat() if is_completed else None))
    
    return jsonify({"success": True, "message": "Progress saved"})

@api_bp.route('/lessons/<int:lesson_id>/complete', methods=['POST'])
@login_required
def complete_lesson(lesson_id):
    db = get_db()
    db.execute('''
        INSERT OR REPLACE INTO lesson_progress (student_id, lesson_id, progress_percent, last_position, is_completed, completed_at)
        VALUES (?, ?, 100, 0, 1, ?)
    ''', (session['student_id'], lesson_id, datetime.now().isoformat()))
    return jsonify({"success": True, "message": "Lesson completed"})

@api_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    db = get_db()
    db.execute("UPDATE notifications SET is_read = 1 WHERE id = ? AND student_id = ?", (notification_id, session['student_id']))
    return jsonify({"success": True})

@api_bp.route('/vip/status', methods=['GET'])
@login_required
def vip_status():
    db = get_db()
    current_time = datetime.now().isoformat()
    
    active_vip = db.query('''
        SELECT * FROM vip_questions WHERE is_active = 1 AND start_time <= ? AND end_time >= ?
    ''', (current_time, current_time))
    
    upcoming_vip = db.query('''
        SELECT * FROM vip_questions WHERE is_active = 1 AND start_time > ? ORDER BY start_time LIMIT 3
    ''', (current_time,))
    
    return jsonify({"success": True, "active_vip": [dict(v) for v in active_vip], "upcoming_vip": [dict(v) for v in upcoming_vip]})

@api_bp.route('/log-screen-capture', methods=['POST'])
@login_required
def log_screen_capture():
    db = get_db()
    data = request.get_json()
    db.execute('''
        INSERT INTO security_logs (student_id, event_type, details, ip_address, created_at)
        VALUES (?, 'screen_capture_attempt', ?, ?, ?)
    ''', (session['student_id'], json.dumps(data), request.remote_addr, datetime.now().isoformat()))
    return jsonify({"success": True})

@api_bp.route('/worksheets/<course_code>/chapter/<int:chapter>/questions', methods=['GET'])
@login_required
def get_self_check_questions(course_code, chapter):
    db = get_db()
    
    # First try to find part-specific worksheet (all_)
    worksheet = db.query_one('''
        SELECT * FROM worksheets 
        WHERE course_code = ? AND chapter_number = ? AND is_active = 1
        AND question_file LIKE ?
        LIMIT 1
    ''', (course_code, chapter, f'all_{course_code}_chapter{chapter}%'))
    
    # If not found, try full chapter
    if not worksheet:
        worksheet = db.query_one('''
            SELECT * FROM worksheets 
            WHERE course_code = ? AND chapter_number = ? AND is_active = 1
            LIMIT 1
        ''', (course_code, chapter))
    
    if not worksheet:
        return jsonify({"success": True, "questions": []})
    
    from core.paths import LESSONS_DIR
    question_file = WORKSHEETS_DIR / worksheet['question_file']
    
    if not question_file.exists():
        return jsonify({"success": True, "questions": []})
    
    try:
        questions_data = json.loads(question_file.read_text(encoding='utf-8'))
        questions = questions_data.get('questions', [])
        # Return first 3 questions for self-check
        return jsonify({"success": True, "questions": questions[:3], "worksheet_id": worksheet['id']})
    except Exception as e:
        return jsonify({"success": True, "questions": []})
