import os
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.error import Conflict
from telegram.ext import Application, CommandHandler, ContextTypes
from database import get_tasks
import pytz

ist = pytz.timezone("Asia/Kolkata")

# =========================
# LOAD ENV
# =========================
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
print("🚀 BOT FILE LOADED")

# =========================
# LOGGING
# =========================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =========================
# ERROR HANDLER
# =========================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    if isinstance(context.error, Conflict):
        logging.warning("⚠️ Conflict error caught — another instance may still be shutting down. Retrying...")
        await asyncio.sleep(5)  # wait and let the old instance die
    else:
        logging.error(f"Unhandled error: {context.error}")

# =========================
# REMINDER FUNCTION
# =========================
async def check_tasks(context: ContextTypes.DEFAULT_TYPE):
    now_time = datetime.now(ist).strftime("%H:%M")
    today_date = datetime.now(ist).strftime("%Y-%m-%d")
    tasks = get_tasks()

    for task in tasks:
        task_id = task[0]
        task_date = task[1]
        task_name = task[2]
        task_time = task[3]
        status = task[4]

        if (
            task_date == today_date and
            task_time == now_time and
            status != "Done"
        ):
            message = (
                "⏰ Reminder\n\n"
                f"📅 Date: {task_date}\n"
                f"📝 Task: {task_name}\n"
                f"🆔 ID: {task_id}\n\n"
                f"/done {task_id}"
            )
            try:
                await context.bot.send_message(chat_id=CHAT_ID, text=message)
                print(f"✅ Reminder sent: {task_name}")
            except Exception as e:
                print("Reminder error:", e)

# =========================
# START COMMAND
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot is running")

# =========================
# POST INIT — runs after app builds, before polling
# =========================
async def post_init(application: Application):
    # Force-clear any lingering sessions on Telegram's side
    await application.bot.delete_webhook(drop_pending_updates=True)
    logging.info("✅ Webhook deleted and pending updates dropped")
    await asyncio.sleep(3)  # give Telegram time to release the old session

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print("🚀 BOT STARTED")

    app = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)   # ✅ runs cleanup before polling starts
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_error_handler(error_handler)  # ✅ handles Conflict gracefully

    app.job_queue.run_repeating(
        check_tasks,
        interval=30,
        first=10,
    )

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
    )
