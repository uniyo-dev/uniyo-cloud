"""
UNIYO LMS - Past Exam Library Routes
"""

from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
from datetime import datetime
import json

from core.db import get_db
from core.auth import login_required, premium_required
from core.helpers import logger
from core.paths import BASE_DIR

past_exam_bp = Blueprint('past_exam', __name__)

# ============================================
# PAST EXAM LIBRARY PAGE
# ============================================

@past_exam_bp.route('/student/past-exams', methods=['GET'])
@login_required
def library():
    """Past Exam Library - Browse all exams"""
    db = get_db()
    
    # Get all active exams
    exams = db.query('''
        SELECT * FROM past_exams
        WHERE is_active = 1
        ORDER BY views DESC
    ''')
    
    # Determine TOP 3 by views
    top_3_ids = [exam['id'] for exam in exams[:3]] if exams else []
    
    # Get student's ratings
    student_ratings = {}
    ratings = db.query('''
        SELECT past_exam_id, rating FROM past_exam_ratings
        WHERE student_id = ?
    ''', (session['student_id'],))
    for r in ratings:
        student_ratings[r['past_exam_id']] = r['rating']
    
    # Get student info
    student = db.query_one("SELECT * FROM students WHERE id = ?", (session["student_id"],))
    
    return render_template('student_past_exams.html', 
                          exams=exams, 
                          top_3_ids=top_3_ids,
                          student_ratings=student_ratings)

# ============================================
# TAKE PAST EXAM (Premium Only)
# ============================================

@past_exam_bp.route('/student/past-exam/<int:exam_id>/take', methods=['GET'])
@login_required
@premium_required
def take_exam(exam_id):
    """Take past exam"""
    db = get_db()
    
    exam = db.query_one("SELECT * FROM past_exams WHERE id = ? AND is_active = 1", (exam_id,))
    if not exam:
        flash("Exam not found", "danger")
        return redirect(url_for('past_exam.library'))
    
    # Increment views
    db.execute("UPDATE past_exams SET views = views + 1 WHERE id = ?", (exam_id,))
    
    # Load exam content
    from core.paths import BASE_DIR
    exam_file = BASE_DIR / "content" / "past_exams" / exam['university'] / exam['file_path']
    
    if not exam_file.exists():
        flash("Exam file not found", "danger")
        return redirect(url_for('past_exam.library'))
    
    exam_content = exam_file.read_text(encoding='utf-8')
    
    return render_template('student_past_exam_take.html', exam=exam, exam_content=exam_content)

# ============================================
# SUBMIT EXAM (Auto-graded)
# ============================================

@past_exam_bp.route('/api/past-exam/<int:exam_id>/submit', methods=['POST'])
@login_required
def submit_exam(exam_id):
    """Submit exam answers for auto-grading"""
    db = get_db()
    data = request.get_json()
    answers = data.get('answers', {})
    time_spent = data.get('time_spent_seconds', 0)
    
    exam = db.query_one("SELECT * FROM past_exams WHERE id = ?", (exam_id,))
    if not exam:
        return jsonify({"success": False, "error": "Exam not found"}), 404
    
    # Load exam file for grading
    exam_file = BASE_DIR / "content" / "past_exams" / exam['university'] / exam['file_path']
    exam_content = exam_file.read_text(encoding='utf-8')
    
    # Simple grading - extract correct answers from HTML data attributes
    import re
    score = 0
    total_points = 0
    answer_details = []
    
    # Extract all questions with data-correct attributes
    questions = re.findall(r'data-type="([^"]*)"[^>]*data-correct="([^"]*)"[^>]*data-points="([^"]*)"', exam_content)
    
    for i, (qtype, correct, points) in enumerate(questions, 1):
        total_points += float(points)
        student_answer = answers.get(str(i), '')
        
        if qtype in ['mcq', 'true_false']:
            if student_answer.strip() == correct.strip():
                score += float(points)
                answer_details.append({"question": i, "correct": True, "points": float(points)})
            else:
                answer_details.append({"question": i, "correct": False, "points": 0})
        elif qtype == 'blank_space' or qtype == 'short_answer':
            correct_terms = [t.strip().lower() for t in correct.split(',')]
            student_terms = [t.strip().lower() for t in student_answer.split(',')]
            
            matched = sum(1 for term in student_terms if term in correct_terms)
            points_per_term = float(points) / len(correct_terms)
            earned = matched * points_per_term
            score += earned
            answer_details.append({"question": i, "correct": matched == len(correct_terms), "points": earned})
    
    percentage = (score / total_points * 100) if total_points > 0 else 0
    
    # Save attempt
    db.execute('''
        INSERT INTO past_exam_attempts (past_exam_id, student_id, score, total_points, percentage, answers_json, time_spent_seconds, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (exam_id, session['student_id'], score, total_points, percentage, json.dumps(answers), time_spent, datetime.now().isoformat()))
    
    return jsonify({
        "success": True,
        "score": score,
        "total_points": total_points,
        "percentage": round(percentage, 2),
        "answer_details": answer_details
    })

# ============================================
# LIKE/DISLIKE EXAM
# ============================================

@past_exam_bp.route('/api/past-exam/<int:exam_id>/rate', methods=['POST'])
@login_required
def rate_exam(exam_id):
    """Like or dislike an exam"""
    db = get_db()
    data = request.get_json()
    rating = data.get('rating')  # 'like' or 'dislike'
    
    if rating not in ['like', 'dislike']:
        return jsonify({"success": False, "error": "Invalid rating"}), 400
    
    # Check if student is premium for dislike
    if rating == 'dislike':
        student = db.query_one("SELECT subscription_status FROM students WHERE id = ?", (session['student_id'],))
        if student['subscription_status'] != 'premium':
            return jsonify({"success": False, "error": "Premium required to dislike"}), 403
    
    # Check existing rating
    existing = db.query_one('''
        SELECT * FROM past_exam_ratings
        WHERE past_exam_id = ? AND student_id = ?
    ''', (exam_id, session['student_id']))
    
    if existing:
        # Update rating
        db.execute('''
            UPDATE past_exam_ratings SET rating = ?, created_at = ?
            WHERE past_exam_id = ? AND student_id = ?
        ''', (rating, datetime.now().isoformat(), exam_id, session['student_id']))
        
        # Update counts
        if existing['rating'] == 'like' and rating == 'dislike':
            db.execute("UPDATE past_exams SET likes = likes - 1, dislikes = dislikes + 1 WHERE id = ?", (exam_id,))
        elif existing['rating'] == 'dislike' and rating == 'like':
            db.execute("UPDATE past_exams SET likes = likes + 1, dislikes = dislikes - 1 WHERE id = ?", (exam_id,))
    else:
        # Insert new rating
        db.execute('''
            INSERT INTO past_exam_ratings (past_exam_id, student_id, rating, created_at)
            VALUES (?, ?, ?, ?)
        ''', (exam_id, session['student_id'], rating, datetime.now().isoformat()))
        
        if rating == 'like':
            db.execute("UPDATE past_exams SET likes = likes + 1 WHERE id = ?", (exam_id,))
        else:
            db.execute("UPDATE past_exams SET dislikes = dislikes + 1 WHERE id = ?", (exam_id,))
    
    exam = db.query_one("SELECT likes, dislikes FROM past_exams WHERE id = ?", (exam_id,))
    
    return jsonify({
        "success": True,
        "likes": exam['likes'],
        "dislikes": exam['dislikes']
    })
