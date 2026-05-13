import threading
import time
import schedule
import asyncio

from datetime import datetime

from telegram import Bot
from telegram.ext import (
    Application,
    CommandHandler
)

from dotenv import load_dotenv
import os

from database import (
    add_task,
    get_tasks,
    complete_task
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
            f"ID: {task[0]}\n"
            f"Task: {task[1]}\n"
            f"Time: {task[2]}\n"
            f"Status: {task[3]}\n\n"
        )

    await update.message.reply_text(msg)

# =========================
# ADD TASK COMMAND
# =========================

async def add(update, context):

    try:

        text = update.message.text.replace(
            "/add ",
            ""
        )

        parts = text.split(",")

        task = parts[0].strip()

        time_value = parts[1].strip()

        add_task(task, time_value)

        await update.message.reply_text(
            f"✅ Task Added\n\n"
            f"Task: {task}\n"
            f"Time: {time_value}"
        )

    except Exception as e:

        print(e)

        await update.message.reply_text(
            "❌ Wrong Format\n\n"
            "Use:\n"
            "/add Task Name, HH:MM"
        )

# =========================
# COMPLETE TASK COMMAND
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

# =========================
# REMINDER ENGINE
# =========================

def check_tasks():

    now = datetime.now().strftime(
        "%H:%M"
    )

    tasks = get_tasks()

    for task in tasks:

        task_id = task[0]

        task_name = task[1]

        task_time = task[2]

        status = task[3]

        if (
            task_time == now and
            status != "Done"
        ):

            message = (
                f"⏰ Reminder\n\n"
                f"Task: {task_name}\n"
                f"ID: {task_id}\n\n"
                f"After completion send:\n"
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
