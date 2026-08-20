"""
UNIYO LMS - Database Connection (Turso SQLite Cloud)
"""

import requests
import json
from contextlib import contextmanager

TURSO_URL = "https://uniyo-uniyo-dev.aws-us-east-2.turso.io"
TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODcyNjE4MjYsImlkIjoiMDFhMDIxMWEtNDkwMS03ZDY2LTk5ODEtZDc5NTcxMDYyNTVhIiwia2lkIjoiT29jQW5QU0Fjc0xicXV2MGI4ekdyaUtfT2ZyS0UxY2FEc3BaU3VkQVFFOCIsInJpZCI6IjU2ZDU3NzkzLTFhZmMtNGNiMC04NDJkLTY4MjRlNGQ0YThmNiJ9.BkDZq1Vhl_vuZ1hmenaJIbkwfu-5Nglr09vgFNPKIorOWU_iwFflaECdWE1RhJsHeom3sw7bwnsSKpllyExSBQ"

class TursoRow(dict):
    """Row that supports both dict and index access"""
    def __getitem__(self, key):
        if isinstance(key, int):
            # Index access - return value by position
            return list(self.values())[key]
        return super().__getitem__(key)

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        return self
    
    def close(self):
        pass
    
    def _execute_raw(self, query, params=None):
        """Execute SQL and return raw Turso response"""
        headers = {
            "Authorization": f"Bearer {TURSO_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Build statement with params
        if params:
            turso_params = []
            for p in params:
                if isinstance(p, int):
                    turso_params.append({"type": "integer", "value": str(p)})
                elif isinstance(p, float):
                    turso_params.append({"type": "real", "value": str(p)})
                elif p is None:
                    turso_params.append({"type": "null", "value": "null"})
                else:
                    turso_params.append({"type": "text", "value": str(p)})
            
            # Replace ? with ?1, ?2, etc for Turso
            import re
            sql = query
            for i in range(len(params)):
                sql = sql.replace('?', f'?{i+1}', 1)
            
            stmt = {"sql": sql, "args": turso_params}
        else:
            stmt = {"sql": query}
        
        body = {
            "requests": [
                {"type": "execute", "stmt": stmt},
                {"type": "close"}
            ]
        }
        
        try:
            response = requests.post(f"{TURSO_URL}/v2/pipeline", headers=headers, json=body, timeout=15)
            return response.json()
        except Exception as e:
            print(f"Turso error: {e}")
            return {"results": []}
    
    def execute(self, query, params=None):
        """Execute and return cursor-like object"""
        result = self._execute_raw(query, params)
        return TursoCursor(result)
    
    def query(self, query, params=None):
        cursor = self.execute(query, params)
        return cursor.fetchall()
    
    def query_one(self, query, params=None):
        cursor = self.execute(query, params)
        return cursor.fetchone()
    
    def query_value(self, query, params=None):
        row = self.query_one(query, params)
        if row:
            return list(row.values())[0] if isinstance(row, dict) else row[0]
        return None
    
    @contextmanager
    def transaction(self):
        try:
            yield self
        except Exception as e:
            raise e
    
    def begin_transaction(self):
        pass
    
    def commit(self):
        pass
    
    def rollback(self):
        pass
    
    def checkpoint(self):
        pass
    
    def vacuum(self):
        pass
    
    def backup(self, backup_path=None):
        pass

class TursoCursor:
    def __init__(self, response):
        self.rows = []
        self.cols = []
        
        try:
            for result in response.get("results", []):
                if result.get("type") == "ok" and result.get("response", {}).get("type") == "execute":
                    exec_result = result["response"]["result"]
                    self.cols = [col["name"] for col in exec_result.get("cols", [])]
                    
                    for row_data in exec_result.get("rows", []):
                        row_dict = {}
                        for i, col_name in enumerate(self.cols):
                            cell = row_data[i]
                            value = cell.get("value") if isinstance(cell, dict) else cell
                            # Convert to proper type
                            if cell.get("type") == "integer":
                                value = int(value)
                            elif cell.get("type") == "real":
                                value = float(value)
                            row_dict[col_name] = value
                        
                        self.rows.append(TursoRow(row_dict))
        except Exception as e:
            print(f"Parse error: {e}")
    
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
