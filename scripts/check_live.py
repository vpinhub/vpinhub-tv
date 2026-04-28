"""
Checks which Twitch channels in vpinhub_tv.json are currently live
and writes the result to live_status.json.

Only writes the file when the set of live channels changes, so GitHub
Pages is not redeployed on every cron tick when nothing has changed.

Run from the repo root:
    python scripts/check_live.py
"""

import json
import re
import time
import requests
from datetime import datetime, timezone

DECAPI_BASE = "https://decapi.me/twitch/uptime/"
UPTIME_RE   = re.compile(r'\d+\s+(hour|minute|second)', re.IGNORECASE)


def is_live(channel: str) -> bool:
    try:
        r = requests.get(DECAPI_BASE + channel, timeout=10)
        return bool(UPTIME_RE.search(r.text.strip()))
    except Exception:
        return False


def main():
    with open("vpinhub_tv.json", encoding="utf-8") as f:
        channels = json.load(f)

    live = []
    for ch in channels:
        if is_live(ch["channel"]):
            live.append(ch["channel"])
        time.sleep(0.3)

    print(f"Live: {live if live else 'none'}")

    # Read existing status so we only commit when something changed
    try:
        with open("live_status.json", encoding="utf-8") as f:
            old = json.load(f)
        old_live = set(old.get("live", []))
    except Exception:
        old_live = None

    if old_live != set(live):
        status = {
            "updated": datetime.now(timezone.utc).isoformat(),
            "live": live,
        }
        with open("live_status.json", "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2)
        print("live_status.json updated.")
    else:
        print("No change — live_status.json not rewritten.")


if __name__ == "__main__":
    main()
