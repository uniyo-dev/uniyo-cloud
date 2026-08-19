"""
UNIYO LMS - Session Cleanup
Background task to clean expired sessions
"""

import threading
import time
from datetime import datetime, timedelta
from core.db import get_db
from core.helpers import logger

def cleanup_expired_sessions():
    """Clean up expired sessions from database"""
    db = get_db()
    try:
        current_time = datetime.now()
        cutoff_24h = (current_time - timedelta(hours=24)).isoformat()
        db.execute('''
            UPDATE active_sessions SET is_active = 0 
            WHERE last_activity < ? AND is_active = 1
        ''', (cutoff_24h,))
        
        cutoff_7d = (current_time - timedelta(days=7)).isoformat()
        db.execute('''
            DELETE FROM active_sessions 
            WHERE created_at < ? AND is_active = 0
        ''', (cutoff_7d,))
        
        db.checkpoint()
        logger.info("Session cleanup completed")
    except Exception as e:
        logger.error(f"Session cleanup failed: {e}")

def cleanup_expired_subscriptions():
    """Update expired premium subscriptions"""
    db = get_db()
    current_time = datetime.now().isoformat()
    db.execute('''
        UPDATE students SET subscription_status = 'expired'
        WHERE subscription_status = 'premium' AND subscription_expires < ?
    ''', (current_time,))
    logger.info("Subscription cleanup completed")

def session_cleanup_task():
    """Background task that runs cleanup periodically"""
    while True:
        cleanup_expired_sessions()
        cleanup_expired_subscriptions()
        time.sleep(3600)  # Run every hour

def start_session_cleanup():
    """Start background cleanup thread"""
    cleanup_thread = threading.Thread(target=session_cleanup_task, daemon=True, name="SessionCleanup")
    cleanup_thread.start()
    logger.info("Session cleanup thread started")
    return cleanup_thread
