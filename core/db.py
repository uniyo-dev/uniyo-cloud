"""
UNIYO LMS - Database Connection (Supabase PostgreSQL)
"""

import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from core.paths import DB_PATH, IS_WINDOWS

# Supabase connection
SUPABASE_HOST = "db.kuopbrowpikkepytlchy.supabase.co"
SUPABASE_PORT = "5432"
SUPABASE_DB = "postgres"
SUPABASE_USER = "postgres"
SUPABASE_PASSWORD = "@Chalie/2026"

DATABASE_URL = f"postgresql://{SUPABASE_USER}:{SUPABASE_PASSWORD}@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DB}"

class Database:
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(DATABASE_URL)
            self._connection.autocommit = True
            psycopg2.extras.register_default_json(self._connection)
        return self._connection
    
    def close(self):
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None
    
    def execute(self, query, params=None):
        conn = self.connect()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor
    
    def query(self, query, params=None):
        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    
    def query_one(self, query, params=None):
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        cursor.close()
        return row
    
    def query_value(self, query, params=None):
        row = self.query_one(query, params)
        return row[0] if row else None
    
    @contextmanager
    def transaction(self):
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
    
    def begin_transaction(self):
        self.execute("BEGIN")
    
    def commit(self):
        self.execute("COMMIT")
    
    def rollback(self):
        try:
            self.execute("ROLLBACK")
        except:
            pass
    
    def checkpoint(self):
        pass  # PostgreSQL doesn't need WAL checkpoint
    
    def vacuum(self):
        pass  # PostgreSQL handles this automatically
    
    def backup(self, backup_path=None):
        pass  # Supabase handles backups automatically

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
