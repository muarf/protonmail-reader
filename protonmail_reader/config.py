import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


PROTON_EMAIL = os.getenv("PROTON_EMAIL", "")
PROTON_PASSWORD = os.getenv("PROTON_PASSWORD", "")

PROFILE_DIR = os.getenv("PROFILE_DIR", str(BASE_DIR / "firefox-profile"))
STATE_FILE = os.getenv("STATE_FILE", str(BASE_DIR / "state.json"))

MAX_PER_RUN = _env_int("MAX_PER_RUN", 20)

HEADLESS = _env_bool("HEADLESS", "false")
DISPLAY = os.getenv("DISPLAY", ":1")
XAUTHORITY = os.getenv("XAUTHORITY", os.path.expanduser("~/.Xauthority"))

INBOX_ONLY_SINGLE = _env_bool("INBOX_ONLY_SINGLE", "true")  # only single-message convos
