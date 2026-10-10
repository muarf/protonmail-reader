import asyncio
import os
from pathlib import Path
from typing import Any, Awaitable, Callable

from .config import (
    HEADLESS,
    INBOX_ONLY_SINGLE,
    MAX_PER_RUN,
    PROFILE_DIR,
    PROTON_EMAIL,
    PROTON_PASSWORD,
)
from .models import Email
from .state import State
from .utils import nav_filter_bad


Handler = Callable[[Email], Awaitable[bool] | bool]


class ProtonFetcher:
    def __init__(self, state_path: str | Path | None = None):
        from .config import STATE_FILE

        self.state_path = str(state_path or STATE_FILE)
        self.state = State(self.state_path)

    async def fetch_new(
        self,
        handler: Handler | None = None,
        dry_run: bool = False,
    ) -> list[Email]:
        from playwright.async_api import async_playwright

        env = {}
        if os.getenv("DISPLAY"):
            env["DISPLAY"] = os.getenv("DISPLAY", ":1")
        if os.getenv("XAUTHORITY"):
            env["XAUTHORITY"] = os.getenv("XAUTHORITY")

        results: list[Email] = []
        all_api: dict[str, Any] = {}

        async with async_playwright() as p:
            context = await p.firefox.launch_persistent_context(
                PROFILE_DIR,
                headless=HEADLESS,
                viewport={"width": 1280, "height": 720},
                env=env,
            )

            page = context.pages[0] if context.pages else await context.new_page()

            async def on_response(response):
                try:
                    if "/api/" in response.url and "conversations" in response.url:
                        # try to cache first batch? keep minimal
                        pass
                    if "/api/" in response.url:
                        try:
                            body = await response.json()
                            if isinstance(body, dict) and body.get("Code") == 1000:
                                all_api[response.url] = body
                        except Exception:
                            pass
                except Exception:
                    pass

            page.on("response", on_response)

            await page.goto(
                "https://account.proton.me/mail",
                wait_until="networkidle",
                timeout=60000,
            )
            await asyncio.sleep(2)

            if PROTON_EMAIL and PROTON_PASSWORD:
                try:
                    await page.fill("#username", PROTON_EMAIL)
                    await page.fill("#password", PROTON_PASSWORD)
                    await page.click('button[type="submit"]')
                except Exception:
                    pass

            for _ in range(20):
                await asyncio.sleep(3)
                if "inbox" in page.url:
                    await asyncio.sleep(5)
                    break
            else:
                try:
                    await context.close()
                except Exception:
                    pass
                return results

            conv_list = []
            for url, data in all_api.items():
                if "conversations?" in url and isinstance(data, dict) and data.get("Code") == 1000:
                    conv_list = data.get("Conversations", []) or []
                    break

            if not conv_list:
                try:
                    await context.close()
                except Exception:
                    pass
                return results

            inbox_base = page.url.split("/inbox")[0]

            forwarded_ids = self.state.forwarded_ids
            candidates = []
            for conv in conv_list:
                if len(candidates) >= MAX_PER_RUN:
                    break
                conv_id = str(conv.get("ID", ""))
                if not conv_id or conv_id in forwarded_ids:
                    continue
                if INBOX_ONLY_SINGLE and conv.get("NumMessages", 0) > 1:
                    continue
                candidates.append(conv)

            for conv in candidates:
                conv_id = str(conv.get("ID", ""))
                subject = conv.get("Subject", "No subject") or "No subject"
                senders = conv.get("Senders", []) or []
                sender_addr = senders[0].get("Address", "") if senders else ""
                sender_name = senders[0].get("Name", "") if senders else ""

                try:
                    await page.goto(
                        f"{inbox_base}/inbox/{conv_id}",
                        wait_until="networkidle",
                        timeout=30000,
                    )
                    await asyncio.sleep(4)

                    body_text = ""
                    conv_frames = []
                    for frame in page.frames:
                        try:
                            furl = frame.url
                            if furl and "/inbox/" in furl:
                                conv_frames.append(frame)
                        except Exception:
                            continue

                    for frame in reversed(conv_frames):
                        try:
                            text = await frame.inner_text("body", timeout=5000)
                            text = (text or "").strip()
                            if text and len(text) > 10:
                                if nav_filter_bad(text):
                                    continue
                                body_text = text
                                break
                        except Exception:
                            continue

                    if not body_text:
                        for frame in page.frames:
                            try:
                                text = await frame.inner_text("body", timeout=5000)
                                text = (text or "").strip()
                                if not text:
                                    continue
                                if nav_filter_bad(text[:200]):
                                    continue
                                lines = [l.strip() for l in text.split("\n") if l.strip()]
                                for j, line in enumerate(lines):
                                    low = line.lower()
                                    if any(
                                        kw in low
                                        for kw in [
                                            "bonjour",
                                            "madame",
                                            "monsieur",
                                            "objet:",
                                            "référence",
                                            "cher ",
                                        ]
                                    ):
                                        body_text = "\n".join(lines[max(0, j - 2) :])
                                        break
                                if body_text:
                                    break
                            except Exception:
                                continue

                    if not body_text:
                        continue

                    email = Email(
                        conv_id=conv_id,
                        subject=subject,
                        from_addr=sender_addr,
                        from_name=sender_name,
                        body_text=body_text,
                        inbox_base=inbox_base,
                        url=f"{inbox_base}/inbox/{conv_id}",
                        raw=conv,
                    )
                    results.append(email)

                    if dry_run:
                        continue

                    if handler is not None:
                        res = handler(email)
                        if asyncio.iscoroutine(res):
                            ok = await res
                        else:
                            ok = bool(res)
                        if ok:
                            self.state.add(conv_id)
                        continue

                    self.state.add(conv_id)
                except Exception:
                    continue

            try:
                await context.close()
            except Exception:
                pass

        return results
