import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from protonmail_reader import Email


async def handle(email: Email) -> bool:
    host = os.getenv("SMTP_HOST", "")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASS", "")
    to_addr = os.getenv("FORWARD_TO", user)

    if not (host and user and to_addr):
        print("[WARN] SMTP not configured; skipping")
        return True

    msg = MIMEMultipart("alternative")
    msg["From"] = f"ProtonReader <{user}>"
    msg["To"] = to_addr
    msg["Subject"] = f"[Proton] {email.subject}"
    msg["Date"] = formatdate(localtime=True)
    msg["X-Proton-Conv-Id"] = email.conv_id
    msg["Reply-To"] = email.from_addr or user
    msg.attach(MIMEText(email.body_text, "plain", "utf-8"))

    try:
        with smtplib.SMTP(host, port, timeout=30) as s:
            s.starttls()
            s.login(user, password)
            s.sendmail(user, to_addr, msg.as_string())
        return True
    except Exception as e:
        print(f"[ERR] SMTP: {e}")
        return False
