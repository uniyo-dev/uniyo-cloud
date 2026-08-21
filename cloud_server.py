"""
UNIYO LMS - Server Entry (Fly.io)
"""

from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).resolve().parent

for folder in ['logs', 'uploads', 'backups', 'certificates', 'database', 'flask_session']:
    (BASE_DIR / folder).mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(BASE_DIR))

try:
    from init_database import initialize_database
    initialize_database()
    print("✓ Database ready")
except Exception as e:
    print(f"Warning: {e}")

# Clear sessions on server start
try:
    from core.db import db
    db.execute('UPDATE active_sessions SET is_active = 0')
    print('Sessions cleared')
except:
    pass

# Clear all sessions on server start (so students can login again)
try:
    from core.db import db
    db.execute("UPDATE active_sessions SET is_active = 0")
    print("✓ Sessions cleared")
except Exception as e:
    print(f"Session cleanup: {e}")

from server import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
