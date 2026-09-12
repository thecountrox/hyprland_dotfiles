#!/usr/bin/env python3
"""Waybar module: Codex rate limits + local token usage.

Bar shows the primary (5h) window percent via `codex app-server`
(`account/rateLimits/read`, so auth/refresh is handled by the CLI itself).
Tooltip adds the secondary (weekly) window plus token usage aggregated
from local rollout files (no network, no secrets).
"""

import glob
import json
import os
import subprocess
import sys
import time
from datetime import datetime

SESSIONS_DIR = os.path.expanduser("~/.codex/sessions")
CACHE_FILE = os.path.join(
    os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache")),
    "waybar-codex-limits.json",
)
CACHE_TTL = 30 * 60
FETCH_TIMEOUT = 20
WEEK_SECS = 7 * 24 * 3600


def fmt(n):
    if n >= 1_000_000:
        s = f"{n / 1_000_000:.1f}".rstrip("0").rstrip(".")
        return f"{s}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}k"
    return str(n)


def window_label(mins):
    if mins is None:
        return "limit"
    if mins >= 10080:
        return "weekly" if mins == 10080 else f"{mins // 10080}w"
    if mins >= 1440:
        return f"{mins // 1440}d"
    if mins >= 60:
        return f"{mins // 60}h"
    return f"{mins}m"


def reset_text(resets_at):
    if not resets_at:
        return "reset unknown"
    dt = datetime.fromtimestamp(resets_at)
    now = datetime.now()
    t12 = dt.strftime("%I:%M %p").lstrip("0")
    delta = int((dt - now).total_seconds())
    rel = ""
    if delta > 0:
        d, rem = divmod(delta, 86400)
        h, rem = divmod(rem, 3600)
        m = rem // 60
        parts = []
        if d:
            parts.append(f"{d}d")
        if h or d:
            parts.append(f"{h}h")
        parts.append(f"{m}m")
        rel = " (in " + " ".join(parts) + ")"
    if dt.date() == now.date():
        return f"resets today at {t12}{rel}"
    return f"resets {dt.strftime('%a %b %d')} at {t12}{rel}"


def fetch_limits():
    """Query rate limits through the Codex app-server (handles auth)."""
    proc = subprocess.Popen(
        ["codex", "app-server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )

    def rpc(id_, method, params=None):
        msg = {"jsonrpc": "2.0", "id": id_, "method": method}
        if params is not None:
            msg["params"] = params
        proc.stdin.write(json.dumps(msg) + "\n")
        proc.stdin.flush()
        deadline = time.time() + FETCH_TIMEOUT
        while time.time() < deadline:
            line = proc.stdout.readline()
            if not line:
                break
            try:
                resp = json.loads(line)
            except ValueError:
                continue
            if resp.get("id") == id_:
                return resp
        raise TimeoutError(method)

    try:
        init = rpc(1, "initialize", {"clientInfo": {"name": "waybar", "version": "1.0"}})
        if "result" not in init:
            raise RuntimeError(f"init failed: {init}")
        resp = rpc(2, "account/rateLimits/read")
        if "result" not in resp:
            raise RuntimeError(f"limits failed: {resp}")
        return resp["result"].get("rateLimits") or {}
    finally:
        try:
            proc.kill()
        except Exception:
            pass


def load_limits():
    try:
        return fetch_limits()
    except Exception:
        pass
    try:
        with open(CACHE_FILE) as fh:
            cached = json.load(fh)
        if time.time() - cached.get("fetched_at", 0) < CACHE_TTL:
            return cached.get("limits") or {}
    except (OSError, ValueError):
        pass
    return {}


def save_limits(limits):
    try:
        with open(CACHE_FILE, "w") as fh:
            json.dump({"fetched_at": time.time(), "limits": limits}, fh)
    except OSError:
        pass


def local_usage():
    """Aggregate token usage from local rollout files for today + 7 days."""
    now = time.time()
    today = datetime.now().date()
    week_start = now - WEEK_SECS
    day_in = day_out = day_cached = day_total = week_total = 0
    sessions_today = set()
    seen = set()

    try:
        files = glob.glob(os.path.join(SESSIONS_DIR, "**", "rollout-*.jsonl"), recursive=True)
    except Exception:
        files = []
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
                if rid and rid in seen:
                    continue
                if rid:
                    seen.add(rid)
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
                    out = int(usage.get("output_tokens", 0)) + int(
                        usage.get("reasoning_output_tokens", 0)
                    )
                    day_out += out
                    day_cached += int(usage.get("cached_input_tokens", 0))
                    day_total += total
                    if payload.get("session_id"):
                        sessions_today.add(payload["session_id"])
    return day_total, day_in, day_out, day_cached, len(sessions_today), week_total


def main():
    limits = load_limits()
    if limits.get("primary") or limits.get("secondary"):
        save_limits(limits)

    day_total, day_in, day_out, day_cached, nsess, week_tokens = local_usage()

    primary = limits.get("primary") or {}
    secondary = limits.get("secondary") or {}
    p_pct = primary.get("usedPercent")
    s_pct = secondary.get("usedPercent")

    if p_pct is None and s_pct is None:
        # Limits unreachable: fall back to local token counts.
        if day_total == 0:
            print(json.dumps({"text": "󰚩   -", "tooltip": "Codex limits unavailable"}))
            return
        print(
            json.dumps(
                {
                    "text": f"󰚩   {fmt(day_total)}",
                    "tooltip": f"Codex limits unavailable\ntoday: {fmt(day_total)} tokens",
                }
            )
        )
        return

    p_pct = p_pct if p_pct is not None else 0
    s_pct = s_pct if s_pct is not None else 0
    p_rem = 100 - p_pct
    s_rem = 100 - s_pct
    p_label = window_label(primary.get("windowDurationMins"))
    s_label = window_label(secondary.get("windowDurationMins"))

    klass = "critical" if p_rem <= 10 else "warning" if p_rem <= 30 else ""
    text = f"󰚩   {p_rem:.0f}%"
    tooltip = (
        f"{p_label} limit: {p_rem:.0f}% remaining, {reset_text(primary.get('resetsAt'))}\n"
        f"{s_label} limit: {s_rem:.0f}% remaining, {reset_text(secondary.get('resetsAt'))}\n"
        f"local usage today: {fmt(day_total)} "
        f"(in {fmt(day_in)} / out {fmt(day_out)} / cached {fmt(day_cached)}, "
        f"{nsess} sessions)\n"
        f"local usage 7d: {fmt(week_tokens)}"
    )
    out = {"text": text, "tooltip": tooltip, "percentage": round(p_rem)}
    if klass:
        out["class"] = klass
    print(json.dumps(out))


if __name__ == "__main__":
    sys.exit(main())
