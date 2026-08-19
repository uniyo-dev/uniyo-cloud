"""
UNIYO LMS - Database Connection & Query Helpers
"""

import sqlite3
import sys
from pathlib import Path
from contextlib import contextmanager

from core.paths import DB_PATH, IS_WINDOWS, get_database_uri

class Database:
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        if self._connection is None:
            if IS_WINDOWS:
                self._connection = sqlite3.connect(
                    get_database_uri(), uri=True, check_same_thread=False,
                    timeout=30, isolation_level=None
                )
            else:
                self._connection = sqlite3.connect(
                    str(DB_PATH), check_same_thread=False,
                    timeout=30, isolation_level=None
                )
            
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA foreign_keys=ON")
            self._connection.execute("PRAGMA synchronous=NORMAL")
            self._connection.execute("PRAGMA cache_size=-2000")
            self._connection.execute("PRAGMA temp_store=MEMORY")
            self._connection.row_factory = sqlite3.Row
        
        return self._connection
    
    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def execute(self, query, params=None):
        conn = self.connect()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor
    
    def query(self, query, params=None):
        conn = self.connect()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    
    def query_one(self, query, params=None):
        conn = self.connect()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchone()
    
    def query_value(self, query, params=None):
        row = self.query_one(query, params)
        return row[0] if row else None
    
    @contextmanager
    def transaction(self):
        conn = self.connect()
        try:
            yield conn
            conn.execute("COMMIT")
        except Exception as e:
            conn.execute("ROLLBACK")
            raise e
    
    def begin_transaction(self):
        self.execute("BEGIN TRANSACTION")
    
    def commit(self):
        self.execute("COMMIT")
    
    def rollback(self):
        try:
            self.execute("ROLLBACK")
        except:
            pass
    
    def checkpoint(self):
        self.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    
    def vacuum(self):
        self.execute("VACUUM")
    
    def backup(self, backup_path=None):
        import shutil
        from datetime import datetime
        if backup_path is None:
            from core.paths import BACKUP_DIR
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = BACKUP_DIR / f"UNIYO_{timestamp}.db"
        self.checkpoint()
        shutil.copy2(str(DB_PATH), str(backup_path))
        return backup_path

db = Database()

def init_app(app):
    app.extensions['db'] = db
    return db

def get_db():
    return db

def execute_query(query, params=None):
    return db.execute(query, params)

def fetch_all(query, params=None):
    return db.query(query, params)

def fetch_one(query, params=None):
    return db.query_one(query, params)

def fetch_value(query, params=None):
    return db.query_value(query, params)
