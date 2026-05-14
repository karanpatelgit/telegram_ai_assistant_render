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
                "model": "llama3-8b-8192",  # free & fast
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7
            },
            timeout=30
        )

        if r.status_code != 200:
            return f"❌ Error {r.status_code}: {r.text[:200]}"

        data = r.json()
        return data["choices"][0]["message"]["content"].strip()

    except requests.exceptions.Timeout:
        return "❌ AI timed out. Try again."
    except Exception as e:
        return f"❌ AI Error: {e}"


def ask_anything(question: str) -> str:
    return _call(f"Answer clearly and concisely:\n{question}")

def explain_simple(topic: str) -> str:
    return _call(f"Explain '{topic}' like I'm 12 years old, in simple bullet points.")

def summarize_text(text: str) -> str:
    return _call(f"Summarize this in 5 bullet points:\n{text}")

def decision_helper(question: str) -> str:
    return _call(
        f"Help me decide: {question}\nGive pros, cons and a clear recommendation.",
        max_tokens=400
    )

def viral_ideas(topic: str) -> str:
    return _call(
        f"Give 5 viral reel ideas about: {topic}\n"
        f"For each give:\n🎬 Hook\n📝 Script outline\n📱 Caption\n#️⃣ 5 hashtags",
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
        f"Format as Day 1: ..., Day 2: ... Be specific and realistic.",
        max_tokens=600
    )

def motivation_line() -> str:
    return _call(
        "Give one powerful motivational quote for a student. Just the quote, nothing else.",
        max_tokens=60
    )
