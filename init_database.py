#!/usr/bin/env python3
"""
UNIYO LMS - Database Initialization & Seeder
"""

import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.db import Database
from core.paths import ensure_directories, DB_PATH, LESSONS_DIR
from core.constants import COURSES, PAYMENT_CONFIG
from core.helpers import hash_password, logger

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    father_name TEXT NOT NULL,
    full_name TEXT NOT NULL,
    sex TEXT NOT NULL CHECK(sex IN ('Male', 'Female')),
    phone TEXT UNIQUE NOT NULL,
    university TEXT NOT NULL,
    stream TEXT NOT NULL CHECK(stream IN ('Natural', 'Social')),
    password_hash TEXT NOT NULL,
    photo TEXT DEFAULT 'default.png',
    email TEXT,
    telegram_username TEXT,
    is_active INTEGER DEFAULT 1,
    subscription_status TEXT DEFAULT 'free',
    subscription_expires TEXT,
    reset_token TEXT,
    reset_token_expiry TEXT,
    last_login TEXT,
    login_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS active_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    device_info TEXT,
    ip_address TEXT,
    created_at TEXT NOT NULL,
    last_activity TEXT,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    credit_hours INTEGER DEFAULT 3,
    semester INTEGER DEFAULT 1,
    stream TEXT DEFAULT 'Common',
    description TEXT,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    part_number INTEGER NOT NULL,
    chapter_title TEXT NOT NULL,
    part_title TEXT NOT NULL,
    file_path TEXT UNIQUE NOT NULL,
    university_specific TEXT,
    estimated_minutes INTEGER DEFAULT 5,
    is_premium INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 1,
    content_version INTEGER DEFAULT 1,
    file_hash TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(course_code) REFERENCES courses(code) ON DELETE CASCADE,
    UNIQUE(course_code, chapter_number, part_number, university_specific)
);

CREATE TABLE IF NOT EXISTS lesson_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    lesson_id INTEGER NOT NULL,
    progress_percent INTEGER DEFAULT 0,
    last_position INTEGER DEFAULT 0,
    is_completed INTEGER DEFAULT 0,
    completed_at TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
    UNIQUE(student_id, lesson_id)
);

CREATE TABLE IF NOT EXISTS worksheets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    question_file TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    content_version INTEGER DEFAULT 1,
    file_hash TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(course_code) REFERENCES courses(code) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS worksheet_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worksheet_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    attempt_number INTEGER DEFAULT 1,
    answers_json TEXT,
    score INTEGER,
    total INTEGER,
    is_completed INTEGER DEFAULT 0,
    completed_at TEXT,
    FOREIGN KEY(worksheet_id) REFERENCES worksheets(id) ON DELETE CASCADE,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vip_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    week_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    question_file TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    duration_hours INTEGER NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    FOREIGN KEY(course_code) REFERENCES courses(code) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vip_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vip_question_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    score INTEGER,
    total INTEGER,
    time_spent_seconds INTEGER,
    answers_json TEXT,
    completed_at TEXT,
    FOREIGN KEY(vip_question_id) REFERENCES vip_questions(id) ON DELETE CASCADE,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE(vip_question_id, student_id)
);

