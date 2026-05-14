import sqlite3
from datetime import datetime
import os
DB_PATH = os.getenv("DB_PATH", "/app/data/assistant.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# ── TABLES ──────────────────────────────────────────────────

cursor.executescript("""
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    task_date   TEXT,
    task        TEXT,
    task_time   TEXT,
    status      TEXT DEFAULT 'Pending',
    category    TEXT DEFAULT 'general',
    recurring   TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS exams (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    subject     TEXT,
    exam_date   TEXT,
    exam_time   TEXT,
    notes       TEXT
);

CREATE TABLE IF NOT EXISTS notes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    note        TEXT,
    tags        TEXT DEFAULT '',
    created_at  TEXT
);

CREATE TABLE IF NOT EXISTS revision (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    topic       TEXT,
    subject     TEXT,
    next_review TEXT,
    interval    INTEGER DEFAULT 3
);

CREATE TABLE IF NOT EXISTS content (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    type        TEXT,
    content     TEXT,
    platform    TEXT,
    scheduled   TEXT,
    status      TEXT DEFAULT 'idea'
);

CREATE TABLE IF NOT EXISTS inbox (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    text        TEXT,
    created_at  TEXT,
    processed   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS memory (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS analytics (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type  TEXT,
    event_data  TEXT,
    created_at  TEXT
);
""")
conn.commit()
#----------------Pharse natural language-----------------------
def parse_natural_task(text: str, today: str) -> dict:
    prompt = (
        f"Today's date is {today}.\n"
        f"Extract task details from this message: '{text}'\n\n"
        f"Reply with ONLY a JSON object, nothing else. No explanation.\n"
        f"Format:\n"
        f'{{"task": "task name", "date": "YYYY-MM-DD", "time": "HH:MM", "category": "study/general/health/work"}}\n\n'
        f"Rules:\n"
        f"- 'tomorrow' = next day from today\n"
        f"- 'morning' = 09:00, 'evening' = 18:00, 'night' = 21:00\n"
        f"- if no time mentioned, use 09:00\n"
        f"- if no date mentioned, use today\n"
        f"- category: use 'study' for exam/study/revision, 'health' for gym/workout, 'work' for meeting/project, else 'general'\n"
        f"- Return ONLY the JSON. No markdown, no explanation, no extra text."
    )
    
    try:
        r = requests.post(
            GROQ_URL,
            headers=HEADERS,
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100,
                "temperature": 0.1  # low temp for consistent JSON
            },
            timeout=15
        )

        if r.status_code != 200:
            return {}

        content = r.json()["choices"][0]["message"]["content"].strip()
        
        # clean any markdown if model adds it
        content = content.replace("```json", "").replace("```", "").strip()
        
        import json
        return json.loads(content)

    except Exception as e:
        return {}
# ── TASKS ────────────────────────────────────────────────────

def add_task(task_date, task, task_time, category="general", recurring=None):
    cursor.execute(
        "INSERT INTO tasks (task_date, task, task_time, category, recurring) VALUES (?,?,?,?,?)",
        (task_date, task, task_time, category, recurring)
    )
    conn.commit()

def get_tasks(date=None):
    if date:
        cursor.execute(
            "SELECT id,task_date,task,task_time,status,category FROM tasks WHERE task_date=? ORDER BY task_time",
            (date,)
        )
    else:
        cursor.execute(
            "SELECT id,task_date,task,task_time,status,category FROM tasks ORDER BY task_date,task_time"
        )
    return cursor.fetchall()

def complete_task(task_id):
    cursor.execute("UPDATE tasks SET status='Done' WHERE id=?", (task_id,))
    conn.commit()
    log_analytics("task_done", str(task_id))

def delete_task(task_id):
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()

def get_recurring_tasks():
    cursor.execute("SELECT * FROM tasks WHERE recurring IS NOT NULL")
    return cursor.fetchall()

# ── EXAMS ────────────────────────────────────────────────────

def add_exam(subject, exam_date, exam_time, notes=""):
    cursor.execute(
        "INSERT INTO exams (subject,exam_date,exam_time,notes) VALUES (?,?,?,?)",
        (subject, exam_date, exam_time, notes)
    )
    conn.commit()

