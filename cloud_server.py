"""
UNIYO LMS - Cloud Server (Render Deployment)
"""

from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).resolve().parent

for folder in ['logs', 'uploads', 'backups', 'certificates', 'database', 'flask_session']:
    (BASE_DIR / folder).mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(BASE_DIR))

# Clear sessions on server start
try:
    from core.db import db
    db.execute("UPDATE active_sessions SET is_active = 0")
    print("✓ Sessions cleared")
except:
    pass

# Run scanner to auto-publish all content
try:
    from init_database import initialize_database
    initialize_database()
    print("✓ Content auto-published")
except Exception as e:
    print(f"Scanner warning: {e}")

from server import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
