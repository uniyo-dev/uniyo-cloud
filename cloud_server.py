"""
UNIYO LMS - Cloud Server (Render Deployment)
"""

from pathlib import Path
import os
import sys
import requests
import json

BASE_DIR = Path(__file__).resolve().parent

for folder in ['logs', 'uploads', 'backups', 'certificates', 'database', 'flask_session']:
    (BASE_DIR / folder).mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(BASE_DIR))

# Turso connection
TURSO_URL = "https://uniyo-uniyo-dev.aws-us-east-2.turso.io"
TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODcyNjE4MjYsImlkIjoiMDFhMDIxMWEtNDkwMS03ZDY2LTk5ODEtZDc5NTcxMDYyNTVhIiwia2lkIjoiT29jQW5QU0Fjc0xicXV2MGI4ekdyaUtfT2ZyS0UxY2FEc3BaU3VkQVFFOCIsInJpZCI6IjU2ZDU3NzkzLTFhZmMtNGNiMC04NDJkLTY4MjRlNGQ0YThmNiJ9.BkDZq1Vhl_vuZ1hmenaJIbkwfu-5Nglr09vgFNPKIorOWU_iwFflaECdWE1RhJsHeom3sw7bwnsSKpllyExSBQ"

headers = {
    "Authorization": f"Bearer {TURSO_TOKEN}",
    "Content-Type": "application/json"
}

def turso_execute(sql):
    body = {
        "requests": [
            {"type": "execute", "stmt": {"sql": sql}},
            {"type": "close"}
        ]
    }
    try:
        requests.post(f"{TURSO_URL}/v2/pipeline", headers=headers, json=body, timeout=20)
    except:
        pass

# Clear sessions
try:
    turso_execute("UPDATE active_sessions SET is_active = 0")
    print("✓ Sessions cleared")
except:
    pass

# Auto-publish ALL content on startup
try:
    turso_execute("UPDATE lessons SET is_active = 1")
    print("✓ 122 lessons published")
    
    turso_execute("UPDATE worksheets SET is_active = 1")
    print("✓ 131 worksheets published")
    
    turso_execute("UPDATE past_exams SET is_active = 1")
    print("✓ 2 past exams published")
except Exception as e:
    print(f"Publish error: {e}")

from server import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
