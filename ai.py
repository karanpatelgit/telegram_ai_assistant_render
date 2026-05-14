import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

HF_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

def _call(prompt: str, max_tokens=300) -> str:
    for attempt in range(3):  # retry 3 times
        try:
            r = requests.post(
                HF_URL,
                headers=HEADERS,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": max_tokens,
                        "temperature": 0.7,
                        "return_full_text": False
                    }
                },
                timeout=60
            )

            # model still loading
            if r.status_code == 503:
                wait = r.json().get("estimated_time", 20)
                time.sleep(min(wait, 20))
                continue

            if r.status_code != 200:
                return f"❌ HF API Error {r.status_code}: {r.text[:200]}"

            if not r.text.strip():
                time.sleep(5)
                continue

            data = r.json()

            if isinstance(data, list):
                return data[0].get("generated_text", "No response").strip()

            if isinstance(data, dict):
                if "error" in data:
                    return f"❌ Model error: {data['error']}"
                return str(data)

            return str(data)

        except requests.exceptions.Timeout:
            return "❌ AI timed out. Try again in a moment."
        except Exception as e:
            return f"❌ AI Error: {e}"

    return "❌ AI unavailable right now. Try again in 30 seconds."


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
