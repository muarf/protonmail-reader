from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class Email:
    conv_id: str
    subject: str
    from_addr: str
    from_name: str
    body_text: str
    inbox_base: str
    url: str
    raw: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
