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
    get_notes,
    delete_task,
    delete_note
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

    msg = (

        "🤖 AI Assistant Running\n\n"

        "Commands:\n"

        "/add DATE, TASK, TIME\n"
        "/bulkadd\n"
        "/today\n"
        "/done ID\n"
        "/deltask ID\n"
        "/note TEXT\n"
        "/notes\n"
        "/delnote ID"
    )

    await update.message.reply_text(msg)

# =========================
# TODAY TASKS
# =========================

async def today(update, context):

    tasks = get_tasks()

    if not tasks:

        await update.message.reply_text(
            "🎉 No Tasks"
        )

        return

    msg = "📅 Tasks\n\n"

    for task in tasks:

        msg += (

            f"🆔 {task[0]}\n"
            f"📅 {task[1]}\n"
            f"📝 {task[2]}\n"
            f"⏰ {task[3]}\n"
            f"📌 {task[4]}\n\n"
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

            f"📅 {task_date}\n"
            f"📝 {task}\n"
            f"⏰ {task_time}"
        )

    except Exception as e:

        print(e)

        await update.message.reply_text(

            "❌ Format:\n"
            "/add 2026-05-20, Study, 18:00"
        )

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
                "❌ No valid tasks"
            )

    except Exception as e:

        print(e)

        await update.message.reply_text(
            "❌ Bulk add failed"
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
            "❌ Use:\n/done TASK_ID"
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
            "❌ No Notes"
        )

        return

    msg = "📝 Notes\n\n"

    for item in all_notes:

        msg += (
            f"{item[0]}. {item[1]}\n\n"
        )

    await update.message.reply_text(msg)

# =========================
# DELETE TASK
# =========================

async def deltask(update, context):

    try:

        task_id = int(

            update.message.text.replace(
                "/deltask ",
                ""
            )
        )

        delete_task(task_id)

        await update.message.reply_text(
            f"🗑 Task {task_id} Deleted"
        )

    except Exception as e:

        print(e)

        await update.message.reply_text(
            "❌ Use:\n/deltask TASK_ID"
        )

# =========================
# DELETE NOTE
# =========================

async def delnote(update, context):

    try:

        note_id = int(

            update.message.text.replace(
                "/delnote ",
                ""
            )
        )

        delete_note(note_id)

        await update.message.reply_text(
            f"🗑 Note {note_id} Deleted"
        )

    except Exception as e:

        print(e)

        await update.message.reply_text(
            "❌ Use:\n/delnote NOTE_ID"
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

                f"📅 {task_date}\n"
                f"📝 {task_name}\n"
                f"🆔 {task_id}\n\n"

                f"/done {task_id}"
            )

            try:

                await bot.send_message(
                    chat_id=CHAT_ID,
                    text=message
                )

                print(
                    f"Reminder Sent: {task_name}"
                )

            except Exception as e:

                print(e)

# =========================
# SCHEDULER LOOP
# =========================

async def scheduler_loop():

    while True:

        await check_tasks()

        await asyncio.sleep(30)

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
    CommandHandler("bulkadd", bulkadd)
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
    CommandHandler("deltask", deltask)
)

app.add_handler(
    CommandHandler("delnote", delnote)
)

# =========================
# MAIN
# =========================

async def main():

    print("🚀 AI Assistant Running")

    asyncio.create_task(
        scheduler_loop()
    )

    await app.run_polling(
        drop_pending_updates=True
    )

# =========================
# START BOT
# =========================

if __name__ == "__main__":

    asyncio.run(main())
