"""Standalone check: does GEMINI_API_KEY work for Gemini's chat API?

Run this directly — it does NOT start the full app, just makes one real
call to Gemini and prints exactly what it says back.

Usage:
    cd backend
    python scripts/test_gemini_key.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx  # noqa: E402

from app.config import get_settings  # noqa: E402

settings = get_settings()

print(f"GEMINI_API_KEY loaded: {'yes, starts with ' + settings.gemini_api_key[:8] + '...' if settings.gemini_api_key else 'NO — missing from backend/.env'}")
print(f"gemini_chat_model: {settings.gemini_chat_model}")
print(f"LLM_PROVIDER active: {settings.llm_provider}")

if not settings.gemini_api_key:
    print("\nSTOP: no key loaded. Check backend/.env has GEMINI_API_KEY=... with no quotes.")
    sys.exit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_chat_model}:generateContent"
print(f"\nCalling {url} ...")
try:
    response = httpx.post(
        url,
        params={"key": settings.gemini_api_key},
        json={"contents": [{"role": "user", "parts": [{"text": "Say hello in one word."}]}]},
        timeout=30,
    )
except httpx.RequestError as exc:
    print(f"\nFAILED — could not reach Gemini at all (network/firewall issue): {exc}")
    sys.exit(1)

print(f"\nHTTP status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    try:
        answer = data["candidates"][0]["content"]["parts"][0]["text"]
        print(f"SUCCESS — Gemini replied: {answer!r}")
        print("\nYour key and model both work. Make sure backend/.env has LLM_PROVIDER=gemini, restart the backend, and retry Chat / Diet Plan in the app.")
    except (KeyError, IndexError):
        print(f"200 OK but no usable answer in the response: {data}")
else:
    print(f"Response body: {response.text[:600]}")
    if response.status_code in (400, 404):
        print(f"\nLikely the model name {settings.gemini_chat_model!r} isn't valid for your key/region. Try a different one, e.g. set GEMINI_CHAT_MODEL=gemini-2.5-flash in backend/.env.")
    elif response.status_code == 403:
        print("\n403 = key invalid, or the Generative Language API isn't enabled for this key's project.")
    elif response.status_code == 429:
        print("\n429 = rate limited. Wait a bit and retry.")
