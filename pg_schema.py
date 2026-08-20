"""PostgreSQL Schema for UNIYO"""

def create_tables(db):
    """Create all tables in PostgreSQL"""
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id SERIAL PRIMARY KEY,
            code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            credit_hours INTEGER DEFAULT 3,
            semester INTEGER DEFAULT 1,
            stream TEXT DEFAULT 'Common',
            description TEXT,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
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
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS active_sessions (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
            session_token TEXT UNIQUE NOT NULL,
            device_info TEXT,
            ip_address TEXT,
            created_at TEXT NOT NULL,
            last_activity TEXT,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id SERIAL PRIMARY KEY,
            course_code TEXT REFERENCES courses(code) ON DELETE CASCADE,
            chapter_number INTEGER NOT NULL,
            part_number INTEGER NOT NULL,
            chapter_title TEXT NOT NULL,
            part_title TEXT NOT NULL,
            file_path TEXT UNIQUE NOT NULL,
            university_specific TEXT,
            estimated_minutes INTEGER DEFAULT 5,
            is_premium INTEGER DEFAULT 1,
            is_active INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            UNIQUE(course_code, chapter_number, part_number, university_specific)
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS lesson_progress (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
            lesson_id INTEGER REFERENCES lessons(id) ON DELETE CASCADE,
            progress_percent INTEGER DEFAULT 0,
            last_position INTEGER DEFAULT 0,
            is_completed INTEGER DEFAULT 0,
            completed_at TEXT,
            UNIQUE(student_id, lesson_id)
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS worksheets (
            id SERIAL PRIMARY KEY,
            course_code TEXT REFERENCES courses(code) ON DELETE CASCADE,
            chapter_number INTEGER NOT NULL,
            title TEXT NOT NULL,
            question_file TEXT NOT NULL,
            is_active INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS worksheet_attempts (
            id SERIAL PRIMARY KEY,
            worksheet_id INTEGER REFERENCES worksheets(id) ON DELETE CASCADE,
            student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
            attempt_number INTEGER DEFAULT 1,
            answers_json TEXT,
            score INTEGER,
            total INTEGER,
            is_completed INTEGER DEFAULT 0,
            completed_at TEXT
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS vip_questions (
            id SERIAL PRIMARY KEY,
            course_code TEXT REFERENCES courses(code) ON DELETE CASCADE,
            chapter_number INTEGER NOT NULL,
            week_number INTEGER NOT NULL,
            month_number INTEGER DEFAULT 1,
            title TEXT NOT NULL,
            question_file TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration_hours INTEGER NOT NULL,
            is_active INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS vip_attempts (
            id SERIAL PRIMARY KEY,
            vip_question_id INTEGER REFERENCES vip_questions(id) ON DELETE CASCADE,
            student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
            score INTEGER,
            total INTEGER,
            time_spent_seconds INTEGER,
            answers_json TEXT,
            completed_at TEXT,
            UNIQUE(vip_question_id, student_id)
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS past_exams (
            id SERIAL PRIMARY KEY,
            university TEXT NOT NULL,
            course_code TEXT REFERENCES courses(code) ON DELETE CASCADE,
            course_title TEXT NOT NULL,
            year INTEGER NOT NULL,
            exam_type TEXT NOT NULL,
            file_path TEXT UNIQUE NOT NULL,
            is_active INTEGER DEFAULT 0,
            description TEXT,
            topics_covered TEXT,
            difficulty_level TEXT,
            time_limit_minutes INTEGER DEFAULT 120,
            total_questions INTEGER DEFAULT 0,
            semester INTEGER DEFAULT 1,
            marks_description TEXT,
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            dislikes INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS past_exam_ratings (
            id SERIAL PRIMARY KEY,
            past_exam_id INTEGER REFERENCES past_exams(id) ON DELETE CASCADE,
            student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
            rating TEXT NOT NULL CHECK(rating IN ('like', 'dislike')),
            created_at TEXT NOT NULL,
            UNIQUE(past_exam_id, student_id)
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS past_exam_attempts (
            id SERIAL PRIMARY KEY,
            past_exam_id INTEGER REFERENCES past_exams(id) ON DELETE CASCADE,
            student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
            score REAL DEFAULT 0,
            total_points REAL DEFAULT 0,
            percentage REAL DEFAULT 0,
            answers_json TEXT,
            time_spent_seconds INTEGER DEFAULT 0,
            completed_at TEXT NOT NULL
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('super_admin', 'content_manager', 'payment_verifier')),
            reset_token TEXT,
            reset_token_expiry TEXT,
            must_change_password INTEGER DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT 'now'
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
            payment_method TEXT NOT NULL,
            transaction_number TEXT UNIQUE,
            amount REAL NOT NULL DEFAULT 200.00,
            payment_status TEXT DEFAULT 'pending',
            screenshot_path TEXT,
            submitted_at TEXT NOT NULL,
            reviewed_at TEXT,
            reviewed_by INTEGER REFERENCES admins(id) ON DELETE SET NULL,
            rejection_reason TEXT,
            resubmit_count INTEGER DEFAULT 0
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            priority TEXT DEFAULT 'normal',
            image TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS certificates (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
            certificate_type TEXT NOT NULL,
            rank INTEGER,
            month_year TEXT,
            certificate_number TEXT UNIQUE NOT NULL,
            verification_token TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            issue_date TEXT NOT NULL,
            issued_by INTEGER REFERENCES admins(id) ON DELETE SET NULL
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'general',
            is_read INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS security_logs (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
            event_type TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id SERIAL PRIMARY KEY,
            admin_id INTEGER REFERENCES admins(id) ON DELETE CASCADE,
            action TEXT NOT NULL,
            target_table TEXT NOT NULL,
            target_id INTEGER,
            details TEXT,
            ip_address TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    print("✓ All PostgreSQL tables created")

def seed_data(db):
    """Seed initial data"""
    from core.helpers import hash_password
    from core.constants import COURSES
    
    # Create default admin
    existing = db.query_one("SELECT id FROM admins WHERE username = 'admin'")
    if not existing:
        password_hash = hash_password("Admin@123")
        db.execute("INSERT INTO admins (username, password_hash, full_name, role, must_change_password) VALUES ('admin', %s, 'System Administrator', 'super_admin', 1)", (password_hash,))
        print("✓ Default admin created")
    
    # Seed courses
    for course in COURSES:
        existing = db.query_one("SELECT id FROM courses WHERE code = %s", (course['code'],))
        if not existing:
            db.execute("INSERT INTO courses (code, title, credit_hours, semester, stream, description, is_active) VALUES (%s, %s, %s, %s, %s, %s, 1)", 
                      (course['code'], course['title'], course.get('credit_hours', 3), course.get('semester', 1), course.get('stream', 'Common'), course.get('description', '')))
    print("✓ Courses seeded")

if __name__ == '__main__':
    from core.db import db
    db.connect()
    create_tables(db)
    seed_data(db)
    db.close()
