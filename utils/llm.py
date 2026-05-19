# utils/llm.py — Unified Groq client
import os
import json
import re
import time
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Load .env from project root (works regardless of cwd)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY)

# Best free model on Groq for structured output tasks
MODEL = "llama-3.3-70b-versatile"


def ask(prompt: str, retries: int = 3) -> str:
    """Send a prompt, return raw text response. Retries on rate limit."""
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate" in error_str.lower():
                wait = (attempt + 1) * 10  # 10s, 20s, 30s
                print(f"[LLM] Rate limited, waiting {wait}s (attempt {attempt + 1}/{retries})")
                time.sleep(wait)
            else:
                raise
    raise Exception("Groq API rate limit exceeded. Please wait a moment and try again.")


def ask_json(prompt: str, retries: int = 3) -> dict:
    """Send a prompt, parse and return JSON. Strips markdown fences and control characters."""
    raw = ask(prompt, retries=retries)
    # Strip markdown fences
    clean = re.sub(r"```json|```", "", raw).strip()
    # Remove all ASCII control characters except normal whitespace (\n \r \t)
    clean = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", clean)
    # Extract only the JSON object/array (handles extra text around it)
    match = re.search(r"(\{.*\}|\[.*\])", clean, re.DOTALL)
    if match:
        clean = match.group(0)
    return json.loads(clean)

