import sqlite3

# =========================
# DATABASE CONNECTION
# =========================

conn = sqlite3.connect(
    "assistant.db",
    check_same_thread=False
)

cursor = conn.cursor()

# =========================
# TASKS TABLE
# =========================

cursor.execute("""

CREATE TABLE IF NOT EXISTS tasks (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    task_date TEXT,

    task TEXT,

    task_time TEXT,

    status TEXT
)

""")

# =========================
# NOTES TABLE
# =========================

cursor.execute("""

CREATE TABLE IF NOT EXISTS notes (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    note TEXT
)

""")

# =========================
# AI MEMORY TABLE
# =========================

cursor.execute("""

CREATE TABLE IF NOT EXISTS ai_memory (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_message TEXT,

    ai_reply TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

""")

conn.commit()

# =========================
# ADD TASK
# =========================

def add_task(
    task_date,
    task,
    task_time
):

    cursor.execute(

        """
        INSERT INTO tasks
        (
            task_date,
            task,
            task_time,
            status
        )

        VALUES (?, ?, ?, ?)
        """,

        (
            task_date,
            task,
            task_time,
            "Pending"
        )
    )

    conn.commit()

# =========================
# GET TASKS
# =========================

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

        ORDER BY
            task_date ASC,
            task_time ASC
        """
    )

    return cursor.fetchall()

# =========================
# COMPLETE TASK
# =========================

def complete_task(task_id):

    cursor.execute(

        """
        UPDATE tasks

        SET status = ?

        WHERE id = ?
        """,

        (
            "Done",
            task_id
        )
    )

    conn.commit()

# =========================
# DELETE TASK
# =========================

def delete_task(task_id):

    cursor.execute(

        """
        DELETE FROM tasks

        WHERE id = ?
        """,

        (task_id,)
    )

    conn.commit()

# =========================
# ADD NOTE
# =========================

def add_note(note):

    cursor.execute(

        """
        INSERT INTO notes
        (note)

        VALUES (?)
        """,

        (note,)
    )

    conn.commit()

# =========================
# GET NOTES
# =========================

def get_notes():

    cursor.execute(

        """
        SELECT
            id,
            note

        FROM notes

        ORDER BY id DESC
        """
    )

    return cursor.fetchall()

# =========================
# DELETE NOTE
# =========================

def delete_note(note_id):

    cursor.execute(

        """
        DELETE FROM notes

        WHERE id = ?
        """,

        (note_id,)
    )

    conn.commit()

# =========================
# SAVE AI CHAT
# =========================

def save_ai_chat(
    user_message,
    ai_reply
):

    cursor.execute(

        """
        INSERT INTO ai_memory
        (
            user_message,
            ai_reply
        )

        VALUES (?, ?)
        """,

        (
            user_message,
            ai_reply
        )
    )

    conn.commit()

# =========================
# GET AI MEMORY
# =========================

def get_ai_memory():

    cursor.execute(

        """
        SELECT
            user_message,
            ai_reply,
            created_at

        FROM ai_memory

        ORDER BY id DESC

        LIMIT 20
        """
    )

    return cursor.fetchall()
