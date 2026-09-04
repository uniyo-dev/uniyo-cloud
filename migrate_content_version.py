"""
Migration: Add version control to content tables in Turso
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.db import Database

def migrate():
    db = Database()
    db.connect()
    print("Connecting to Turso...")
    
    # Create content_archive table
    try:
        db.execute('''
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
            )
        ''')
        print("✓ content_archive table created")
    except Exception as e:
        print(f"✗ Error creating content_archive: {e}")
    
    # Add version columns
    columns = [
        ('lessons', 'content_version', 'INTEGER DEFAULT 1'),
        ('lessons', 'file_hash', 'TEXT'),
        ('worksheets', 'content_version', 'INTEGER DEFAULT 1'),
        ('worksheets', 'file_hash', 'TEXT'),
        ('past_exams', 'content_version', 'INTEGER DEFAULT 1'),
        ('past_exams', 'file_hash', 'TEXT'),
    ]
    
    for table, col, col_type in columns:
        try:
            # Check if column exists
            result = db.query_one(f"SELECT * FROM {table} LIMIT 1")
            if result:
                existing_cols = list(result.keys())
            else:
                existing_cols = []
            
            if col in existing_cols:
                print(f"  ⏭ {table}.{col} already exists")
            else:
                db.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
                print(f"  ✓ Added {table}.{col}")
        except Exception as e:
            print(f"  ✗ Error adding {table}.{col}: {e}")
    
    print("\n✓ Migration complete")
    db.close()
    return True

if __name__ == '__main__':
    migrate()
