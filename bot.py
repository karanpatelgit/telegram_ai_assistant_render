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
#==============================
import requests
import os

HF_API_KEY = os.getenv("HF_API_KEY")

HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

async def ai_reply(prompt: str):

    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "return_full_text": False
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        data = response.json()

        # HF returns list format sometimes
        if isinstance(data, list):
            return data[0]["generated_text"]

        # error handling
        if "error" in data:
            return f"⚠️ AI Error: {data['error']}"

        return str(data)

    except Exception as e:
        return f"❌ AI Request Failed: {str(e)}"
#==================================================        
async def ai(update, context):

    try:
        user_text = update.message.text.replace("/ai", "").strip()

        if not user_text:
            await update.message.reply_text(
                "❌ Use: /ai your question"
            )
            return

        reply = await ai_reply(user_text)

        await update.message.reply_text(reply)

    except Exception as e:
        print(e)
        await update.message.reply_text("❌ AI error")
app.add_handler(CommandHandler("ai", ai))
#==============================================================
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
