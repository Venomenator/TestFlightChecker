#!/usr/bin/env python3
# ==============================================================================
# check_url.py - URL Content Monitor
# Python 3.12.4 compatible — uses only standard library modules
# Usage: python3 check_url.py
# Recommended cron: */15 * * * * /usr/bin/python3 /path/to/check_url.py
# ==============================================================================

import urllib.request
import urllib.error
import subprocess
import sys
from datetime import datetime

# ------------------------------------------------------------------------------
# CONFIGURATION — edit these values
# ------------------------------------------------------------------------------
URL = "https://example.com"
SEARCH_STRING = "Expected text here"

NOTIFY_TITLE = "URL Monitor"
NOTIFY_OK_MSG = "✅ String found — Continue to wait."
NOTIFY_FAIL_MSG = f"⚠️ Action required! String NOT found at: {URL}."

TIMEOUT = 15  # seconds


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
        notify(NOTIFY_TITLE, f"❌ Could not reach {URL}", sound="Basso")
        sys.exit(1)

    # String found — all good
    if SEARCH_STRING in page_content:
        log(f"OK: String found at {URL}")
        notify(NOTIFY_TITLE, NOTIFY_OK_MSG)

    # String missing — alert and open browser
    else:
        log(f"ACTION REQUIRED: String NOT found at {URL}")
        notify(NOTIFY_TITLE, NOTIFY_FAIL_MSG, sound="Sosumi")
        open_url(URL)


if __name__ == "__main__":
    main()
