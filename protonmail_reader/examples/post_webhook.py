import os
import json

try:
    import httpx
except Exception:
    httpx = None

from protonmail_reader import Email


async def handle(email: Email) -> bool:
    url = os.getenv("WEBHOOK_URL", "")
    if not url:
        print("[WARN] WEBHOOK_URL missing")
        return True
    if httpx is None:
        print("[WARN] httpx not installed")
        return True

    payload = email.to_dict()
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
    return True
