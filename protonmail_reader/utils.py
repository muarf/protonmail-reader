from pathlib import Path


def ensure_firefox(playwright) -> str:
    """Return path to firefox or raise with hint."""
    try:
        browser_type = playwright.firefox
        _ = browser_type.name
        return ""
    except Exception as e:
        raise RuntimeError(f"Playwright Firefox not installed: {e}") from e


def nav_filter_bad(frame_text: str) -> bool:
    """Return True if text looks like sidebar/nav chrome."""
    lower = frame_text[:200].lower()
    for nav in ["boite de réception", "navigation", "proton mail", "sidebar", "folders"]:
        if nav in lower:
            return True
    return False
