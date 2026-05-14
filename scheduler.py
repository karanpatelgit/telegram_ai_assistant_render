from datetime import datetime
from database import get_tasks

# This function runs automatically via JobQueue
async def check_tasks(context):

    now_time = datetime.now().strftime("%H:%M")
    today_date = datetime.now().strftime("%Y-%m-%d")

    tasks = get_tasks()

    for task in tasks:

        task_id = task[0]
        task_date = task[1]
        task_name = task[2]
        task_time = task[3]
        status = task[4]

        # Only today's pending tasks
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
                "Mark done:\n"
                f"/done {task_id}"
            )

            try:
                await context.bot.send_message(
                    chat_id=context.job.chat_id,
                    text=message
                )

                print(f"✅ Reminder sent: {task_name}")

            except Exception as e:
                print("Reminder error:", e)
