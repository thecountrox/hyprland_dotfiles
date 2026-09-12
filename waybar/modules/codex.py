#!/usr/bin/env python3
"""Waybar module: Codex token usage aggregated from local rollout files.

Scans ~/.codex/sessions for `token_usage_record` entries (no network, no
secrets) and shows tokens burned today, with a 7-day total in the tooltip.
Output is a single waybar JSON object.
"""

import glob
import json
import os
import sys
import time
from datetime import datetime

SESSIONS_DIR = os.path.expanduser("~/.codex/sessions")
WEEK_SECS = 7 * 24 * 3600


def fmt(n):
    if n >= 1_000_000:
        s = f"{n / 1_000_000:.1f}".rstrip("0").rstrip(".")
        return f"{s}M"
    if n >= 1_000:
        s = f"{n / 1_000:.0f}"
        return f"{s}k"
    return str(n)


def main():
    now = time.time()
    today = datetime.now().date()
    week_start = now - WEEK_SECS

    day_in = day_out = day_cached = 0
    week_total = 0
    sessions_today = set()
    seen_responses = set()

    pattern = os.path.join(SESSIONS_DIR, "**", "rollout-*.jsonl")
    try:
        files = glob.glob(pattern, recursive=True)
    except Exception:
        files = []
    # Rollout files are append-only: skip anything untouched in the window.
    files = [f for f in files if os.path.getmtime(f) >= week_start - 3600]

    for path in files:
        try:
            fh = open(path, "r", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                if '"token_usage_record"' not in line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                payload = rec.get("payload") or {}
                if rec.get("type") != "token_usage_record" or not payload.get("usage"):
                    continue
                rid = payload.get("response_id")
                if rid and rid in seen_responses:
                    continue
                if rid:
                    seen_responses.add(rid)
                try:
                    ts = datetime.fromisoformat(rec["timestamp"].replace("Z", "+00:00")).timestamp()
                except (KeyError, ValueError):
                    continue
                usage = payload["usage"]
                total = int(usage.get("total_tokens", 0))
                if ts >= week_start:
                    week_total += total
                if datetime.fromtimestamp(ts).date() == today:
                    day_in += int(usage.get("input_tokens", 0))
                    day_out += int(usage.get("output_tokens", 0)) + int(
                        usage.get("reasoning_output_tokens", 0)
                    )
                    day_cached += int(usage.get("cached_input_tokens", 0))
                    if payload.get("session_id"):
                        sessions_today.add(payload["session_id"])

    day_total = day_in + day_out
    if day_total == 0 and week_total == 0:
        print(json.dumps({"text": "󰚩 -", "tooltip": "No Codex usage recorded"}))
        return

    text = f"󰚩 {fmt(day_total)}"
    tooltip = (
        f"Codex usage today: {fmt(day_total)} "
        f"({len(sessions_today)} sessions)\n"
        f"in {fmt(day_in)} / out {fmt(day_out)} / cached {fmt(day_cached)}\n"
        f"last 7 days: {fmt(week_total)}"
    )
    print(json.dumps({"text": text, "tooltip": tooltip}))


if __name__ == "__main__":
    sys.exit(main())
