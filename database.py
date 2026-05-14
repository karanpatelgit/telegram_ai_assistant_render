import sqlite3

conn = sqlite3.connect("assistant.db", check_same_thread=False)
cursor = conn.cursor()

# TASKS
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_date TEXT,
    task TEXT,
    task_time TEXT,
    status TEXT
)
""")

# NOTES
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note TEXT
)
""")

conn.commit()

# ---------------- TASKS ----------------

def add_task(task_date, task, task_time):
    cursor.execute(
        "INSERT INTO tasks (task_date, task, task_time, status) VALUES (?, ?, ?, ?)",
        (task_date, task, task_time, "Pending")
    )
    conn.commit()

def get_tasks():
    cursor.execute(
        """
        SELECT
            id,
            task_date,
            task,
            task_time,
            status
        FROM tasks
        ORDER BY task_date, task_time
        """
    )

    return cursor.fetchall()

def complete_task(task_id):
    cursor.execute("UPDATE tasks SET status='Done' WHERE id=?", (task_id,))
    conn.commit()

def delete_task(task_id):
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()

# ---------------- NOTES ----------------

def add_note(note):
    cursor.execute("INSERT INTO notes (note) VALUES (?)", (note,))
    conn.commit()

def get_notes():
    cursor.execute("SELECT * FROM notes ORDER BY id DESC")
    return cursor.fetchall()

def delete_note(note_id):
    cursor.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()turn cursor.fetchall()
