"""
UNIYO LMS - Database Connection (Turso)
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()
import json
from contextlib import contextmanager

TURSO_URL = os.environ.get("TURSO_URL", "https://uniyo-uniyo-dev.aws-us-east-2.turso.io")
TURSO_TOKEN = os.environ.get("TURSO_TOKEN", "")

class TursoRow(dict):
    def __getitem__(self, key):
        if isinstance(key, int):
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
        headers = {
            "Authorization": f"Bearer {TURSO_TOKEN}",
            "Content-Type": "application/json"
        }
        
        if params:
            sql = query
            args = []
            for i, p in enumerate(params):
                param_name = f"p{i+1}"
                sql = sql.replace('?', f':{param_name}', 1)
                
                if isinstance(p, int):
                    args.append({"name": param_name, "type": "integer", "value": str(p)})
                elif isinstance(p, float):
                    args.append({"name": param_name, "type": "real", "value": str(p)})
                elif p is None:
                    args.append({"name": param_name, "type": "text", "value": ""})
                else:
                    args.append({"name": param_name, "type": "text", "value": str(p)})
            
            stmt = {"sql": sql}
            if args:
                stmt["args"] = args
        else:
            stmt = {"sql": query}
        
        body = {
            "requests": [
                {"type": "execute", "stmt": stmt},
                {"type": "close"}
            ]
        }
        
        try:
            response = requests.post(f"{TURSO_URL}/v2/pipeline", headers=headers, json=body, timeout=20)
            return response.json()
        except Exception as e:
            print(f"Turso error: {e}")
            return {"results": []}
    
    def execute(self, query, params=None):
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
                if result.get("type") == "ok":
                    resp = result.get("response", {})
                    exec_result = resp.get("result", {})
                    self.cols = [col["name"] for col in exec_result.get("cols", [])]
                    
                    for row_data in exec_result.get("rows", []):
                        row_dict = {}
                        for i, col_name in enumerate(self.cols):
                            if i < len(row_data):
                                cell = row_data[i]
                                value = cell.get("value") if isinstance(cell, dict) else cell
                                if isinstance(cell, dict) and cell.get("type") == "integer":
                                    value = int(value) if value else 0
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
