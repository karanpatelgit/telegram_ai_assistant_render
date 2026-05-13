import threading
import time
import schedule
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

load_dotenv()

TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

CHAT_ID = os.getenv(
    "CHAT_ID"
)

bot = Bot(token=TOKEN)

app = Application.builder().token(TOKEN).build()


# =========================
# TELEGRAM COMMANDS
# =========================

async  def start( update, context):

    await update.message.reply_text(
        "🤖 AI Assistant Running"
    )


async  def today(update, context):

    tasks = get_tasks()

    if not tasks:

        await update.message.reply_text(
            "🎉 No Tasks"
        )

        return

    msg = "📅 Tasks\n\n"

    for task in tasks:

        msg += (
            f"ID: {task[0]}\n"
            f"Task: {task[1]}\n"
            f"Time: {task[2]}\n"
            f"Status: {task[3]}\n\n"
        )

    await update.message.reply_text(msg)


async  def add(update, context):

    try:

        text = await update.message.text.replace(
            "/add ",
            ""
        )

        parts = text.split(",")

        task = parts[0].strip()

        time_value = parts[1].strip()

        add_task(task, time_value)

        await update.message.reply_text(
            "✅ Task Added"
        )

    except:

        await update.message.reply_text(
            "❌ Use:\n/add Task, HH:MM"
        )


async def done(update, context):

    try:

        task_id = int(
            await update.message.text.replace(
                "/done ",
                ""
            )
        )

        complete_task(task_id)

        await update.message.reply_text(
            "✅ Task Completed"
        )

    except:

        await update.message.reply_text(
            "❌ Use:\n/done TASK_ID"
        )


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

async def check_tasks():

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
                f"After completion:\n"
                f"/done {task_id}"
            )

            bot.send_message(
                chat_id=CHAT_ID,
                text=message
            )

            print(
                f"Reminder sent for {task_name}"
            )


schedule.every(30).seconds.do(
    check_tasks
)

# =========================
# THREADS
# =========================

async def run_scheduler():

    while True:

        schedule.run_pending()

        time.sleep(5)


scheduler_thread = threading.Thread(
    target=run_scheduler
)

scheduler_thread.start()

print("🚀 AI Assistant Running")

app.run_polling()
