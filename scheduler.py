import os
import logging
from datetime import datetime
from dotenv import load_dotenv
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
# CREATE APP
# =========================
app = Application.builder().token(TOKEN).build()

# =========================
# START COMMAND
# =========================
async def start(update, context):
    await update.message.reply_text("🤖 Bot is running")

app.add_handler(CommandHandler("start", start))

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
                await context.bot.send_message(
                    chat_id=CHAT_ID,  # ✅ Fixed: use env var directly
                    text=message
                )
                print(f"✅ Reminder sent: {task_name}")
            except Exception as e:
                print("Reminder error:", e)

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print("🚀 BOT STARTED")
    app.job_queue.run_repeating(
        check_tasks,
        interval=30,
        first=10,
    )
    app.run_polling(drop_pending_updates=True)  # ✅ Fixed: drop stale updates on start

    app.run_polling()
