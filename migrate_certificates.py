"""
Migration Script: Add missing columns to certificates table in Turso
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.db import Database

def migrate():
    db = Database()
    db.connect()
    print("Connecting to Turso...")
    
    # Check if columns already exist
    try:
        result = db.query_one("SELECT * FROM certificates LIMIT 1")
        if result:
            existing_cols = list(result.keys())
        else:
            existing_cols = []
    except Exception as e:
        print(f"Error checking columns: {e}")
        return
    
    columns_to_add = {
        'full_name': 'TEXT',
        'university': 'TEXT',
        'stream': 'TEXT',
        'phone': 'TEXT',
        'amount': 'REAL',
        'payment_method': 'TEXT',
        'transaction_number': 'TEXT'
    }
    
    added = 0
    skipped = 0
    
    for col_name, col_type in columns_to_add.items():
        if col_name in existing_cols:
            print(f"  ⏭ {col_name} already exists")
            skipped += 1
        else:
            try:
                db.execute(f"ALTER TABLE certificates ADD COLUMN {col_name} {col_type}")
                print(f"  ✓ Added {col_name} ({col_type})")
                added += 1
            except Exception as e:
                print(f"  ✗ Failed to add {col_name}: {e}")
    
    print(f"\nMigration complete: {added} added, {skipped} skipped")
    
    # Verify
    result = db.query_one("SELECT * FROM certificates LIMIT 1")
    if result:
        print(f"✓ Certificates table now has {len(result.keys())} columns")
    
    db.close()
    return True

if __name__ == '__main__':
    migrate()