CREATE TABLE IF NOT EXISTS past_exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    university TEXT NOT NULL,
    course_code TEXT NOT NULL,
    course_title TEXT NOT NULL,
    year INTEGER NOT NULL,
    exam_type TEXT NOT NULL,
    file_path TEXT UNIQUE NOT NULL,
    is_active INTEGER DEFAULT 1,
    content_version INTEGER DEFAULT 1,
    file_hash TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(course_code) REFERENCES courses(code) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    payment_method TEXT NOT NULL,
    transaction_number TEXT UNIQUE,
    amount REAL NOT NULL DEFAULT 200.00,
    payment_status TEXT DEFAULT 'pending',
    screenshot_path TEXT,
    submitted_at TEXT NOT NULL,
    reviewed_at TEXT,
    reviewed_by INTEGER,
    rejection_reason TEXT,
    resubmit_count INTEGER DEFAULT 0,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(reviewed_by) REFERENCES admins(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('super_admin', 'content_manager', 'payment_verifier')),
    reset_token TEXT,
    reset_token_expiry TEXT,
    must_change_password INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS announcements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    priority TEXT DEFAULT 'normal',
    image TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    certificate_type TEXT NOT NULL,
    rank INTEGER,
    month_year TEXT,
    certificate_number TEXT UNIQUE NOT NULL,
    verification_token TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    issue_date TEXT NOT NULL,
    issued_by INTEGER,
    full_name TEXT,
    university TEXT,
    stream TEXT,
    phone TEXT,
    amount REAL,
    payment_method TEXT,
    transaction_number TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY(issued_by) REFERENCES admins(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS content_archive (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type TEXT NOT NULL,
    original_id INTEGER,
    course_code TEXT,
    chapter_number INTEGER,
    part_number INTEGER,
    title TEXT,
    file_path TEXT,
    file_hash TEXT,
    archived_at TEXT NOT NULL,
    reason TEXT DEFAULT 'replaced'
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    type TEXT DEFAULT 'general',
    is_read INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS security_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    event_type TEXT NOT NULL,
    details TEXT,
    ip_address TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    target_table TEXT NOT NULL,
    target_id INTEGER,
    details TEXT,
    ip_address TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(admin_id) REFERENCES admins(id) ON DELETE CASCADE
);
"""

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_students_phone ON students(phone)",
    "CREATE INDEX IF NOT EXISTS idx_students_university ON students(university)",
    "CREATE INDEX IF NOT EXISTS idx_students_stream ON students(stream)",
    "CREATE INDEX IF NOT EXISTS idx_students_subscription ON students(subscription_status)",
    "CREATE INDEX IF NOT EXISTS idx_sessions_student ON active_sessions(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_sessions_token ON active_sessions(session_token)",
    "CREATE INDEX IF NOT EXISTS idx_lessons_course ON lessons(course_code)",
    "CREATE INDEX IF NOT EXISTS idx_lessons_active ON lessons(is_active)",
    "CREATE INDEX IF NOT EXISTS idx_progress_student ON lesson_progress(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_worksheets_course ON worksheets(course_code)",
    "CREATE INDEX IF NOT EXISTS idx_vip_active ON vip_questions(is_active)",
    "CREATE INDEX IF NOT EXISTS idx_vip_attempts_student ON vip_attempts(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_payments_student ON payments(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(payment_status)",
    "CREATE INDEX IF NOT EXISTS idx_certificates_student ON certificates(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_notifications_student ON notifications(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_audit_admin ON audit_logs(admin_id)",
]

def seed_courses(db):
    logger.info("Seeding courses...")
    for course in COURSES:
        existing = db.query_one("SELECT id FROM courses WHERE code = ?", (course['code'],))
        if not existing:
            db.execute('''
                INSERT INTO courses (code, title, credit_hours, semester, stream, description, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', (course['code'], course['title'], course.get('credit_hours', 3), course.get('semester', 1), course.get('stream', 'Common'), course.get('description', '')))
            logger.info(f"  Added: {course['code']} - {course['title']}")

def seed_default_admin(db):
    logger.info("Seeding default admin...")
    existing = db.query_one("SELECT id FROM admins WHERE username = 'admin'")
    if not existing:
        password_hash = hash_password("Admin@123")
        db.execute('''
            INSERT INTO admins (username, password_hash, full_name, role, must_change_password)
            VALUES ('admin', ?, 'System Administrator', 'super_admin', 1)
        ''', (password_hash,))
        logger.info("  Created admin (username: admin, password: Admin@123)")

import hashlib

def get_file_hash(file_path):
    """Calculate MD5 hash of file content"""
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None

def archive_content(db, content_type, entry, reason='replaced'):
    """Archive old content before replacing"""
    from datetime import datetime
    db.execute('''
        INSERT INTO content_archive (content_type, original_id, course_code, chapter_number, part_number, title, file_path, file_hash, archived_at, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (content_type, entry.get('id'), entry.get('course_code'), entry.get('chapter_number'), entry.get('part_number'), entry.get('title'), entry.get('file_path'), entry.get('file_hash'), datetime.now().isoformat(), reason))

def scan_content_folder(db):
    """Scan lessons folder - HTML files to lessons, JSON files to worksheets"""
    from datetime import datetime, timedelta
    from core.paths import WORKSHEETS_DIR, VIP_QUESTIONS_DIR
    
    logger.info("Scanning lessons folder...")
    
    if not LESSONS_DIR.exists():
        return 0
    
    valid_courses = db.query("SELECT code FROM courses")
    valid_course_codes = [c["code"] for c in valid_courses]
    
    # Scan chapter sub-folders in content/courses/
    files = []
    if LESSONS_DIR.exists():
        for course_dir in LESSONS_DIR.iterdir():
            if course_dir.is_dir():
                for chapter_dir in course_dir.iterdir():
                    if chapter_dir.is_dir():
                        files.extend(list(chapter_dir.glob("*.html")))
                        files.extend(list(chapter_dir.glob("*.json")))
                # Also course root
                files.extend(list(course_dir.glob("*.html")))
                files.extend(list(course_dir.glob("*.json")))
        # Root level
        files.extend(list(LESSONS_DIR.glob("*.html")))
        files.extend(list(LESSONS_DIR.glob("*.json")))
    
    # Also scan VIP questions folder
    vip_files = []
    if VIP_QUESTIONS_DIR.exists():
        for course_dir in VIP_QUESTIONS_DIR.iterdir():
            if course_dir.is_dir():
                vip_files.extend(list(course_dir.glob("*.json")))
        # Also check root
        vip_files.extend(list(VIP_QUESTIONS_DIR.glob("*.json")))
    
    # Track VIP additions separately
    vip_added = 0
    
    # Scan VIP files
    for vip_file in vip_files:
        filename = vip_file.name
        
        # Check if already in database
        existing_vip = db.query_one("SELECT id FROM vip_questions WHERE question_file = ?", (filename,))
        if existing_vip:
            continue
        
        # Parse: VIP_{CourseCode}_Week{WeekNumber}.json
        try:
            name_without_ext = filename.rsplit(".", 1)[0]
            parts = name_without_ext.split("_")
            
            if len(parts) >= 4 and parts[0] == "VIP":
                course_code = parts[1]
                # New format: VIP_Course_Chapter{N}_Week{N}.json
                chapter_str = parts[2].replace("Chapter", "")
                week_str = parts[3].replace("Week", "")
                chapter_number = int(chapter_str)
                week_number = int(week_str)
                
                # Determine title
                title = f"VIP Chapter {chapter_number} Week {week_number}"
                
                # Schedule for next Sunday (default)
                now = datetime.now()
                days_until_sunday = (6 - now.weekday()) % 7
                if days_until_sunday == 0:
                    days_until_sunday = 7
                next_sunday = now + timedelta(days=days_until_sunday + (week_number - 1) * 7)
                start_time = next_sunday.replace(hour=8, minute=0, second=0)
                end_time = start_time + timedelta(hours=24)
                
                db.execute('''
                    INSERT INTO vip_questions (course_code, week_number, chapter_number, title, question_file, start_time, end_time, duration_hours, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 24, 0, ?)
                ''', (course_code, week_number, chapter_number, title, filename, start_time.isoformat(), end_time.isoformat(), now.isoformat()))
                
                vip_added += 1
                logger.info("  Found VIP: " + filename)
        except Exception as e:
            logger.warning("  Could not parse VIP file: " + filename)
    
    if not files and not vip_files:
        return 0
    
    added = 0
    skipped = 0
    
    # First, handle NESTED structure: content/courses/{Course}/chapter{N}/part{M}.html
    nested_added = 0
    if LESSONS_DIR.exists():
        for course_dir in LESSONS_DIR.iterdir():
            if not course_dir.is_dir():
                continue
            course_code = course_dir.name
            
            for chapter_dir in course_dir.iterdir():
                if not chapter_dir.is_dir():
                    continue
                
                if 'chapter' not in chapter_dir.name:
                    continue
                
                try:
                    chapter_num = int(chapter_dir.name.replace('chapter', ''))
                except:
                    continue
                
                for part_file in chapter_dir.glob("*.html"):
                    filename = part_file.name
                    
                    # New path: {course}/chapter{N}/part{M}.html
                    file_path = f"{course_code}/{chapter_dir.name}/{filename}"
                    
                    existing = db.query_one("SELECT id FROM lessons WHERE file_path = ?", (file_path,))
                    if existing:
                        continue
                    
                    try:
                        part_num = int(filename.replace('part', '').replace('.html', ''))
                    except:
                        continue
                    
                    db.execute('''
                        INSERT INTO lessons (course_code, chapter_number, part_number, chapter_title, part_title, file_path, university_specific, estimated_minutes, is_premium, is_active, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, NULL, 10, 1, 0, ?)
                    ''', (course_code, chapter_num, part_num, f'Chapter {chapter_num}', f'Part {part_num}', file_path, datetime.now().isoformat()))
                    
                    nested_added += 1
                    logger.info(f"  Found lesson: {file_path}")
    
    # New nested structure: content/worksheets/{Course}/chapter{N}/part{M}.json
    ws_added = 0
    if WORKSHEETS_DIR.exists():
        for course_dir in WORKSHEETS_DIR.iterdir():
            if not course_dir.is_dir():
                continue
            course_code = course_dir.name
            
            for chapter_dir in course_dir.iterdir():
                if not chapter_dir.is_dir():
                    continue
                
                if "chapter" not in chapter_dir.name:
                    continue
                
                try:
                    chapter_num = int(chapter_dir.name.replace("chapter", ""))
                except:
                    continue
                
                for ws_file in chapter_dir.glob("*.json"):
                    filename = ws_file.name
                    file_path = f"{course_code}/{chapter_dir.name}/{filename}"
                    
                    existing = db.query_one("SELECT id FROM worksheets WHERE question_file = ?", (file_path,))
                    if existing:
                        continue
                    
                    name = filename.replace(".json", "")
                    
                    if name == "full":
                        title = f"Full Chapter {chapter_num} Worksheet"
                    elif "part" in name:
                        try:
                            part_num = int(name.replace("part", ""))
                        except:
                            part_num = 0
                        title = f"Part {part_num} Practice Worksheet"
                    else:
                        title = f"Chapter {chapter_num} Worksheet"
                    
                    db.execute(
                        "INSERT INTO worksheets (course_code, chapter_number, title, question_file, is_active, created_at) VALUES (?, ?, ?, ?, 1, ?)",
                        (course_code, chapter_num, title, file_path, datetime.now().isoformat())
                    )
                    
                    ws_added += 1
                    logger.info(f"  Found worksheet: {file_path}")
    if nested_added > 0 or ws_added > 0:
        logger.info(f"  Added {nested_added} lessons, {ws_added} worksheets from new structure")
        return nested_added + ws_added
    
    for file in files:
        filename = file.name
        
        # Check if already in database
        existing_lesson = db.query_one("SELECT id FROM lessons WHERE file_path = ?", (filename,))
        existing_ws = db.query_one("SELECT id FROM worksheets WHERE question_file = ?", (filename,))
        
        if existing_lesson or existing_ws:
            skipped += 1
            continue
        
        try:
            name_without_ext = filename.rsplit(".", 1)[0]
            parts = name_without_ext.split("_")
            
            if len(parts) < 3:
                skipped += 1
                continue
            
            # ============================================
            # JSON FILES → WORKSHEETS TABLE
            # ============================================
            if filename.endswith(".json"):
                course_code = parts[1]
                
                if course_code not in valid_course_codes:
                    skipped += 1
                    continue
                
                # Parse chapter number
                chapter_number = 0
                if "chapter" in name_without_ext:
                    try:
                        chapter_str = name_without_ext.split("chapter")[1].split("_")[0]
                        chapter_number = int(chapter_str)
                    except:
                        chapter_number = 0
                
                # Determine title
                if "full" in name_without_ext:
                    title = "Full Chapter {} Worksheet".format(chapter_number)
                elif "part" in name_without_ext and "worksheet" in name_without_ext:
                    part_number = 0
                    try:
                        part_str = name_without_ext.split("part")[1].split("_")[0]
                        part_number = int(part_str)
                    except:
                        part_number = 0
                    title = "Part {} Practice Worksheet".format(part_number)
                else:
                    title = "Chapter {} Worksheet".format(chapter_number)
                
                db.execute(
                    "INSERT INTO worksheets (course_code, chapter_number, title, question_file, is_active, created_at) VALUES (?, ?, ?, ?, 1, ?)",
                    (course_code, chapter_number, title, filename, datetime.now().isoformat())
                )
                added += 1
                logger.info("  Found worksheet: " + filename)
            
            # ============================================
            # HTML FILES → LESSONS TABLE
            # ============================================
            elif filename.endswith(".html"):
                course_code = parts[1]
                
                if course_code not in valid_course_codes:
                    skipped += 1
                    continue
                
                # Parse chapter and part
                if "chapter" in name_without_ext and "part" in name_without_ext:
                    chapter_number = 0
                    part_number = 0
                    
                    try:
                        chapter_str = name_without_ext.split("chapter")[1].split("_")[0]
                        chapter_number = int(chapter_str)
                    except:
                        chapter_number = 0
                    
                    try:
                        part_str = name_without_ext.split("part")[1].split("_")[0]
                        part_number = int(part_str)
                    except:
                        part_number = 0
                    
                    university_specific = None
                    if parts[0] not in ["all", "free"]:
                        university_specific = parts[0]
                    
                    is_free = parts[0] == "free"
                    is_premium = 0 if is_free else 1
                    
                    db.execute(
                        "INSERT INTO lessons (course_code, chapter_number, part_number, chapter_title, part_title, file_path, university_specific, estimated_minutes, is_premium, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, 5, ?, 1, ?)",
                        (course_code, chapter_number, part_number, "Chapter {}".format(chapter_number), "Part {}".format(part_number), filename, university_specific, is_premium, datetime.now().isoformat())
                    )
                    added += 1
                    logger.info("  Found lesson: " + filename)
                else:
                    skipped += 1
            else:
                skipped += 1
                
        except Exception as e:
            logger.warning("  Could not parse: " + filename + " - " + str(e))
            skipped += 1
    
    # ============================================
    # SCAN PAST EXAMS FOLDER
    # ============================================
    from core.paths import BASE_DIR
    PAST_EXAMS_DIR = BASE_DIR / "content" / "past_exams"
    past_exam_added = 0
    
    if PAST_EXAMS_DIR.exists():
        past_files = []
        for uni_dir in PAST_EXAMS_DIR.iterdir():
            if uni_dir.is_dir():
                past_files.extend(list(uni_dir.glob("*.html")))
                past_files.extend(list(uni_dir.glob("*.json")))
        # Also check root
        past_files.extend(list(PAST_EXAMS_DIR.glob("*.html")))
        past_files.extend(list(PAST_EXAMS_DIR.glob("*.json")))
        
        for past_file in past_files:
            filename = past_file.name
            
            existing = db.query_one("SELECT id FROM past_exams WHERE file_path = ?", (filename,))
            if existing:
                continue
            
            # Parse: {UniversityShort}_{CourseCode}_{Year}_{ExamType}.{ext}
            name_without_ext = filename.rsplit(".", 1)[0]
            parts = name_without_ext.split("_")
            
            if len(parts) >= 4:
                university = parts[0]
                course_code = parts[1]
                year = int(parts[2])
                exam_type = parts[3].capitalize()
                
                # Get course title
                course = db.query_one("SELECT title FROM courses WHERE code = ?", (course_code,))
                course_title = course['title'] if course else course_code
                
                db.execute('''
                    INSERT INTO past_exams (university, course_code, course_title, year, exam_type, file_path, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, 0, ?)
                ''', (university, course_code, course_title, year, exam_type, filename, datetime.now().isoformat()))
                
                past_exam_added += 1
                logger.info("  Found past exam: " + filename)
    
    # REMOVE database entries for files that no longer exist
    removed = 0
    current_files = set()
    for file in files:
        current_files.add(file.name)
    
    # Add all files from lessons sub-folders
    if LESSONS_DIR.exists():
        for course_dir in LESSONS_DIR.iterdir():
            if course_dir.is_dir():
                for chapter_dir in course_dir.iterdir():
                    if chapter_dir.is_dir():
                        for f in chapter_dir.glob("*.html"):
                            current_files.add(f.name)
                        for f in chapter_dir.glob("*.json"):
                            current_files.add(f.name)
    
    # Add all VIP files from sub-folders
    if VIP_QUESTIONS_DIR.exists():
        for course_dir in VIP_QUESTIONS_DIR.iterdir():
            if course_dir.is_dir():
                for f in course_dir.glob("*.json"):
                    current_files.add(f.name)
    
    # Add past exam files to current_files (scan SUB-FOLDERS)
    PAST_EXAMS_DIR = BASE_DIR / "content" / "past_exams"
    if PAST_EXAMS_DIR.exists():
        # Scan sub-folders
        for uni_dir in PAST_EXAMS_DIR.iterdir():
            if uni_dir.is_dir():
                for past_file in uni_dir.glob("*.html"):
                    current_files.add(past_file.name)
                for past_file in uni_dir.glob("*.json"):
                    current_files.add(past_file.name)
        # Also root level
        for past_file in PAST_EXAMS_DIR.glob("*.html"):
            current_files.add(past_file.name)
        for past_file in PAST_EXAMS_DIR.glob("*.json"):
            current_files.add(past_file.name)
    
    all_db_lessons = db.query("SELECT id, file_path FROM lessons")
    for db_lesson in all_db_lessons:
        if db_lesson["file_path"] not in current_files:
            db.execute("DELETE FROM lessons WHERE id = ?", (db_lesson["id"],))
            removed += 1
            logger.info("  Removed (file deleted): " + db_lesson["file_path"])
    
    all_db_worksheets = db.query("SELECT id, question_file FROM worksheets")
    for db_ws in all_db_worksheets:
        if db_ws["question_file"] not in current_files:
            db.execute("DELETE FROM worksheets WHERE id = ?", (db_ws["id"],))
            removed += 1
            logger.info("  Removed (file deleted): " + db_ws["question_file"])
    
    # Remove deleted past exam files
    all_db_exams = db.query("SELECT id, file_path FROM past_exams")
    for db_exam in all_db_exams:
        if db_exam["file_path"] not in current_files:
            db.execute("DELETE FROM past_exams WHERE id = ?", (db_exam["id"],))
            removed += 1
            logger.info("  Removed (file deleted): " + db_exam["file_path"])
    
    logger.info("  Added " + str(added) + " lessons/worksheets, " + str(vip_added) + " VIPs, " + str(past_exam_added) + " past exams, removed " + str(removed))
    return added + vip_added + past_exam_added



def execute_schema(db):
    """Execute schema statements one at a time"""
    statements = []
    current_statement = []
    
    for line in SCHEMA.split('\n'):
        line = line.strip()
        if not line or line.startswith('--'):
            continue
        current_statement.append(line)
        if line.endswith(';'):
            statements.append(' '.join(current_statement))
            current_statement = []
    
    for statement in statements:
        try:
            db.execute(statement)
        except Exception as e:
            logger.warning(f"Schema statement skipped: {e}")


def initialize_database():
    logger.info("=" * 50)
    logger.info("UNIYO LMS - Database Initialization")
    logger.info("=" * 50)
    
    ensure_directories()
    
    db = Database()
    db.connect()
    logger.info(f"Database: {DB_PATH}")
    
    execute_schema(db)
    logger.info("Tables created")
    
    for index in INDEXES:
        db.execute(index)
    logger.info(f"{len(INDEXES)} indexes created")
    
    seed_courses(db)
    seed_default_admin(db)
    scan_content_folder(db)
    
    db.checkpoint()
    
    logger.info("=" * 50)
    logger.info("Database initialization complete!")
    logger.info("Admin: admin / Admin@123")
    logger.info("=" * 50)
    return True

if __name__ == '__main__':
    initialize_database()
