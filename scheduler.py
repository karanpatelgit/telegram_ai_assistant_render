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

            # FORMAT:
            # 2026-05-20, Study, 18:00

            if len(parts) != 3:
                continue

            task_date = parts[0].strip()

            task = parts[1].strip()

            task_time = parts[2].strip()

            add_task(
                task_date,
                task,
                task_time
            )

            added_tasks.append(
                f"✅ {task_date} | {task} | {task_time}"
            )

        if added_tasks:

            msg = (
                "📅 Multiple Tasks Added\n\n"
                + "\n".join(added_tasks)
            )

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
# REMINDER ENGINE
# =========================

async def check_tasks():

    now = datetime.now().strftime(
        "%H:%M"
    )

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

            task_date == today_date

            and

            task_time == now

            and

            status != "Done"
        ):

            message = (

                f"⏰ Reminder\n\n"

                f"📅 Date: {task_date}\n"

                f"📝 Task: {task_name}\n"

                f"🆔 ID: {task_id}\n\n"

                f"Complete using:\n"

                f"/done {task_id}"
            )

            try:

                await bot.send_message(
                    chat_id=CHAT_ID,
                    text=message
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
# SCHEDULER LOOP
# =========================

async def scheduler_loop():

    while True:

        await check_tasks()

        await asyncio.sleep(30)


# =========================
# MAIN
# =========================

async def main():

    print("🚀 AI Assistant Running")

    asyncio.create_task(
        scheduler_loop()
    )

    await app.initialize()

    await app.start()

    await app.run_polling(
        drop_pending_updates=True
    )


# =========================
# START BOT
# =========================

if __name__ == "__main__":

    asyncio.run(main())
