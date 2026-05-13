import threading
import time
import schedule
from datetime import datetime

from telegram import Bot
from telegram.ext import (
    Updater,
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

updater = Updater(
    TOKEN,
    use_context=True
)

dispatcher = updater.dispatcher


# =========================
# TELEGRAM COMMANDS
# =========================

def start(update, context):

    update.message.reply_text(
        "🤖 AI Assistant Running"
    )


def today(update, context):

    tasks = get_tasks()

    if not tasks:

        update.message.reply_text(
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

    update.message.reply_text(msg)


def add(update, context):

    try:

        text = update.message.text.replace(
            "/add ",
            ""
        )

        parts = text.split(",")

        task = parts[0].strip()

        time_value = parts[1].strip()

        add_task(task, time_value)

        update.message.reply_text(
            "✅ Task Added"
        )

    except:

        update.message.reply_text(
            "❌ Use:\n/add Task, HH:MM"
        )


def done(update, context):

    try:

        task_id = int(
            update.message.text.replace(
                "/done ",
                ""
            )
        )

        complete_task(task_id)

        update.message.reply_text(
            "✅ Task Completed"
        )

    except:

        update.message.reply_text(
            "❌ Use:\n/done TASK_ID"
        )


dispatcher.add_handler(
    CommandHandler("start", start)
)

dispatcher.add_handler(
    CommandHandler("today", today)
)

dispatcher.add_handler(
    CommandHandler("add", add)
)

dispatcher.add_handler(
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

def run_scheduler():

    while True:

        schedule.run_pending()

        time.sleep(5)


scheduler_thread = threading.Thread(
    target=run_scheduler
)

scheduler_thread.start()

print("🚀 AI Assistant Running")

updater.start_polling()

updater.idle()