"""Standalone check: is MISTRAL_API_KEY in backend/.env actually valid?

Run this directly — it does NOT start the full app, just makes one real
call to Mistral's API using your configured key, and prints exactly what
Mistral says back. Takes a few seconds.

Usage (from backend/training or backend, with your venv active):
    cd backend
    python scripts/test_mistral_key.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx  # noqa: E402

from app.config import get_settings  # noqa: E402

settings = get_settings()

print(f"MISTRAL_API_KEY loaded: {'yes, starts with ' + settings.mistral_api_key[:8] + '...' if settings.mistral_api_key else 'NO — it is empty/missing from backend/.env'}")
print(f"MISTRAL_MODEL: {settings.mistral_model}")
print(f"MISTRAL_BASE_URL: {settings.mistral_base_url}")

if not settings.mistral_api_key:
    print("\nSTOP: no key loaded at all. Check backend/.env has a MISTRAL_API_KEY= line with no quotes around the value.")
    sys.exit(1)

print("\nCalling Mistral's API directly...")
try:
    response = httpx.post(
        f"{settings.mistral_base_url.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {settings.mistral_api_key}"},
        json={"model": settings.mistral_model, "messages": [{"role": "user", "content": "Say hello in one word."}], "temperature": 0.2},
        timeout=30,
    )
except httpx.RequestError as exc:
    print(f"\nFAILED — could not reach Mistral at all (network/firewall issue): {exc}")
    sys.exit(1)

print(f"\nHTTP status: {response.status_code}")
if response.status_code == 200:
    answer = response.json()["choices"][0]["message"]["content"]
    print(f"SUCCESS — Mistral replied: {answer!r}")
    print("\nYour key and model name are both valid. If Chat/Diet Plan still fail in the app, the issue is elsewhere — send me the error text shown in the app now (it should be a real message, not 'Something went wrong').")
else:
    print(f"Response body: {response.text[:500]}")
    if response.status_code == 401:
        print("\n401 = the key itself is invalid, expired, or wrong product/key type. Get a fresh key from https://console.mistral.ai/api-keys and paste it into backend/.env (La Plateforme key — should NOT need any special prefix besides what the console gives you).")
    elif response.status_code == 404:
        print(f"\n404 = the model name {settings.mistral_model!r} isn't recognized. Double check it against https://docs.mistral.ai/getting-started/models/ — 'mistral-small-latest' should be valid.")
    elif response.status_code == 429:
        print("\n429 = rate limited. Wait a minute and try again, or you're on a very restricted free tier.")
    else:
        print("\nSee the response body above for the exact reason Mistral gave.")
