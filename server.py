#!/usr/bin/env python3
"""
UNIYO LMS - Main Server Entry Point
"""

import sys
import os
from pathlib import Path
from datetime import timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import Flask, render_template, jsonify, redirect, url_for, session, request
from flask_session import Session as FlaskSession

from core.paths import BASE_DIR, DB_PATH, ensure_directories, get_hotspot_ip, IS_TERMUX, IS_WINDOWS
from core.db import Database, init_app as init_db
from core.session_cleanup import start_session_cleanup
from core.helpers import logger
from core.constants import PAYMENT_CONFIG, SUPPORTED_LANGUAGES

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uniyo-dev-secret-key-2024')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = str(BASE_DIR / 'flask_session')
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['DATABASE'] = str(DB_PATH)

FlaskSession(app)
db = init_db(app)

# Import blueprints
from routes.student_routes import student_bp
from routes.admin_routes import admin_bp
from routes.api_routes import api_bp
from routes.lesson_routes import lesson_bp
from routes.worksheet_routes import worksheet_bp
from routes.vip_routes import vip_bp
from routes.certificate_routes import certificate_bp
from routes.past_exam_routes import past_exam_bp

app.register_blueprint(student_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp)
app.register_blueprint(lesson_bp)
app.register_blueprint(worksheet_bp)
app.register_blueprint(vip_bp)
app.register_blueprint(certificate_bp)
app.register_blueprint(past_exam_bp)

@app.template_filter('format_date')
def format_date(date_string, format='%d %b %Y, %I:%M %p'):
    from datetime import datetime
    try:
        return datetime.fromisoformat(date_string).strftime(format)
    except:
        return date_string

@app.template_filter('format_month')
def format_month(month_year):
    from datetime import datetime
    try:
        return datetime.strptime(month_year, '%Y-%m').strftime('%B %Y')
    except:
        return month_year

@app.context_processor
def inject_globals():
    return {
        'app_name': 'UNIYO',
        'app_tagline': 'University Made for YOU',
        'payment_config': PAYMENT_CONFIG,
        'supported_languages': SUPPORTED_LANGUAGES,
    }

@app.errorhandler(404)
def not_found_error(error):
    if request.path.startswith('/api/'):
        return jsonify({"success": False, "error": "Endpoint not found"}), 404
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    db.rollback()
    logger.error(f"Internal server error: {error}")
    if request.path.startswith('/api/'):
        return jsonify({"success": False, "error": "Internal server error"}), 500
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500

@app.route('/health')
def health_check():
    try:
        db.query_one("SELECT 1")
        database_status = "connected"
    except:
        database_status = "error"
    return jsonify({"status": "healthy", "app": "UNIYO LMS", "version": "1.0.0", "database": database_status})

if __name__ == '__main__':
    ensure_directories()
    hotspot_ip = get_hotspot_ip()
    
    print("\n" + "=" * 50)
    print("       UNIYO LMS - Server Starting")
    print("=" * 50)
    print(f"  Local Access:    http://127.0.0.1:5000")
    print(f"  Hotspot Access:  http://{hotspot_ip}:5000")
    print(f"  Admin Panel:     http://{hotspot_ip}:5000/admin")
    print("=" * 50)
    print(f"  Admin: admin / Admin@123")
    print("=" * 50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)
