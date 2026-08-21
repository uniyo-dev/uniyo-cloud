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

# Auto-sync content on every start
try:
    from sync_content import sync_all_content
    sync_all_content()
    print("✓ Content auto-synced")
except Exception as e:
    print(f"Sync error: {e}")

from server import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
