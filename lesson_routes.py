"""
UNIYO LMS - Lesson Reader Routes
"""

from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from datetime import datetime
from pathlib import Path

from core.db import get_db
from core.auth import login_required
from core.helpers import logger
from core.paths import LESSONS_DIR
from core.constants import UNIVERSITY_SHORT_NAMES

lesson_bp = Blueprint('lesson', __name__)

@lesson_bp.route('/student/lessons/<course_code>/chapter/<int:chap>/part/<int:part>', methods=['GET'])
@login_required
def read_lesson(course_code, chap, part):
    db = get_db()
    student = db.query_one("SELECT * FROM students WHERE id = ?", (session['student_id'],))
    
    if not student:
        from core.auth import terminate_student_session
        terminate_student_session()
        return redirect(url_for('student.login'))
    
    university_short = UNIVERSITY_SHORT_NAMES.get(student['university'], 'all')
    
    lesson = db.query_one('''
        SELECT * FROM lessons WHERE course_code = ? AND chapter_number = ? AND part_number = ?
        AND (university_specific = ? OR university_specific IS NULL OR university_specific = 'all')
        AND is_active = 1
        ORDER BY CASE WHEN university_specific = ? THEN 0 ELSE 1 END
        LIMIT 1
    ''', (course_code, chap, part, university_short, university_short))
    
    if not lesson:
        flash("Lesson not found or not published yet.", "danger")
        return redirect(url_for('student.home'))
    
    if lesson['is_premium'] == 1 and student['subscription_status'] != 'premium':
        flash("This is a premium lesson. Please upgrade your account to access.", "warning")
        return redirect(url_for('student.home'))
    
    # Try new structure first: content/courses/{Course}/chapter{N}/part{M}.html
    lesson_file = LESSONS_DIR / lesson['course_code'] / f"chapter{lesson['chapter_number']}" / f"part{lesson['part_number']}.html"
    if not lesson_file.exists():
        # Fallback to old structure
        lesson_file = LESSONS_DIR / lesson['file_path']
    
    if not lesson_file.exists():
        flash("Lesson content file not found.", "danger")
        return redirect(url_for('student.home'))
    
    lesson_content = lesson_file.read_text(encoding='utf-8')
    
    progress = db.query_one('''
        SELECT * FROM lesson_progress WHERE student_id = ? AND lesson_id = ?
    ''', (session['student_id'], lesson['id']))
    
    all_parts = db.query('''
        SELECT * FROM lessons 
        WHERE course_code = ? AND chapter_number = ? AND is_active = 1
        AND (university_specific IS NULL OR university_specific = ? OR university_specific = 'all')
        GROUP BY part_number
        ORDER BY part_number
    ''', (course_code, chap, university_short))
    
    next_lesson = db.query_one('''
        SELECT * FROM lessons WHERE course_code = ? AND is_active = 1
        AND (chapter_number > ? OR (chapter_number = ? AND part_number > ?))
        ORDER BY chapter_number, part_number LIMIT 1
    ''', (course_code, chap, chap, part))
    
    prev_lesson = db.query_one('''
        SELECT * FROM lessons WHERE course_code = ? AND is_active = 1
        AND (chapter_number < ? OR (chapter_number = ? AND part_number < ?))
        ORDER BY chapter_number DESC, part_number DESC LIMIT 1
    ''', (course_code, chap, chap, part))
    
    watermark = {
        'student_name': student['full_name'],
        'student_phone': student['phone'],
    }
    
    # Find PART-SPECIFIC worksheet first
    part_worksheet = db.query_one('''
        SELECT * FROM worksheets 
        WHERE course_code = ? AND chapter_number = ?
        AND question_file LIKE ?
        AND is_active = 1
        LIMIT 1
    ''', (course_code, chap, f'{course_code}/chapter{chap}/part{part}%'))
    
    # If no part-specific, look for university-specific part worksheet
    if not part_worksheet:
        part_worksheet = db.query_one('''
            SELECT * FROM worksheets 
            WHERE course_code = ? AND chapter_number = ?
            AND question_file LIKE ?
            AND is_active = 1
            LIMIT 1
        ''', (course_code, chap, f'{course_code}/chapter{chap}/part{part}%'))
    
    # Find FULL chapter worksheet (only for last part)
    full_worksheet = None
    is_last_part = True
    for p in all_parts:
        if p['part_number'] > lesson['part_number']:
            is_last_part = False
            break
    
    if is_last_part:
        full_worksheet = db.query_one('''
            SELECT * FROM worksheets 
            WHERE course_code = ? AND chapter_number = ?
            AND question_file LIKE ?
            AND is_active = 1
            LIMIT 1
        ''', (course_code, chap, f'{course_code}/chapter{chap}/full%'))
        
        if not full_worksheet:
            full_worksheet = db.query_one('''
                SELECT * FROM worksheets 
                WHERE course_code = ? AND chapter_number = ?
                AND question_file LIKE ?
                AND is_active = 1
                LIMIT 1
            ''', (course_code, chap, f'{course_code}/chapter{chap}/full%'))
    
    # Get all UNIQUE chapters (GROUP BY chapter_number - each chapter only ONCE)
    all_chapters = db.query('''
        SELECT chapter_number, MIN(chapter_title) as chapter_title
        FROM lessons
        WHERE course_code = ? AND is_active = 1
        AND (university_specific IS NULL OR university_specific = ? OR university_specific = 'all')
        GROUP BY chapter_number
        ORDER BY chapter_number
    ''', (course_code, university_short))
    
    # Get total parts per chapter for display
    chapter_info = []
    for chapter in all_chapters:
        parts_count = db.query_value('''
            SELECT COUNT(DISTINCT part_number) FROM lessons
            WHERE course_code = ? AND chapter_number = ? AND is_active = 1
            AND (university_specific IS NULL OR university_specific = ? OR university_specific = 'all')
        ''', (course_code, chapter['chapter_number'], university_short))
        
        chapter_info.append({
            'chapter_number': chapter['chapter_number'],
            'chapter_title': chapter['chapter_title'],
            'parts_count': parts_count or 0
        })
    
    return render_template('student_lessons.html', lesson=lesson, lesson_content=lesson_content, progress=progress, all_parts=all_parts, next_lesson=next_lesson, prev_lesson=prev_lesson, student=student, watermark=watermark, part_worksheet=part_worksheet, full_worksheet=full_worksheet, is_last_part=is_last_part, chapter_info=chapter_info, current_chapter=chap)
