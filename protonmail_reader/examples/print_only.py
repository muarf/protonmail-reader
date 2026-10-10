from protonmail_reader import Email


async def handle(email: Email) -> bool:
    print("---")
    print(f"conv_id: {email.conv_id}")
    print(f"from: {email.from_name} <{email.from_addr}>")
    print(f"subject: {email.subject}")
    print(f"url: {email.url}")
    print(f"body_chars: {len(email.body_text)}")
    print(email.body_text[:400])
    print("---")
    return True
