import threading
import time
import schedule
import asyncio
import os

from datetime import datetime
from dotenv import load_dotenv

from telegram import Bot
from telegram.ext import (
    Application,
    CommandHandler
)

from database import (
    add_task,
    get_tasks,
    complete_task,
    add_note,
    get_notes
)

# =========================
# LOAD ENV
# =========================

load_dotenv()

TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

CHAT_ID = os.getenv(
    "CHAT_ID"
)

# =========================
# TELEGRAM SETUP
# =========================

bot = Bot(token=TOKEN)

app = Application.builder().token(TOKEN).build()

# =========================
# START COMMAND
# =========================

async def start(update, context):

    await update.message.reply_text(
        "🤖 AI Assistant Running"
    )

# =========================
# TODAY COMMAND
# =========================

async def today(update, context):

    tasks = get_tasks()

    if not tasks:

        await update.message.reply_text(
            "🎉 No Tasks"
        )

        return

    msg = "📅 Today's Tasks\n\n"

    for task in tasks:

        msg += (
            f"Date: {task[1]}\n"
            f"Task: {task[2]}\n"
            f"Time: {task[3]}\n"
            f"Status: {task[4]}\n\n"
            )

    await update.message.reply_text(msg)

# =========================
# ADD TASK
# =========================

async def add(update, context):

    try:

        text = update.message.text.replace(
            "/add ",
            ""
        )

        parts = text.split(",")

        task_date = parts[0].strip()

        task = parts[1].strip()

        task_time = parts[2].strip()

        add_task(
            task_date,
            task,
            task_time
        )

        await update.message.reply_text(

            f"✅ Task Added\n\n"

            f"📅 Date: {task_date}\n"

            f"📝 Task: {task}\n"

            f"⏰ Time: {task_time}"
        )

    except Exception as e:

        print(e)

        await update.message.reply_text(

            "❌ Wrong Format\n\n"

            "Use:\n"

            "/add 2026-05-20, Study, 18:00"
        )
# =========================
# COMPLETE TASK
# =========================

async def done(update, context):

    try:

        task_id = int(
            update.message.text.replace(
                "/done ",
                ""
            )
        )

        complete_task(task_id)

        await update.message.reply_text(
            f"✅ Task {task_id} Completed"
        )

    except Exception as e:

        print(e)

        await update.message.reply_text(
            "❌ Wrong Format\n\n"
            "Use:\n"
            "/done TASK_ID"
        )

# =========================
# SAVE NOTE
# =========================

async def note(update, context):

    text = update.message.text.replace(
        "/note ",
        ""
    )

    add_note(text)

    await update.message.reply_text(
        "📝 Note Saved"
    )

# =========================
# SHOW NOTES
# =========================

async def notes(update, context):

    all_notes = get_notes()

    if not all_notes:

        await update.message.reply_text(
            "No Notes"
        )

        return

    msg = "📝 Stored Notes\n\n"

    for item in all_notes:

        msg += (
            f"{item[0]}. "
            f"{item[1]}\n\n"
        )

    await update.message.reply_text(msg)
# =========================
# BULK ADD TASKS
# =========================

async def bulkadd(update, context):

    try:

        text = update.message.text.replace(
            "/bulkadd",
            ""
        ).strip()

        lines = text.split("\n")

        added_tasks = []

        for line in lines:

            parts = line.split(",")

            if len(parts) != 2:
                continue

            task = parts[0].strip()

            task_time = parts[1].strip()

            add_task(task, task_time)

            added_tasks.append(
                f"✅ {task} - {task_time}"
            )

        if added_tasks:

            msg = "📅 Multiple Tasks Added\n\n"

            msg += "\n".join(added_tasks)

            await update.message.reply_text(msg)

        else:

            await update.message.reply_text(
                "❌ No valid tasks found"
            )

    except Exception as e:

        print(e)

        await update.message.reply_text(
            "❌ Error adding tasks"
        )
        
# =========================
# HANDLERS
# =========================

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    CommandHandler("today", today)
)

app.add_handler(
    CommandHandler("add", add)
)

app.add_handler(
    CommandHandler("done", done)
)

app.add_handler(
    CommandHandler("note", note)
)

app.add_handler(
    CommandHandler("notes", notes)
)

app.add_handler(
    CommandHandler("bulkadd", bulkadd)
)
# =========================
# REMINDER ENGINE
# =========================

def check_tasks():

    today_date = datetime.now().strftime(
    "%Y-%m-%d"
    )

    tasks = get_tasks()

    for task in tasks:

        task_id = task[0]

        task_date = task[1]

        task_name = task[2]
        
        task_time = task[3]
        
        status = task[4]

        if (
            task_time == now and
            status != "Done"
        ):

            message = (
                f"⏰ Reminder\n\n"
                f"Task: {task_name}\n"
                f"ID: {task_id}\n\n"
                f"Complete using:\n"
                f"/done {task_id}"
            )

            try:

                asyncio.run(
                    bot.send_message(
                        chat_id=CHAT_ID,
                        text=message
                    )
                )

                print(
                    f"✅ Reminder Sent: {task_name}"
                )

            except Exception as e:

                print(
                    "Reminder Error:",
                    e
                )

# =========================
# SCHEDULER
# =========================

schedule.every(30).seconds.do(
    check_tasks
)

# =========================
# SCHEDULER THREAD
# =========================

def run_scheduler():

    while True:

        schedule.run_pending()

        time.sleep(5)

# =========================
# START THREAD
# =========================

scheduler_thread = threading.Thread(
    target=run_scheduler
)

scheduler_thread.daemon = True

scheduler_thread.start()

# =========================
# RUN BOT
# =========================

print("🚀 AI Assistant Running")

app.run_polling()
