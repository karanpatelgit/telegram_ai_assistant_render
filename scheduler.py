import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
import pytz
from database import get_tasks, get_due_revisions, get_exams, reschedule_revision

load_dotenv()
CHAT_ID = os.getenv("CHAT_ID")
ist = pytz.timezone("Asia/Kolkata")

def now_ist():
    return datetime.now(ist)

# ── TASK REMINDERS ───────────────────────────────────────────

async def check_tasks(context):
    now = now_ist()
    now_time = now.strftime("%H:%M")
    today  = now.strftime("%Y-%m-%d")
    tasks  = get_tasks(date=today)

    for t in tasks:
        task_id, task_date, task, task_time, status, category = t
        if task_time == now_time and status != "Done":
            emoji = "📚" if category == "study" else "📅"
            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=(
                    f"{emoji} *Reminder*\n\n"
                    f"📝 {task}\n"
                    f"🏷 Category: {category}\n"
                    f"🆔 ID: {task_id}\n\n"
                    f"Mark done: /done {task_id}"
                ),
                parse_mode="Markdown"
            )

# ── REVISION REMINDERS ───────────────────────────────────────

async def check_revisions(context):
    today = now_ist().strftime("%Y-%m-%d")
    due = get_due_revisions(today)

    for r in due:
        rev_id, topic, subject, next_review, interval = r
        next_interval = min(interval * 2, 30)  # spaced repetition: double interval, cap at 30
        reschedule_revision(rev_id, next_interval)
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=(
                f"🧠 *Spaced Repetition Reminder*\n\n"
                f"📖 Topic: {topic}\n"
                f"📚 Subject: {subject}\n\n"
                f"Next review scheduled in {next_interval} days ✅"
            ),
            parse_mode="Markdown"
        )

# ── EXAM COUNTDOWN ───────────────────────────────────────────

async def check_exam_countdown(context):
    today = now_ist()
    exams = get_exams()

    for exam in exams:
        exam_id, subject, exam_date, exam_time, notes = exam
        try:
            delta = (datetime.strptime(exam_date, "%Y-%m-%d") - today.replace(tzinfo=None)).days
        except:
            continue

        if delta in [7, 3, 1]:
            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=(
                    f"⚠️ *Exam Countdown*\n\n"
                    f"📚 Subject: {subject}\n"
                    f"📅 Date: {exam_date} at {exam_time}\n"
                    f"⏳ *{delta} day(s) remaining!*\n\n"
                    f"💪 Start revising now!"
                ),
                parse_mode="Markdown"
            )

# ── MORNING BRIEFING (7:00 AM IST) ──────────────────────────

async def morning_briefing(context):
    from ai import motivation_line
    today = now_ist().strftime("%Y-%m-%d")
    tasks = get_tasks(date=today)
    exams = get_exams()

    task_lines = "\n".join(
        [f"  • {t[3]} — {t[2]} [{t[5]}]" for t in tasks]
    ) or "  No tasks today 🎉"

    upcoming_exams = [
        e for e in exams
        if (datetime.strptime(e[2], "%Y-%m-%d") - datetime.now()).days <= 7
    ]
    exam_lines = "\n".join(
        [f"  • {e[1]} on {e[2]}" for e in upcoming_exams]
    ) or "  None this week"

    quote = motivation_line()

    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=(
            f"🌅 *Good Morning! Daily Briefing*\n"
            f"📅 {today}\n\n"
            f"📋 *Today's Tasks:*\n{task_lines}\n\n"
            f"🎓 *Upcoming Exams:*\n{exam_lines}\n\n"
            f"💬 *Quote of the Day:*\n_{quote}_"
        ),
        parse_mode="Markdown"
    )

# ── NIGHT SUMMARY (10:00 PM IST) ────────────────────────────

async def night_summary(context):
    today = now_ist().strftime("%Y-%m-%d")
    tasks = get_tasks(date=today)

    done    = [t for t in tasks if t[4] == "Done"]
    pending = [t for t in tasks if t[4] != "Done"]

    done_lines    = "\n".join([f"  ✅ {t[2]}" for t in done])    or "  None"
    pending_lines = "\n".join([f"  ⏳ {t[2]}" for t in pending]) or "  None"

    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=(
            f"🌙 *Night Summary*\n\n"
            f"✅ *Completed ({len(done)}):*\n{done_lines}\n\n"
            f"⏳ *Pending ({len(pending)}):*\n{pending_lines}\n\n"
            f"Rest well, grind tomorrow! 💪"
        ),
        parse_mode="Markdown"
    )
