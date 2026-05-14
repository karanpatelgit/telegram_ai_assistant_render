import os
import requests
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from database import (
    add_task, get_tasks, complete_task,
    add_note, get_notes,
    delete_task, delete_note
)

# ---------------- ENV ----------------

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")

# ---------------- AI (HF FREE) ----------------

async def ai_reply(prompt: str):
    url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

    headers = {"Authorization": f"Bearer {HF_API_KEY}"}

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7
        }
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        data = r.json()

        if isinstance(data, list):
            return data[0]["generated_text"]

        return str(data)

    except Exception as e:
        return f"AI Error: {e}"

# ---------------- COMMANDS ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot Ready!")

# -------- TASKS --------

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.replace("/add ", "")
        date, task, time = [x.strip() for x in text.split(",")]

        add_task(date, task, time)

        await update.message.reply_text(f"✅ Added:\n{date} | {task} | {time}")

    except:
        await update.message.reply_text("Use:\n/add YYYY-MM-DD, Task, HH:MM")

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = get_tasks()

    if not tasks:
        await update.message.reply_text("No tasks")
        return

    msg = "📅 Tasks:\n\n"
    for t in tasks:
        msg += f"{t[0]} | {t[1]} | {t[2]} | {t[3]} | {t[4]}\n"

    await update.message.reply_text(msg)

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        task_id = int(update.message.text.replace("/done ", ""))
        complete_task(task_id)
        await update.message.reply_text("✅ Done")
    except:
        await update.message.reply_text("Use /done ID")

async def deltask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        task_id = int(update.message.text.replace("/deltask ", ""))
        delete_task(task_id)
        await update.message.reply_text("🗑 Deleted task")
    except:
        await update.message.reply_text("Use /deltask ID")

# -------- NOTES --------

async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/note ", "")
    add_note(text)
    await update.message.reply_text("📝 Saved")

async def notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_notes()

    if not data:
        await update.message.reply_text("No notes")
        return

    msg = "📝 Notes:\n\n"
    for n in data:
        msg += f"{n[0]}. {n[1]}\n"

    await update.message.reply_text(msg)

async def delnote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        note_id = int(update.message.text.replace("/delnote ", ""))
        delete_note(note_id)
        await update.message.reply_text("🗑 Deleted note")
    except:
        await update.message.reply_text("Use /delnote ID")

# -------- AI --------

async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/ai ", "")
    reply = await ai_reply(text)
    await update.message.reply_text(reply)

# ---------------- REMINDER (JOBQUEUE - CLEAN) ----------------

async def check_tasks(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().strftime("%H:%M")
    today = datetime.now().strftime("%Y-%m-%d")

    tasks = get_tasks()

    for t in tasks:
        task_id, date, task, time, status = t

        if date == today and time == now and status != "Done":
            await context.bot.send_message(
                chat_id=context.job.chat_id,
                text=f"⏰ Reminder\n{task}\nID: {task_id}"
            )

# ---------------- MAIN ----------------

def main():
    app = Application.builder().token(TOKEN).build()

    # commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("deltask", deltask))

    app.add_handler(CommandHandler("note", note))
    app.add_handler(CommandHandler("notes", notes))
    app.add_handler(CommandHandler("delnote", delnote))

    app.add_handler(CommandHandler("ai", ai))

    # JOB QUEUE (NO THREADING, NO SCHEDULER BUGS)
    job_queue = app.job_queue
    job_queue.run_repeating(check_tasks, interval=30, first=10)

    print("🚀 Bot Running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
