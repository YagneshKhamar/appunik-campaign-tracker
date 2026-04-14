#!/usr/bin/env python3
"""
AppUnik Campaign Tracker — Real-time Telegram reply parser.
Runs every 30 minutes via GitHub Actions.
Reads Telegram replies, updates progress.json and campaign-log.md.

Expected reply format from user:
  Done: LinkedIn post, DM outreach
  Skipped: YouTube Short
  Note: 3 connection requests accepted, 1 CTO replied
"""

import os
import json
import re
import requests
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = int(os.environ["TELEGRAM_CHAT_ID"])
PROGRESS_FILE = "progress.json"
LOG_FILE = "campaign-log.md"

# Only process messages from the last 35 minutes (30-min cron + 5-min buffer)
LOOKBACK_SECONDS = 6 * 60 * 60 + 5 * 60  # 6 hours + 5 min buffer


def fetch_updates():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-50&limit=50"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        print("Telegram getUpdates failed:", data)
        return []
    return data.get("result", [])


def parse_reply(text):
    """Parse Done/Skipped/Note lines from a Telegram message."""
    done = []
    skipped = []
    notes = []

    for line in text.strip().splitlines():
        line = line.strip()
        lower = line.lower()
        if lower.startswith("done:"):
            items = line[5:].strip()
            done = [x.strip() for x in re.split(r"[,;]", items) if x.strip()]
        elif lower.startswith("skipped:"):
            items = line[8:].strip()
            skipped = [x.strip() for x in re.split(r"[,;]", items) if x.strip()]
        elif lower.startswith("note:"):
            notes.append(line[5:].strip())

    return done, skipped, notes


def extract_counts(done_list, notes_list):
    """
    Try to extract numeric increments from done/notes for cumulative stats.
    Looks for patterns like "5 DMs", "1 post", "2 connections", "1 call"
    """
    all_text = " ".join(done_list + notes_list).lower()

    posts = 0
    dms = 0
    connections = 0
    calls = 0

    # Posts / LinkedIn post
    m = re.search(r"(\d+)\s*(linkedin\s+)?post", all_text)
    if m:
        posts = int(m.group(1))
    elif "post" in all_text and "skipped" not in all_text:
        posts = 1  # assume 1 post if mentioned without a number

    # DMs
    m = re.search(r"(\d+)\s*dm", all_text)
    if m:
        dms = int(m.group(1))

    # Connection requests accepted / connections made
    m = re.search(r"(\d+)\s*(connection|connect)", all_text)
    if m:
        connections = int(m.group(1))

    # Scale Diagnostic / calls booked
    m = re.search(r"(\d+)\s*(call|diagnostic|booked)", all_text)
    if m:
        calls = int(m.group(1))

    return posts, dms, connections, calls


def day_of_week_key():
    """Return the week_tracker key for today (UTC)."""
    keys = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    return keys[datetime.now(timezone.utc).weekday()]


def update_progress(done, skipped, notes):
    with open(PROGRESS_FILE, "r") as f:
        progress = json.load(f)

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Don't double-process: skip if today's entry already has data with same tasks
    yesterday = progress.get("yesterday", {})
    if (
        yesterday.get("date") == today_str
        and yesterday.get("tasks_done") == done
        and yesterday.get("tasks_skipped") == skipped
    ):
        print("No new data — already up to date.")
        return False

    # Update yesterday entry with today's report
    progress["yesterday"] = {
        "date": today_str,
        "tasks_planned": yesterday.get("tasks_planned", []),
        "tasks_done": done,
        "tasks_skipped": skipped,
        "user_notes": " | ".join(notes) if notes else "",
        "completion_status": "done" if done and not skipped else ("partial" if done else "skipped"),
    }

    # Update week_tracker
    dow = day_of_week_key()
    if dow in progress["week_tracker"] and done:
        progress["week_tracker"][dow] = True

    # Update cumulative counts
    posts, dms, connections, calls = extract_counts(done, notes)
    progress["cumulative"]["posts_published"] += posts
    progress["cumulative"]["dms_sent"] += dms
    progress["cumulative"]["cto_connections_made"] += connections
    progress["cumulative"]["calls_booked"] += calls

    progress["last_updated"] = now_str

    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)

    print(f"progress.json updated — done={done}, skipped={skipped}, notes={notes}")
    return True


def append_log(done, skipped, notes):
    today_str = datetime.now(timezone.utc).strftime("%B %d, %Y")
    now_str = datetime.now(timezone.utc).strftime("%H:%M UTC")

    entry_lines = [
        f"\n### {today_str} — Real-time update ({now_str})",
    ]
    if done:
        entry_lines.append(f"- **Done:** {', '.join(done)}")
    if skipped:
        entry_lines.append(f"- **Skipped:** {', '.join(skipped)}")
    if notes:
        for note in notes:
            entry_lines.append(f"- **Note:** {note}")

    entry_lines.append("")

    with open(LOG_FILE, "a") as f:
        f.write("\n".join(entry_lines) + "\n")

    print("campaign-log.md updated.")


def main():
    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc - timedelta(seconds=LOOKBACK_SECONDS)

    updates = fetch_updates()
    if not updates:
        print("No Telegram updates found.")
        return

    # Find the most recent qualifying message from our chat
    qualifying = []
    for update in updates:
        msg = update.get("message") or update.get("edited_message")
        if not msg:
            continue
        if msg.get("chat", {}).get("id") != CHAT_ID:
            continue
        text = msg.get("text", "")
        if not text:
            continue

        # Must contain at least one of Done/Skipped/Note
        lower = text.lower()
        if not any(lower.find(k + ":") >= 0 for k in ["done", "skipped", "note"]):
            continue

        msg_time = datetime.fromtimestamp(msg["date"], tz=timezone.utc)
        if msg_time < cutoff:
            continue

        qualifying.append((msg_time, text))

    if not qualifying:
        print("No qualifying reply found in the last 35 minutes.")
        return

    # Use the most recent qualifying message
    qualifying.sort(key=lambda x: x[0], reverse=True)
    _, text = qualifying[0]
    print(f"Found reply: {text[:100]}")

    done, skipped, notes = parse_reply(text)
    changed = update_progress(done, skipped, notes)
    if changed:
        append_log(done, skipped, notes)


if __name__ == "__main__":
    main()
