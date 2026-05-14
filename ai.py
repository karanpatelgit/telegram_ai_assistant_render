import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

HF_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mistral-7B-Instruct-v0.2/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

def _call(prompt: str, max_tokens=300) -> str:
    for attempt in range(3):
        try:
            r = requests.post(
                HF_URL,
                headers=HEADERS,
                json={
                    "model": "mistralai/Mistral-7B-Instruct-v0.2",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                },
                timeout=60
            )

            if r.status_code == 503:
                time.sleep(20)
                continue

            if r.status_code != 200:
                return f"❌ HF API Error {r.status_code}: {r.text[:200]}"

            if not r.text.strip():
                time.sleep(5)
                continue

            data = r.json()
            return data["choices"][0]["message"]["content"].strip()

        except requests.exceptions.Timeout:
            return "❌ AI timed out. Try again."
        except Exception as e:
            return f"❌ AI Error: {e}"

    return "❌ AI unavailable. Try again in 30 seconds."

def ask_anything(question: str) -> str:
    prompt = f"[INST] Answer clearly and concisely:\n{question} [/INST]"
    return _call(prompt)

def explain_simple(topic: str) -> str:
    prompt = f"[INST] Explain '{topic}' like I'm 12 years old, in simple bullet points. [/INST]"
    return _call(prompt)

def summarize_text(text: str) -> str:
    prompt = f"[INST] Summarize this in 5 bullet points:\n{text} [/INST]"
    return _call(prompt)

def decision_helper(question: str) -> str:
    prompt = f"""[INST] Help me decide: {question}
Give a structured response with pros/cons and a recommendation. [/INST]"""
    return _call(prompt, max_tokens=400)

def viral_ideas(topic: str) -> str:
    prompt = f"""[INST] Give 5 viral reel ideas about: {topic}
For each: Hook, Script outline, Caption, 5 hashtags. [/INST]"""
    return _call(prompt, max_tokens=500)

def generate_caption(topic: str, platform: str = "instagram") -> str:
    prompt = f"""[INST] Write a viral {platform} caption for: {topic}
Include hook, body, CTA, and 10 hashtags. [/INST]"""
    return _call(prompt, max_tokens=300)

def study_plan(subjects: str, days: int) -> str:
    prompt = f"""[INST] Create a {days}-day study plan for: {subjects}
Format as Day 1: ..., Day 2: ... Be specific. [/INST]"""
    return _call(prompt, max_tokens=500)

def motivation_line() -> str:
    prompt = "[INST] Give one powerful motivational quote for a student. Just the quote. [/INST]"
    return _call(prompt, max_tokens=60)
