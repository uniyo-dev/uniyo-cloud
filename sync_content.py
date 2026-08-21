"""
Auto-sync content from files to Turso on every server start
"""

import requests
import json
from pathlib import Path

TURSO_URL = "https://uniyo-uniyo-dev.aws-us-east-2.turso.io"
TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODcyNjE4MjYsImlkIjoiMDFhMDIxMWEtNDkwMS03ZDY2LTk5ODEtZDc5NTcxMDYyNTVhIiwia2lkIjoiT29jQW5QU0Fjc0xicXV2MGI4ekdyaUtfT2ZyS0UxY2FEc3BaU3VkQVFFOCIsInJpZCI6IjU2ZDU3NzkzLTFhZmMtNGNiMC04NDJkLTY4MjRlNGQ0YThmNiJ9.BkDZq1Vhl_vuZ1hmenaJIbkwfu-5Nglr09vgFNPKIorOWU_iwFflaECdWE1RhJsHeom3sw7bwnsSKpllyExSBQ"

headers = {
    "Authorization": f"Bearer {TURSO_TOKEN}",
    "Content-Type": "application/json"
}

def execute_sql(sql):
    body = {
        "requests": [
            {"type": "execute", "stmt": {"sql": sql}},
            {"type": "close"}
        ]
    }
    try:
        requests.post(f"{TURSO_URL}/v2/pipeline", headers=headers, json=body, timeout=20)
    except:
        pass

def sync_all_content():
    """Sync all content from files to Turso"""
    BASE_DIR = Path(__file__).resolve().parent
    
    # Sync lessons
    lessons_dir = BASE_DIR / 'content' / 'courses'
    statements = []
    lesson_count = 0
    
    for course_dir in lessons_dir.iterdir():
        if not course_dir.is_dir():
            continue
        course_code = course_dir.name
        
        for chapter_dir in course_dir.iterdir():
            if not chapter_dir.is_dir() or 'chapter' not in chapter_dir.name:
                continue
            chapter_num = chapter_dir.name.replace('chapter', '')
            
            for part_file in chapter_dir.glob('*.html'):
                part_name = part_file.stem.replace('part', '')
                file_path = f"{course_code}/{chapter_dir.name}/{part_file.name}"
                sql = f"INSERT OR REPLACE INTO lessons (course_code, chapter_number, part_number, chapter_title, part_title, file_path, is_premium, is_active, created_at) VALUES ('{course_code}', {chapter_num}, {part_name}, 'Chapter {chapter_num}', 'Part {part_name}', '{file_path}', 1, 1, 'now')"
                statements.append({"type": "execute", "stmt": {"sql": sql}})
                lesson_count += 1
    
    # Sync worksheets
    worksheets_dir = BASE_DIR / 'content' / 'worksheets'
    ws_count = 0
    
    for course_dir in worksheets_dir.iterdir():
        if not course_dir.is_dir():
            continue
        course_code = course_dir.name
        
        for chapter_dir in course_dir.iterdir():
            if not chapter_dir.is_dir() or 'chapter' not in chapter_dir.name:
                continue
            chapter_num = chapter_dir.name.replace('chapter', '')
            
            for ws_file in chapter_dir.glob('*.json'):
                file_path = f"{course_code}/{chapter_dir.name}/{ws_file.name}"
                title = ws_file.stem
                sql = f"INSERT OR REPLACE INTO worksheets (course_code, chapter_number, title, question_file, is_active, created_at) VALUES ('{course_code}', {chapter_num}, '{title}', '{file_path}', 1, 'now')"
                statements.append({"type": "execute", "stmt": {"sql": sql}})
                ws_count += 1
    
    # Sync past exams
    past_exams_dir = BASE_DIR / 'content' / 'past_exams'
    pe_count = 0
    
    for exam_file in past_exams_dir.glob('*.html'):
        name = exam_file.stem
        parts = name.split('_')
        if len(parts) >= 4:
            sql = f"INSERT OR REPLACE INTO past_exams (university, course_code, course_title, year, exam_type, file_path, is_active, created_at) VALUES ('{parts[0]}', '{parts[1]}', '{parts[1]}', {parts[2]}, '{parts[3]}', '{exam_file.name}', 1, 'now')"
            statements.append({"type": "execute", "stmt": {"sql": sql}})
            pe_count += 1
    
    # Execute all in batches
    statements.append({"type": "close"})
    batch_size = 50
    for i in range(0, len(statements)-1, batch_size):
        batch = statements[i:i+batch_size]
        batch.append({"type": "close"})
        body = {"requests": batch}
        requests.post(f"{TURSO_URL}/v2/pipeline", headers=headers, json=body, timeout=120)
    
    # Clear old sessions
    execute_sql("UPDATE active_sessions SET is_active = 0")
    
    print(f"✓ {lesson_count} lessons, {ws_count} worksheets, {pe_count} past exams synced")
    return True

if __name__ == '__main__':
    sync_all_content()
