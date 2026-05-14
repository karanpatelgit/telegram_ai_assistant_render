import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

if not HF_API_KEY:
    logging.warning(
        "HF_API_KEY is not set. AI features will return an error message "
        "instead of calling the Hugging Face API."
    )

HF_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}


def _call(prompt: str, max_tokens=300) -> str:
    if not HF_API_KEY:
        return (
            "⚠️ AI features are unavailable: HF_API_KEY is not configured. "
            "Please set the HF_API_KEY environment variable in your Railway service settings."
        )
    try:
        r = requests.post(
            HF_URL,
            headers=HEADERS,
            json={
                "inputs": prompt,
                "parameters": {"max_new_tokens": max_tokens, "temperature": 0.7}
            },
            timeout=30
        )
        data = r.json()
        if isinstance(data, list):
            full = data[0]["generated_text"]
            # strip the prompt echo that Mistral returns
            return full[len(prompt):].strip()
        return str(data)
    except Exception as e:
        return f"❌ AI Error: {e}"


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
Give a structured response with:
✅ Option A pros/cons
✅ Option B pros/cons
💡 Your recommendation [/INST]"""
    return _call(prompt, max_tokens=400)


def viral_ideas(topic: str) -> str:
    prompt = f"""[INST] Give 5 viral reel/short video ideas about: {topic}
For each idea give:
🎬 Hook (first 3 seconds)
📝 Script outline
📱 Caption
#️⃣ 5 hashtags [/INST]"""
    return _call(prompt, max_tokens=500)


def generate_caption(topic: str, platform: str = "instagram") -> str:
    prompt = f"""[INST] Write a viral {platform} caption for: {topic}
Include: hook line, body, CTA, and 10 hashtags. [/INST]"""
    return _call(prompt, max_tokens=300)


def study_plan(subjects: str, days: int) -> str:
    prompt = f"""[INST] Create a {days}-day study plan for: {subjects}
Format as Day 1: ..., Day 2: ..., etc. Be specific and realistic. [/INST]"""
    return _call(prompt, max_tokens=500)


def motivation_line() -> str:
    prompt = "[INST] Give one powerful motivational quote for a student. Just the quote, no explanation. [/INST]"
    return _call(prompt, max_tokens=60)
