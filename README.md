# TestFlightChecker

A lightweight Python script that monitors a TestFlight beta URL and alerts you the moment a slot opens up. When Apple's "This beta is full." message disappears from the page, you get an immediate macOS notification, an optional Pushover push notification, and the TestFlight link opens automatically in your browser.

## How it works

The script fetches the TestFlight join page at a configurable interval and checks for a specific string (default: `"This beta is full."`). If the string is found, the beta is still full — nothing to do. If the string is gone, a slot is available and all configured alerts fire.

## Requirements

- macOS (uses `osascript` for notifications and `open` for browser launch)
- Python 3.12+ (uses only the standard library — no packages to install)
- A [Pushover](https://pushover.net) account *(optional, for push notifications)*

## Setup

**1. Clone or download the repo**

**2. Configure Pushover (optional)**

Copy the example config and add your credentials:

```bash
cp config.example.py config.py
```

Then edit `config.py`:

```python
PUSHOVER_API_TOKEN = "your_app_token_here"
PUSHOVER_USER_KEY  = "your_user_key_here"
```

`config.py` is excluded from version control. Leave the values as empty strings to disable Pushover.

**3. Set your target URL**

Edit the configuration block near the top of `TestFlightChecker.py`:

```python
URL           = "https://testflight.apple.com/join/YOUR_CODE"
SEARCH_STRING = "This beta is full."
```

## Usage

Run manually:

```bash
python3 TestFlightChecker.py
```

Or schedule it to run automatically with cron (every 15 minutes):

```bash
crontab -e
```

```
*/15 * * * * /usr/bin/python3 /path/to/TestFlightChecker.py
```

## Alert behaviour

| Situation | macOS notification | Pushover | Browser |
|---|---|---|---|
| Beta is still full | ✅ (silent) | Silent (priority -1) | — |
| **Slot available** | ⚠️ + Sosumi sound | High priority (1) | Opens URL |
| Page unreachable | ❌ + Basso sound | High priority (1) | — |

## Files

| File | Purpose |
|---|---|
| `TestFlightChecker.py` | Main script |
| `config.example.py` | Template for Pushover credentials |
| `config.py` | Your local credentials *(not tracked by git)* |
