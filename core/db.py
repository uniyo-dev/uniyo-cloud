"""
UNIYO LMS - Database Connection (Turso SQLite Cloud)
Uses Turso HTTP API - works with any Python version
"""

import requests
import json
from contextlib import contextmanager

# Turso connection
TURSO_URL = "libsql://uniyo-uniyo-dev.aws-us-east-2.turso.io"
TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODcyNjE4MjYsImlkIjoiMDFhMDIxMWEtNDkwMS03ZDY2LTk5ODEtZDc5NTcxMDYyNTVhIiwia2lkIjoiT29jQW5QU0Fjc0xicXV2MGI4ekdyaUtfT2ZyS0UxY2FEc3BaU3VkQVFFOCIsInJpZCI6IjU2ZDU3NzkzLTFhZmMtNGNiMC04NDJkLTY4MjRlNGQ0YThmNiJ9.BkDZq1Vhl_vuZ1hmenaJIbkwfu-5Nglr09vgFNPKIorOWU_iwFflaECdWE1RhJsHeom3sw7bwnsSKpllyExSBQ"

# Convert libsql:// to https:// for HTTP API
HTTP_URL = TURSO_URL.replace("libsql://", "https://")

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        # Turso doesn't need persistent connection - it's HTTP
        return self
    
    def close(self):
        pass
    
    def execute(self, query, params=None):
        """Execute SQL via Turso HTTP API"""
        headers = {
            "Authorization": f"Bearer {TURSO_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Convert ? placeholders to Turso format
        if params:
            # Turso uses named parameters
            sql = query
            args = []
            for p in params:
                if isinstance(p, str):
                    args.append({"type": "text", "value": p})
                elif isinstance(p, int):
                    args.append({"type": "integer", "value": str(p)})
                elif isinstance(p, float):
                    args.append({"type": "real", "value": str(p)})
                else:
                    args.append({"type": "text", "value": str(p)})
            
            body = {
                "statements": [{"q": sql, "params": args}]
            }
        else:
            body = {
                "statements": [{"q": query}]
            }
        
        try:
            response = requests.post(
                f"{HTTP_URL}/v2/pipeline",
                headers=headers,
                json=body,
                timeout=10
            )
            return TursoCursor(response.json())
        except Exception as e:
            print(f"Turso error: {e}")
            return TursoCursor({"results": {"cols": [], "rows": []}})
    
    def query(self, query, params=None):
        cursor = self.execute(query, params)
        return cursor.fetchall()
    
    def query_one(self, query, params=None):
        cursor = self.execute(query, params)
        return cursor.fetchone()
    
    def query_value(self, query, params=None):
        row = self.query_one(query, params)
        return row[0] if row else None
    
    @contextmanager
    def transaction(self):
        try:
            yield self
            self.execute("COMMIT")
        except Exception as e:
            self.execute("ROLLBACK")
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

class TursoCursor:
    def __init__(self, response):
        self.response = response
        self.rows = []
        self.cols = []
        
        try:
            results = response.get("results", {})
            self.cols = [col.get("name", "") for col in results.get("cols", [])]
            raw_rows = results.get("rows", [])
            for row in raw_rows:
                self.rows.append(dict(zip(self.cols, row)))
        except:
            pass
    
    def fetchall(self):
        return self.rows
    
    def fetchone(self):
        return self.rows[0] if self.rows else None
    
    def close(self):
        pass

db = Database()

def init_app(app):
    app.extensions['db'] = db
    return db

def get_db():
    return db
