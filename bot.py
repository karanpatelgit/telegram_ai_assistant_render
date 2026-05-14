import os
import asyncio

from datetime import datetime, time as dtime

import pytz
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters, CallbackQueryHandler
)

from database import (
    add_task, get_tasks, complete_task, delete_task,
    add_exam, get_exams, delete_exam,
    add_note, get_notes, search_notes, delete_note,
    add_revision, get_all_revisions,
    add_content, get_content,
    add_inbox, get_inbox, process_inbox_item,
    set_memory, get_all_memory,
    get_analytics_summary, log_analytics
)

from ai import (
    explain_simple, summarize_text,
    decision_helper, viral_ideas, generate_caption,
    study_plan, chat_with_history
)

from scheduler import (
    check_tasks, check_revisions, check_exam_countdown,
    morning_briefing, night_summary
)
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ist = pytz.timezone("Asia/Kolkata")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

conversation_history = {}

# ───────────────── ERROR HANDLER ─────────────────
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Error: {context.error}")

# ───────────────── START ─────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("📋 Tasks", callback_data="menu_tasks"),
        InlineKeyboardButton("🎓 Study", callback_data="menu_study"),
    ]]
    await update.message.reply_text(
        "🤖 AI Life OS Bot",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ───────────────── TASK ─────────────────
async def cmd_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.replace("/add", "").strip()
        date, task, time = [x.strip() for x in text.split(",")]
        add_task(date, task, time)
        log_analytics("task_added")
        await update.message.reply_text("✅ Task added!")
    except:
        await update.message.reply_text("Usage: /add YYYY-MM-DD, task, HH:MM")

async def cmd_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now(ist).strftime("%Y-%m-%d")
    tasks = get_tasks(date=today)

    if not tasks:
        await update.message.reply_text("No tasks today!")
        return

    msg = "📅 Tasks\n\n"
    for t in tasks:
        msg += f"[{t[0]}] {t[3]} - {t[2]}\n"

    await update.message.reply_text(msg)

# ───────────────── EXAMS ─────────────────
async def cmd_addexam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.replace("/addexam", "").strip()
        subject, exam_date, exam_time = text.split()
        add_exam(subject, exam_date, exam_time)
        await update.message.reply_text("🎓 Exam added!")
    except:
        await update.message.reply_text("Usage: /addexam subject YYYY-MM-DD HH:MM")

# ───────────────── NOTES ─────────────────
async def cmd_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/note", "").strip()
    add_note(text)
    await update.message.reply_text("📝 Note saved!")

# ───────────────── AI CHAT ─────────────────
async def cmd_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    question = update.message.text.replace("/ask", "").strip()

    if not question:
        await update.message.reply_text("Usage: /ask question")
        return

    conversation_history.setdefault(user_id, [])
    conversation_history[user_id].append({"role": "user", "content": question})

    thinking = await update.message.reply_text("🤔 Thinking...")

    try:
        loop = asyncio.get_event_loop()
        reply = await asyncio.wait_for(
            loop.run_in_executor(None, chat_with_history, conversation_history[user_id]),
            timeout=25
        )
    except:
        reply = "❌ Error"

    conversation_history[user_id].append({"role": "assistant", "content": reply})

    await thinking.edit_text(reply)

# ───────────────── QUICK CAPTURE ─────────────────
async def quick_capture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_inbox(update.message.text)
    await update.message.reply_text("📥 Saved to inbox!")

# ───────────────── MAIN ─────────────────
def main():
    app = (
    Application.builder()
    .token(TOKEN)
    .build()
        )
    app.add_error_handler(error_handler)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", cmd_add))
    app.add_handler(CommandHandler("today", cmd_today))
    app.add_handler(CommandHandler("addexam", cmd_addexam))
    app.add_handler(CommandHandler("note", cmd_note))
    app.add_handler(CommandHandler("ask", cmd_ask))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, quick_capture))

    jq = app.job_queue
    jq.run_repeating(check_tasks, interval=60, first=10)
    jq.run_daily(morning_briefing, time=dtime(7, 0, tzinfo=ist))

    print("🚀 Bot Running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
