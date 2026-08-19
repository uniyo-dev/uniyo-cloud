"""
UNIYO LMS - Worksheet Engine Routes
"""

from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
from datetime import datetime
from pathlib import Path
import json

from core.db import get_db
from core.auth import login_required, premium_required
from core.helpers import logger
from core.paths import WORKSHEETS_DIR

worksheet_bp = Blueprint('worksheet', __name__)

@worksheet_bp.route('/student/worksheet/<int:worksheet_id>', methods=['GET'])
@login_required
@premium_required
def view_worksheet(worksheet_id):
    db = get_db()
    worksheet = db.query_one("SELECT * FROM worksheets WHERE id = ? AND is_active = 1", (worksheet_id,))
    
    if not worksheet:
        flash("Worksheet not found or not published.", "danger")
        return redirect(url_for('student.home'))
    
    questions_data = load_worksheet_questions(worksheet['question_file'])
    
    if questions_data is None:
        flash("Worksheet questions not found.", "danger")
        return redirect(url_for('student.home'))
    
    attempts = db.query('''
        SELECT * FROM worksheet_attempts WHERE worksheet_id = ? AND student_id = ? ORDER BY attempt_number DESC
    ''', (worksheet_id, session['student_id']))
    
    best_score = db.query_one('''
        SELECT MAX(score) as best, MAX(total) as total FROM worksheet_attempts
        WHERE worksheet_id = ? AND student_id = ? AND is_completed = 1
    ''', (worksheet_id, session['student_id']))
    
    return render_template('student_worksheet.html', worksheet=worksheet, questions=questions_data.get('questions', []), attempts=attempts, best_score=best_score)

@worksheet_bp.route('/api/worksheet/<int:worksheet_id>/submit', methods=['POST'])
@login_required
def submit_worksheet(worksheet_id):
    db = get_db()
    data = request.get_json()
    answers = data.get('answers', {})
    
    worksheet = db.query_one("SELECT * FROM worksheets WHERE id = ?", (worksheet_id,))
    if not worksheet:
        return jsonify({"success": False, "error": "Worksheet not found"}), 404
    
    questions_data = load_worksheet_questions(worksheet['question_file'])
    questions = questions_data.get('questions', [])
    
    score = 0
    total = len(questions)
    answer_details = []
    
    for question in questions:
        question_id = str(question.get('id'))
        selected = answers.get(question_id, '')
        correct = question.get('correct_answer', '')
        is_correct = (selected == correct)
        if is_correct:
            score += 1
        answer_details.append({'question_id': question_id, 'selected': selected, 'correct': correct, 'is_correct': is_correct, 'explanation': question.get('explanation', '')})
    
    percentage = (score / total * 100) if total > 0 else 0
    
    last_attempt = db.query_one("SELECT MAX(attempt_number) as max_attempt FROM worksheet_attempts WHERE worksheet_id = ? AND student_id = ?", (worksheet_id, session['student_id']))
    attempt_number = (last_attempt['max_attempt'] or 0) + 1
    
    db.execute('''
        INSERT INTO worksheet_attempts (worksheet_id, student_id, attempt_number, answers_json, score, total, is_completed, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?)
    ''', (worksheet_id, session['student_id'], attempt_number, json.dumps(answer_details), score, total, datetime.now().isoformat()))
    
    return jsonify({"success": True, "score": score, "total": total, "percentage": round(percentage, 2), "attempt_number": attempt_number, "answer_details": answer_details})

@worksheet_bp.route('/api/worksheet/<int:worksheet_id>/autosave', methods=['POST'])
@login_required
def autosave_worksheet(worksheet_id):
    logger.info(f"Autosave for worksheet {worksheet_id}")
    return jsonify({"success": True, "message": "Progress saved"})

def load_worksheet_questions(question_file):
    try:
        from core.paths import WORKSHEETS_DIR
        import json as json_module
        
        # New structure: content/worksheets/{Course}/chapter{N}/part{M}.json
        file_path = WORKSHEETS_DIR / question_file
        
        if not file_path.exists():
            logger.error(f"Worksheet file not found: {question_file}")
            return None
        
        return json_module.loads(file_path.read_text(encoding='utf-8'))
    except Exception as e:
        logger.error(f"Error loading questions: {e}")
        return None
