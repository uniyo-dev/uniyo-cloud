"""
UNIYO LMS - Helper Functions
"""

import os
import uuid
import secrets
import logging
from pathlib import Path
from datetime import datetime
from werkzeug.utils import secure_filename

from core.paths import BASE_DIR, STUDENT_PHOTOS_DIR, PAYMENT_SCREENSHOTS_DIR, ANNOUNCEMENT_IMAGES_DIR, CERTIFICATE_QR_DIR

def generate_unique_filename(original_filename, prefix="file"):
    extension = Path(original_filename).suffix.lower()
    unique_id = uuid.uuid4().hex[:12]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}_{unique_id}{extension}"

def save_student_photo(file):
    if not file or file.filename == '':
        return 'default.png'
    filename = generate_unique_filename(file.filename, prefix="student")
    file_path = STUDENT_PHOTOS_DIR / filename
    file.save(str(file_path))
    return filename

def save_payment_screenshot(file, student_id):
    if not file or file.filename == '':
        return None
    filename = generate_unique_filename(file.filename, prefix=f"payment_{student_id}")
    file_path = PAYMENT_SCREENSHOTS_DIR / filename
    file.save(str(file_path))
    return filename

def save_announcement_image(file):
    if not file or file.filename == '':
        return None
    filename = generate_unique_filename(file.filename, prefix="announcement")
    file_path = ANNOUNCEMENT_IMAGES_DIR / filename
    file.save(str(file_path))
    return filename

def generate_session_token():
    return secrets.token_hex(32)

def generate_certificate_number(month_year=None, rank=None):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_hex = secrets.token_hex(3).upper()
    if month_year and rank:
        month_clean = month_year.replace('-', '')
        return f"UNIYO-{month_clean}-RANK{rank}-{random_hex}"
    return f"UNIYO-COMP-{timestamp}-{random_hex}"

def generate_verification_token():
    return secrets.token_urlsafe(32)

def hash_password(password):
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password)

def verify_password(password_hash, password):
    from werkzeug.security import check_password_hash
    return check_password_hash(password_hash, password)

def generate_qr_data_uri(data):
    import qrcode
    from io import BytesIO
    import base64
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="#0B0F19", back_color="#FFFFFF")
    buffer = BytesIO()
    qr_image.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{qr_base64}"

def get_current_timestamp():
    return datetime.now().isoformat()

def format_date(date_string, format='%d %b %Y, %I:%M %p'):
    try:
        date_obj = datetime.fromisoformat(date_string)
        return date_obj.strftime(format)
    except:
        return date_string

def get_month_year(date_string=None):
    if date_string:
        date_obj = datetime.fromisoformat(date_string)
    else:
        date_obj = datetime.now()
    return date_obj.strftime('%Y-%m')

def get_client_ip(request):
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

def get_device_info(request):
    return request.user_agent.string

def sanitize_input(text):
    if not text:
        return ''
    return text.strip()

def calculate_percentage(score, total):
    if total == 0:
        return 0
    return round((score / total) * 100, 2)

# get_letter_grade is defined in core/constants.py
# Use: from core.constants import get_letter_grade

def setup_logging():
    from core.paths import LOG_DIR
    log_file = LOG_DIR / f"uniyo_{datetime.now().strftime('%Y%m%d')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler(str(log_file)), logging.StreamHandler()]
    )
    return logging.getLogger('UNIYO')

logger = setup_logging()
