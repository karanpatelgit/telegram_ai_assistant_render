import sqlite3

conn = sqlite3.connect(
    "tasks.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT,
    time TEXT,
    status TEXT
)
""")

conn.commit()


def add_task(task, time):

    cursor.execute(
        "INSERT INTO tasks (task, time, status) VALUES (?, ?, ?)",
        (task, time, "Pending")
    )

    conn.commit()


def get_tasks():

    cursor.execute(
        "SELECT * FROM tasks"
    )

    return cursor.fetchall()


def complete_task(task_id):

    cursor.execute(
        "UPDATE tasks SET status='Done' WHERE id=?",
        (task_id,)
    )

    conn.commit()