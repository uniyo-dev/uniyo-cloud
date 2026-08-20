"""
UNIYO LMS - Database Connection (SQLite)
"""

import sqlite3
from contextlib import contextmanager
from core.paths import DB_PATH

class Database:
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        if self._connection is None:
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(str(DB_PATH), check_same_thread=False)
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
        pass
    
    def vacuum(self):
        pass
    
    def backup(self, backup_path=None):
        pass

db = Database()

def init_app(app):
    app.extensions['db'] = db
    return db

def get_db():
    return db
