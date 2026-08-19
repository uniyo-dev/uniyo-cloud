"""
UNIYO LMS - VIP Competition Routes
"""

from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
from datetime import datetime
import json

from core.db import get_db
from core.auth import login_required
from core.helpers import logger
from core.paths import VIP_QUESTIONS_DIR

vip_bp = Blueprint('vip', __name__)

@vip_bp.route('/student/vip', methods=['GET'])
@login_required
def vip_dashboard():
    db = get_db()
    current_time = datetime.now().isoformat()
    
    active_vip = db.query("SELECT * FROM vip_questions WHERE is_active = 1 AND start_time <= ? AND end_time >= ?", (current_time, current_time))
    upcoming_vip = db.query("SELECT * FROM vip_questions WHERE is_active = 1 AND start_time > ? ORDER BY start_time LIMIT 5", (current_time,))
    past_vip = db.query('''
        SELECT vq.*, va.score, va.total, va.time_spent_seconds FROM vip_questions vq
        LEFT JOIN vip_attempts va ON vq.id = va.vip_question_id AND va.student_id = ?
        WHERE vq.is_active = 1 AND vq.end_time < ? ORDER BY vq.start_time DESC LIMIT 10
    ''', (session['student_id'], current_time))
    
    current_month = datetime.now().strftime('%Y-%m')
    leaderboard = get_monthly_leaderboard(current_month)
    
    return render_template('student_vip.html', active_vip=active_vip, upcoming_vip=upcoming_vip, past_vip=past_vip, leaderboard=leaderboard, current_month=current_month)

@vip_bp.route('/student/vip/<int:vip_id>/take', methods=['GET'])
@login_required
def take_vip(vip_id):
    db = get_db()
    current_time = datetime.now().isoformat()
    
    vip = db.query_one("SELECT * FROM vip_questions WHERE id = ? AND is_active = 1", (vip_id,))
    
    if not vip:
        flash("VIP question not found", "danger")
        return redirect(url_for('vip.vip_dashboard'))
    
    if current_time < vip['start_time']:
        flash("This VIP question has not started yet", "warning")
        return redirect(url_for('vip.vip_dashboard'))
    
    if current_time > vip['end_time']:
        flash("This VIP question has ended", "warning")
        return redirect(url_for('vip.vip_dashboard'))
    
    existing_attempt = db.query_one("SELECT * FROM vip_attempts WHERE vip_question_id = ? AND student_id = ?", (vip_id, session['student_id']))
    if existing_attempt:
        flash("You have already attempted this VIP question", "warning")
        return redirect(url_for('vip.vip_dashboard'))
    
    questions_data = load_vip_questions(vip['question_file'])
    if questions_data is None:
        flash("VIP questions not found", "danger")
        return redirect(url_for('vip.vip_dashboard'))
    
    return render_template('student_vip_take.html', vip=vip, questions=questions_data.get('questions', []))

@vip_bp.route('/api/vip/<int:vip_id>/submit', methods=['POST'])
@login_required
def submit_vip(vip_id):
    db = get_db()
    current_time = datetime.now().isoformat()
    
    vip = db.query_one("SELECT * FROM vip_questions WHERE id = ?", (vip_id,))
    if not vip:
        return jsonify({"success": False, "error": "VIP question not found"}), 404
    
    if current_time > vip['end_time']:
        return jsonify({"success": False, "error": "Time has expired"}), 400
    
    existing = db.query_one("SELECT * FROM vip_attempts WHERE vip_question_id = ? AND student_id = ?", (vip_id, session['student_id']))
    if existing:
        return jsonify({"success": False, "error": "Already attempted"}), 400
    
    data = request.get_json()
    answers = data.get('answers', {})
    time_spent = data.get('time_spent_seconds', 0)
    
    questions_data = load_vip_questions(vip['question_file'])
    questions = questions_data.get('questions', [])
    
    score = 0
    total = len(questions)
    
    for question in questions:
        question_id = str(question.get('id'))
        selected = answers.get(question_id, '')
        correct = question.get('correct_answer', '')
        if selected == correct:
            score += 1
    
    db.execute('''
        INSERT INTO vip_attempts (vip_question_id, student_id, score, total, time_spent_seconds, answers_json, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (vip_id, session['student_id'], score, total, time_spent, json.dumps(answers), current_time))
    
    return jsonify({"success": True, "score": score, "total": total, "percentage": round((score / total * 100), 2) if total > 0 else 0, "time_spent": time_spent})

def get_monthly_leaderboard(month_year):
    db = get_db()
    results = db.query('''
        SELECT s.id as student_id, s.full_name, s.university, SUM(va.score) as total_score, SUM(va.time_spent_seconds) as total_time, COUNT(va.id) as attempts_count
        FROM vip_attempts va JOIN students s ON va.student_id = s.id JOIN vip_questions vq ON va.vip_question_id = vq.id
        WHERE strftime('%Y-%m', vq.start_time) = ? GROUP BY s.id ORDER BY total_score DESC, total_time ASC
    ''', (month_year,))
    
    leaderboard = []
    for index, result in enumerate(results):
        leaderboard.append({'rank': index + 1, 'student_id': result['student_id'], 'full_name': result['full_name'], 'university': result['university'], 'total_score': result['total_score'], 'total_time': result['total_time'], 'attempts_count': result['attempts_count']})
    return leaderboard

def load_vip_questions(question_file):
    try:
        file_path = VIP_QUESTIONS_DIR / question_file
        if not file_path.exists():
            return None
        return json.loads(file_path.read_text(encoding='utf-8'))
    except Exception as e:
        logger.error(f"Error loading VIP questions: {e}")
        return None
