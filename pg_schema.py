"""PostgreSQL Schema for UNIYO"""

def create_tables(db):
    """Create all tables in PostgreSQL"""
    
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
        CREATE TABLE IF NOT EXISTS notifications (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'general',
            is_read INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')
    
    print("✓ PostgreSQL tables created")

if __name__ == '__main__':
    from core.db import db
    db.connect()
    create_tables(db)
    db.close()
