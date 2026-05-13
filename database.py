import sqlite3

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

```
id INTEGER PRIMARY KEY AUTOINCREMENT,

task TEXT,

task_time TEXT,

status TEXT
```

)

""")

# =========================

# NOTES TABLE

# =========================

cursor.execute("""

CREATE TABLE IF NOT EXISTS notes (

```
id INTEGER PRIMARY KEY AUTOINCREMENT,

note TEXT
```

)

""")

conn.commit()

# =========================

# TASK FUNCTIONS

# =========================

def add_task(task, task_time):

```
cursor.execute(

    "INSERT INTO tasks (task, task_time, status) VALUES (?, ?, ?)",

    (task, task_time, "Pending")
)

conn.commit()
```

def get_tasks():

```
cursor.execute(

    "SELECT * FROM tasks"
)

return cursor.fetchall()
```

def complete_task(task_id):

```
cursor.execute(

    "UPDATE tasks SET status='Done' WHERE id=?",

    (task_id,)
)

conn.commit()
```

# =========================

# NOTES FUNCTIONS

# =========================

def add_note(note):

```
cursor.execute(

    "INSERT INTO notes (note) VALUES (?)",

    (note,)
)

conn.commit()
```

def get_notes():

```
cursor.execute(

    "SELECT * FROM notes"
)

return cursor.fetchall()
```
