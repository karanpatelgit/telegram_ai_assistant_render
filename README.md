# Telegram AI Assistant — Render Deployable

Telegram bot (tasks, exams, notes, AI chat via Groq) deployed on **Render** as a **Web Service** using **webhooks**.

## Deploy on Render

### Option A — Blueprint (one-click)
1. Push this repo to GitHub.
2. Render → **New +** → **Blueprint** → connect repo. Render reads `render.yaml`.
3. After first deploy, copy the service URL → set `WEBHOOK_URL` in Environment → redeploy.

### Option B — Manual
- Build: `pip install -r requirements.txt`
- Start: `python bot.py`
- Add env vars below, then deploy.

## Environment variables

| Key | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | From @BotFather |
| `WEBHOOK_URL` | Your Render URL, e.g. `https://my-bot.onrender.com` (no trailing slash) |
| `GROQ_API_KEY` | From console.groq.com |
| `CHAT_ID` | Your Telegram chat ID for scheduler reminders |

Render auto-injects `PORT` — do not set it.

## Local dev
```bash
pip install -r requirements.txt
cp .env.example .env  # fill tokens, leave WEBHOOK_URL empty
python bot.py
