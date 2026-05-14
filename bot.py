import os
import asyncio
import logging
from datetime import datetime, time as dtime

import pytz
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters,
)

from database import (
    add_task, get_tasks,
    add_exam,
    add_note,
    add_inbox,
    log_analytics,
)

from ai import chat_with_history

from scheduler import (
    check_tasks,
    morning_briefing,
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://your-app.onrender.com
PORT = int(os.getenv("PORT", "10000"))  # Render injects PORT for Web Services

ist = pytz.timezone("Asia/Kolkata")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

conversation_history: dict = {}


# ───────────────── ERROR HANDLER ─────────────────
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    log.error(f"Error: {context.error}")


# ───────────────── START ─────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("📋 Tasks", callback_data="menu_tasks"),
        InlineKeyboardButton("🎓 Study", callback_data="menu_study"),
    ]]
    await update.message.reply_text(
        "🤖 AI Life OS Bot",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ───────────────── TASK ─────────────────
async def cmd_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.replace("/add", "").strip()
        date, task, time = [x.strip() for x in text.split(",")]
        add_task(date, task, time)
        log_analytics("task_added")
        await update.message.reply_text("✅ Task added!")
    except Exception:
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
    except Exception:
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
            timeout=25,
        )
    except Exception:
        reply = "❌ Error"

    conversation_history[user_id].append({"role": "assistant", "content": reply})

    await thinking.edit_text(reply)


# ───────────────── QUICK CAPTURE ─────────────────
async def quick_capture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_inbox(update.message.text)
    await update.message.reply_text("📥 Saved to inbox!")


# ───────────────── MAIN ─────────────────
def build_app() -> Application:
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN env var is required")

    app = Application.builder().token(TOKEN).build()

    app.add_error_handler(error_handler)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", cmd_add))
    app.add_handler(CommandHandler("today", cmd_today))
    app.add_handler(CommandHandler("addexam", cmd_addexam))
    app.add_handler(CommandHandler("note", cmd_note))
    app.add_handler(CommandHandler("ask", cmd_ask))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, quick_capture))

    jq = app.job_queue
    if jq is not None:
        jq.run_repeating(check_tasks, interval=60, first=10)
        jq.run_daily(morning_briefing, time=dtime(7, 0, tzinfo=ist))
    else:
        log.warning("JobQueue not available — install python-telegram-bot[job-queue]")

    return app


def main():
    app = build_app()

    if WEBHOOK_URL:
        # Render Web Service path — bind to $PORT and let Telegram POST updates here.
        webhook_path = TOKEN  # secret path
        full_webhook_url = f"{WEBHOOK_URL.rstrip('/')}/{webhook_path}"
        log.info(f"🚀 Starting in WEBHOOK mode on 0.0.0.0:{PORT}")
        log.info(f"   Public webhook URL: {full_webhook_url}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=webhook_path,
            webhook_url=full_webhook_url,
            drop_pending_updates=True,
        )
    else:
        # Local dev / fallback — long-polling.
        log.info("🚀 Starting in POLLING mode (set WEBHOOK_URL for Render)")
        app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
