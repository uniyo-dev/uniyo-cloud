"""
PythonAnywhere WSGI Entry Point
"""

import sys
from pathlib import Path

# Set project path
project_path = '/home/uniyo-dev/UNIYO'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Initialize database
try:
    from init_database import initialize_database
    initialize_database()
except:
    pass

# Import Flask app
from server import app as application
