#!/usr/bin/env python3
# ==============================================================================
# check_url.py - URL Content Monitor
# Python 3.12.4 compatible — uses only standard library modules
# Usage: python3 check_url.py
# Recommended cron: */15 * * * * /usr/bin/python3 /path/to/check_url.py
# ==============================================================================

import urllib.request
import urllib.error
import urllib.parse
import subprocess
import sys
from datetime import datetime

# ------------------------------------------------------------------------------
# CONFIGURATION — edit these values
# ------------------------------------------------------------------------------
URL = "https://testflight.apple.com/join/zGQJrQDU"
SEARCH_STRING = "This beta is full."

NOTIFY_TITLE = "URL Monitor"
NOTIFY_OK_MSG = "❌ String found — Beta is Full."
NOTIFY_FAIL_MSG = "✅ Action required! String NOT found at: {URL}."

TIMEOUT = 15  # seconds

# ------------------------------------------------------------------------------
# PUSHOVER CONFIGURATION — loaded from config.py (not tracked by git)
# Copy config.example.py to config.py and add your credentials there
# ------------------------------------------------------------------------------
try:
    from config import PUSHOVER_API_TOKEN, PUSHOVER_USER_KEY
except ImportError:
    PUSHOVER_API_TOKEN = ""
    PUSHOVER_USER_KEY  = ""

PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"


# ------------------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------------------
def log(message: str) -> None:
    """Print a timestamped log line to stdout."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")


def notify(title: str, message: str, sound: str = "default") -> None:
    """Send a macOS notification via osascript."""
    script = (
        f'display notification "{message}" '
        f'with title "{title}" '
        f'sound name "{sound}"'
    )
    subprocess.run(["osascript", "-e", script], check=False)


def pushover(title: str, message: str, priority: int = 0) -> None:
    """
    Send a Pushover push notification.
    Only fires if PUSHOVER_API_TOKEN and PUSHOVER_USER_KEY are configured.
    priority: -1 (quiet), 0 (normal), 1 (high), 2 (require confirmation)
    """
    if not PUSHOVER_API_TOKEN or not PUSHOVER_USER_KEY:
        return  # Pushover not configured — skip silently

    payload = urllib.parse.urlencode({
        "token":    PUSHOVER_API_TOKEN,
        "user":     PUSHOVER_USER_KEY,
        "title":    title,
        "message":  message,
        "priority": priority,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            PUSHOVER_API_URL,
            data=payload,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            if resp.status == 200:
                log("Pushover notification sent.")
            else:
                log(f"WARNING: Pushover returned status {resp.status}")
    except Exception as e:
        log(f"WARNING: Pushover notification failed — {e}")


def open_url(url: str) -> None:
    """Open a URL in the default browser (macOS)."""
    subprocess.run(["open", url], check=False)


# ------------------------------------------------------------------------------
# FETCH PAGE CONTENT
# ------------------------------------------------------------------------------
def fetch_page(url: str, timeout: int) -> str | None:
    """
    Fetch the page at `url` and return its text content.
    Returns None on any error.
    """
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (check_url monitor)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        log(f"ERROR: HTTP {e.code} received for URL: {url}")
    except urllib.error.URLError as e:
        log(f"ERROR: Could not reach {url} — {e.reason}")
    except TimeoutError:
        log(f"ERROR: Request timed out after {timeout}s for URL: {url}")
    return None


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------
def main() -> None:
    page_content = fetch_page(URL, TIMEOUT)

    # Connection / fetch failed
    if page_content is None:
        msg = f"❌ Could not reach {URL}"
        notify(NOTIFY_TITLE, msg, sound="Basso")
        pushover(NOTIFY_TITLE, msg, priority=1)
        sys.exit(1)

    # String found — all good
    if SEARCH_STRING in page_content:
        log(f"OK: String found at {URL}")
        notify(NOTIFY_TITLE, NOTIFY_OK_MSG)
        pushover(NOTIFY_TITLE, NOTIFY_OK_MSG, priority=-1)

    # String missing — alert and open browser
    else:
        log(f"ACTION REQUIRED: String NOT found at {URL}")
        notify(NOTIFY_TITLE, NOTIFY_FAIL_MSG, sound="Sosumi")
        pushover(NOTIFY_TITLE, NOTIFY_FAIL_MSG, priority=1)
        open_url(URL)


if __name__ == "__main__":
    main()