def get_exams():
    cursor.execute("SELECT * FROM exams ORDER BY exam_date")
    return cursor.fetchall()

def delete_exam(exam_id):
    cursor.execute("DELETE FROM exams WHERE id=?", (exam_id,))
    conn.commit()

# ── NOTES ────────────────────────────────────────────────────

def add_note(note, tags=""):
    cursor.execute(
        "INSERT INTO notes (note, tags, created_at) VALUES (?,?,?)",
        (note, tags, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()

def get_notes():
    cursor.execute("SELECT id,note,tags,created_at FROM notes ORDER BY id DESC")
    return cursor.fetchall()

def search_notes(query):
    cursor.execute(
        "SELECT id,note,tags,created_at FROM notes WHERE note LIKE ? OR tags LIKE ?",
        (f"%{query}%", f"%{query}%")
    )
    return cursor.fetchall()

def delete_note(note_id):
    cursor.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()

# ── REVISION ─────────────────────────────────────────────────

def add_revision(topic, subject, days=3):
    from datetime import timedelta
    next_review = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    cursor.execute(
        "INSERT INTO revision (topic,subject,next_review,interval) VALUES (?,?,?,?)",
        (topic, subject, next_review, days)
    )
    conn.commit()

def get_due_revisions(date):
    cursor.execute(
        "SELECT * FROM revision WHERE next_review <= ?", (date,)
    )
    return cursor.fetchall()

def reschedule_revision(rev_id, next_interval):
    from datetime import timedelta
    next_date = (datetime.now() + timedelta(days=next_interval)).strftime("%Y-%m-%d")
    cursor.execute(
        "UPDATE revision SET next_review=?, interval=? WHERE id=?",
        (next_date, next_interval, rev_id)
    )
    conn.commit()

def get_all_revisions():
    cursor.execute("SELECT * FROM revision ORDER BY next_review")
    return cursor.fetchall()

# ── CONTENT ──────────────────────────────────────────────────

def add_content(content_type, content, platform="", scheduled=""):
    cursor.execute(
        "INSERT INTO content (type,content,platform,scheduled) VALUES (?,?,?,?)",
        (content_type, content, platform, scheduled)
    )
    conn.commit()

def get_content(status=None):
    if status:
        cursor.execute("SELECT * FROM content WHERE status=? ORDER BY id DESC", (status,))
    else:
        cursor.execute("SELECT * FROM content ORDER BY id DESC")
    return cursor.fetchall()

def update_content_status(content_id, status):
    cursor.execute("UPDATE content SET status=? WHERE id=?", (status, content_id))
    conn.commit()

# ── INBOX ────────────────────────────────────────────────────

def add_inbox(text):
    cursor.execute(
        "INSERT INTO inbox (text,created_at) VALUES (?,?)",
        (text, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()

def get_inbox(processed=0):
    cursor.execute(
        "SELECT * FROM inbox WHERE processed=? ORDER BY id DESC", (processed,)
    )
    return cursor.fetchall()

def process_inbox_item(inbox_id):
    cursor.execute("UPDATE inbox SET processed=1 WHERE id=?", (inbox_id,))
    conn.commit()

# ── MEMORY ───────────────────────────────────────────────────

def set_memory(key, value):
    cursor.execute(
        "INSERT OR REPLACE INTO memory (key,value) VALUES (?,?)", (key, value)
    )
    conn.commit()

def get_memory(key):
    cursor.execute("SELECT value FROM memory WHERE key=?", (key,))
    r = cursor.fetchone()
    return r[0] if r else None

def get_all_memory():
    cursor.execute("SELECT key,value FROM memory")
    return cursor.fetchall()

# ── ANALYTICS ────────────────────────────────────────────────

def log_analytics(event_type, event_data=""):
    cursor.execute(
        "INSERT INTO analytics (event_type,event_data,created_at) VALUES (?,?,?)",
        (event_type, event_data, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()

def get_analytics_summary():
    cursor.execute("""
        SELECT event_type, COUNT(*) as count
        FROM analytics
        GROUP BY event_type
        ORDER BY count DESC
    """)
    return cursor.fetchall()
