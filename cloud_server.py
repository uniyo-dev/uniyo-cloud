"""
UNIYO LMS - Cloud Server (Render Deployment)
"""

from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).resolve().parent

for folder in ['logs', 'uploads', 'backups', 'certificates', 'certificates/pdf', 'certificates/qr', 'database', 'flask_session']:
    (BASE_DIR / folder).mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(BASE_DIR))

# Create tables and seed data
try:
    from pg_schema import create_tables, seed_data
    from core.db import db
    db.connect()
    create_tables(db)
    seed_data(db)
    print("✓ PostgreSQL ready")
except Exception as e:
    print(f"Database init warning: {e}")

from server import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
