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

updater = Updater(
    TOKEN,
    use_context=True
)

dispatcher = updater.dispatcher


def start(update, context):

    update.message.reply_text(
        "🤖 AI Assistant Started"
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

        time = parts[1].strip()

        add_task(task, time)

        update.message.reply_text(
            "✅ Task Added"
        )

    except:

        update.message.reply_text(
            "❌ Format:\n/add Task, HH:MM"
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

print("🤖 Bot Running...")

updater.start_polling()

updater.idle()