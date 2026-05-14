import os
import requests
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

def _call(prompt: str, max_tokens=300) -> str:
    try:
        r = requests.post(
            GROQ_URL,
            headers=HEADERS,
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7
            },
            timeout=25
        )
        if r.status_code != 200:
            return f"❌ Error {r.status_code}: {r.text[:200]}"
        return r.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        return "❌ AI timed out. Try again."
    except Exception as e:
        return f"❌ AI Error: {e}"

def chat_with_history(messages: list) -> str:
    try:
        r = requests.post(
            GROQ_URL,
            headers=HEADERS,
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a brilliant, friendly AI assistant. "
                            "You remember the full conversation context. "
                            "Be conversational, helpful, and concise. "
                            "Like a smart friend, not a textbook."
                        )
                    }
                ] + messages,
                "max_tokens": 500,
                "temperature": 0.7
            },
            timeout=25
        )
        if r.status_code != 200:
            return f"❌ Error {r.status_code}: {r.text[:200]}"
        return r.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        return "❌ AI timed out. Try again."
    except Exception as e:
        return f"❌ Error: {e}"

def ask_anything(question: str) -> str:
    return _call(f"Answer clearly and conversationally:\n{question}")

def explain_simple(topic: str) -> str:
    return _call(
        f"Explain '{topic}' like I'm 12 years old.\n"
        f"Use simple words, a real-life analogy, and 3-5 bullet points."
    )

def summarize_text(text: str) -> str:
    return _call(
        f"Summarize this:\n{text}\n\n"
        f"Format:\n🎯 Main point\n📌 5 key takeaways\n💡 Why it matters"
    )

def decision_helper(question: str) -> str:
    return _call(
        f"Help me decide: {question}\n"
        f"Give pros/cons for each option and a clear recommendation.",
        max_tokens=400
    )

def viral_ideas(topic: str) -> str:
    return _call(
        f"Give 5 viral reel ideas about: {topic}\n"
        f"For each:\n🎬 Hook\n📝 Script outline\n📱 Caption\n#️⃣ 5 hashtags",
        max_tokens=600
    )

def generate_caption(topic: str, platform: str = "instagram") -> str:
    return _call(
        f"Write a viral {platform} caption for: {topic}\n"
        f"Include hook, body, CTA and 10 hashtags.",
        max_tokens=300
    )

def study_plan(subjects: str, days: int) -> str:
    return _call(
        f"Create a {days}-day study plan for: {subjects}\n"
        f"Format as Day 1: ..., Day 2: ...",
        max_tokens=600
    )

def motivation_line() -> str:
    return _call(
        "Give one powerful motivational quote for a student. Just the quote.",
        max_tokens=60
    )
