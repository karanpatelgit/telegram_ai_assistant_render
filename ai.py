import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

def _call(prompt: str, max_tokens=300) -> str:
    # Try multiple free models in order
    models = [
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "HuggingFaceH4/zephyr-7b-beta",
        "microsoft/DialoGPT-large",
    ]
    
    for model in models:
        url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        
        for attempt in range(2):
            try:
                r = requests.post(
                    url,
                    headers=headers,
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": max_tokens,
                            "temperature": 0.7,
                            "return_full_text": False,
                            "do_sample": True
                        }
                    },
                    timeout=60
                )

                # model loading
                if r.status_code == 503:
                    estimated = r.json().get("estimated_time", 15)
                    time.sleep(min(estimated, 15))
                    continue

                if r.status_code == 200 and r.text.strip():
                    data = r.json()
                    if isinstance(data, list) and len(data) > 0:
                        text = data[0].get("generated_text", "").strip()
                        if text:
                            return text

            except Exception:
                continue

        # if this model failed, try next one
        continue

    return "❌ All AI models unavailable right now. Try again in a minute."


def ask_anything(question: str) -> str:
    prompt = f"<s>[INST] Answer clearly and concisely:\n{question} [/INST]"
    return _call(prompt)

def explain_simple(topic: str) -> str:
    prompt = f"<s>[INST] Explain '{topic}' like I'm 12 years old, in simple bullet points. [/INST]"
    return _call(prompt)

def summarize_text(text: str) -> str:
    prompt = f"<s>[INST] Summarize this in 5 bullet points:\n{text} [/INST]"
    return _call(prompt)

def decision_helper(question: str) -> str:
    prompt = f"<s>[INST] Help me decide: {question}\nGive pros, cons and a recommendation. [/INST]"
    return _call(prompt, max_tokens=400)

def viral_ideas(topic: str) -> str:
    prompt = f"<s>[INST] Give 5 viral reel ideas about: {topic}\nFor each give: Hook, Script, Caption, 5 Hashtags. [/INST]"
    return _call(prompt, max_tokens=500)

def generate_caption(topic: str, platform: str = "instagram") -> str:
    prompt = f"<s>[INST] Write a viral {platform} caption for: {topic}\nInclude hook, body, CTA and 10 hashtags. [/INST]"
    return _call(prompt, max_tokens=300)

def study_plan(subjects: str, days: int) -> str:
    prompt = f"<s>[INST] Create a {days}-day study plan for: {subjects}\nFormat as Day 1: ..., Day 2: ... [/INST]"
    return _call(prompt, max_tokens=500)

def motivation_line() -> str:
    prompt = "<s>[INST] Give one powerful motivational quote for a student. Just the quote, nothing else. [/INST]"
    return _call(prompt, max_tokens=60)
