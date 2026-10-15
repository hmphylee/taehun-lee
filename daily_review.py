"""Content workflow daily summary. Python 3.11+, standard library only."""
import argparse
import json
import os
import sqlite3
from datetime import date, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

STATUSES = ("idea", "draft", "production", "ready", "published", "archived")
TIMEZONE = "Asia/Seoul"


def summarize(items, day):
    counts = dict.fromkeys(STATUSES, 0)
    due = 0
    for item in items:
        status = item["status"]
        if status not in counts:
            raise ValueError("Unknown content status")
        counts[status] += 1
        deadline = item.get("due_date")
        if deadline and date.fromisoformat(deadline) <= day:
            due += status not in ("published", "archived")
    return {"review_date": day.isoformat(), "timezone": TIMEZONE,
            "total_items": sum(counts.values()), "status_counts": counts,
            "due_items": due}


def request_json(base, key, path, payload=None):
    headers = {"apikey": key, "Content-Type": "application/json"}
    if payload is not None:
        headers["Prefer"] = "resolution=merge-duplicates,return=minimal"
    data = None if payload is None else json.dumps(payload).encode()
    request = Request(base + "/rest/v1/" + path, data=data, headers=headers)
    try:
        with urlopen(request, timeout=30) as response:
            body = response.read()
        return json.loads(body) if body else None
    except HTTPError as error:
        # Do not log request headers, response bodies, URLs or credentials.
        raise RuntimeError(f"Supabase HTTP {error.code}; check schema and server key") from None
    except (URLError, TimeoutError):
        raise RuntimeError("Supabase connection failed; retry after checking connectivity") from None


def run_cloud(day):
    base = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SECRET_KEY", "")
    parsed = urlparse(base)
    if (parsed.scheme != "https" or not parsed.hostname
            or not parsed.hostname.endswith(".supabase.co")
            or parsed.path or parsed.query or parsed.fragment
            or parsed.username or parsed.password or parsed.port):
        raise ValueError("Set SUPABASE_URL to the HTTPS project URL")
    if not key.startswith("sb_secret_"):
        raise ValueError("Set SUPABASE_SECRET_KEY to a server-side sb_secret_ key")
    items, offset = [], 0
    while True:
        query = urlencode({"select": "id,status,due_date", "order": "id.asc",
                           "offset": offset, "limit": 200})
        batch = request_json(base, key, "content_items?" + query)
        if not isinstance(batch, list):
            raise RuntimeError("Unexpected Supabase content response")
        items.extend(batch)
        if not batch:
            break
        offset += len(batch)
    report = summarize(items, day)
    request_json(base, key, "daily_reviews?on_conflict=review_date,timezone", report)
    return report


def run_demo(day, database):
    # These are deliberately fictional workflow records, not channel metrics.
    items = [{"status": "idea", "due_date": None},
             {"status": "production", "due_date": day.isoformat()},
             {"status": "published", "due_date": day.isoformat()}]
    report = summarize(items, day)
    with sqlite3.connect(database) as db:
        db.execute("CREATE TABLE IF NOT EXISTS daily_reviews "
                   "(review_date TEXT, timezone TEXT, report TEXT, "
                   "PRIMARY KEY (review_date, timezone))")
        db.execute("INSERT INTO daily_reviews VALUES (?, ?, ?) "
                   "ON CONFLICT(review_date,timezone) DO UPDATE SET report=excluded.report",
                   (report["review_date"], TIMEZONE, json.dumps(report, ensure_ascii=False)))
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Local fictional data only")
    parser.add_argument("--demo-db", default="demo.sqlite3")
    args = parser.parse_args()
    day = datetime.now(ZoneInfo(TIMEZONE)).date()
    try:
        report = run_demo(day, args.demo_db) if args.demo else run_cloud(day)
    except (ValueError, RuntimeError, sqlite3.Error) as error:
        parser.exit(1, f"Daily review failed: {error}\n")
    print(json.dumps({"mode": "demo" if args.demo else "supabase", **report},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
