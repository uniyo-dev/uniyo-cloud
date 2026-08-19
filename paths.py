"""
UNIYO LMS - Path Management
"""

from pathlib import Path
import os
import sys

# Platform detection
IS_TERMUX = os.path.exists('/data/data/com.termux')
IS_WINDOWS = sys.platform.startswith('win')
IS_LINUX = sys.platform.startswith('linux') and not IS_TERMUX

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Core paths
DB_PATH = BASE_DIR / "database" / "UNIYO.db"
BACKUP_DIR = BASE_DIR / "backups"
LOG_DIR = BASE_DIR / "logs"

# Content paths - all under content/
CONTENT_DIR = BASE_DIR / "content"
LESSONS_DIR = CONTENT_DIR / "courses"
WORKSHEETS_DIR = CONTENT_DIR / "worksheets"      # New structure: content/worksheets/{Course}/chapter{N}/part{M}.json
VIP_QUESTIONS_DIR = BASE_DIR / "vip_questions"
PAST_EXAMS_DIR = CONTENT_DIR / "past_exams"
QUESTIONS_DIR = BASE_DIR / "questions"

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Upload paths
UPLOADS_DIR = BASE_DIR / "uploads"
STUDENT_PHOTOS_DIR = UPLOADS_DIR / "students"
PAYMENT_SCREENSHOTS_DIR = UPLOADS_DIR / "payments"
ANNOUNCEMENT_IMAGES_DIR = UPLOADS_DIR / "announcements"

# Certificate paths
CERTIFICATES_DIR = BASE_DIR / "certificates"
CERTIFICATE_PDF_DIR = CERTIFICATES_DIR / "pdf"
CERTIFICATE_QR_DIR = CERTIFICATES_DIR / "qr"

# Metadata
METADATA_DIR = BASE_DIR / "metadata"

def get_database_uri():
    if IS_WINDOWS:
        return f"file:{DB_PATH.as_posix()}?mode=rwc"
    return str(DB_PATH)

def get_hotspot_ip():
    if IS_TERMUX:
        return "192.168.43.1"
    elif IS_WINDOWS:
        return "192.168.137.1"
    return "127.0.0.1"

def ensure_directories():
    directories = [
        DB_PATH.parent, BACKUP_DIR, LOG_DIR,
        LESSONS_DIR, WORKSHEETS_DIR, VIP_QUESTIONS_DIR, PAST_EXAMS_DIR,
        TEMPLATES_DIR, STATIC_DIR,
        UPLOADS_DIR, STUDENT_PHOTOS_DIR, PAYMENT_SCREENSHOTS_DIR,
        ANNOUNCEMENT_IMAGES_DIR, CERTIFICATES_DIR, CERTIFICATE_PDF_DIR,
        CERTIFICATE_QR_DIR, METADATA_DIR, QUESTIONS_DIR,
    ]
    created = []
    for directory in directories:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            created.append(directory.name)
    return created
