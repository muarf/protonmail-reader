# protonmail-reader

Minimal, autonomous ProtonMail reader using Playwright + Firefox. Fetch new unread emails as plain Python objects and pipe them anywhere (Signal/Telegram/WhatsApp/email/webhook).

## Why

- Reads ProtonMail without IMAP (uses browser API via Playwright)
- No secrets hardcoded — uses `.env` or existing `firefox-profile` session
- Plugable handler: call any async/sync function per email
- Keeps track of processed `conv_id` in `state.json`
- Works with existing X11/Display (or headless + xvfb)

## Quick start

```bash
cd protonmail-reader
cp .env.example .env
# Edit .env if needed (PROTON_EMAIL/PROTON_PASSWORD optional if logged in)
pip install -r requirements.txt
playwright install firefox
```

## Usage

Dry-run (just print):
```bash
export DISPLAY=:1  # or set in .env
python cli.py --dry-run --handler protonmail_reader.examples.print_only:handle
```

Process & mark:
```bash
python cli.py --handler protonmail_reader.examples.print_only:handle
```

Custom handler:
```bash
python cli.py --handler mymodule:process_email
```

SMTP example:
```bash
export SMTP_HOST=mail.riseup.net SMTP_PORT=587 SMTP_USER=you@riseup.net SMTP_PASS=pass FORWARD_TO=dest@riseup.net
python cli.py --handler protonmail_reader.examples.forward_smtp:handle
```

Webhook example:
```bash
export WEBHOOK_URL=https://example.com/hook
python cli.py --handler protonmail_reader.examples.post_webhook:handle
```

## Notes

- If already logged in, `firefox-profile/` is reused (fast, no login). Do **not** commit it.
- First login may require CAPTCHA/2FA — run with visible DISPLAY once.
- Only single-message conversations are processed by default (`INBOX_ONLY_SINGLE=true`). Tune via env.
- BODGE-y: relies on Proton's UI/iframes; if Proton changes, extraction may need tweak (frame selection + nav filter).
- State grows but capped (~5000 ids) — safe for long-running.
