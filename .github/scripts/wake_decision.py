#!/usr/bin/env python3
"""wake_decision.py — external wake-up decision (GitHub Actions side).

Reads the PUBLIC live-state.json (the board), decides whether the VM-side
engine needs waking, and writes 209-intelligence/wake.json in the exact
schema the VM-side watchdog/poller reads.

WHY THIS EXISTS: a VM replacement wipes /etc and kills everything inside
(dispatcher unit, mesh unit, Kuma). This check runs OUTSIDE the VM, on
GitHub Actions, reading the public board served by GitHub Pages — which
survives VM death — and leaves wake commands in the repo for the VM-side
watchdog to pick up once it is back.

Board sources (in order; first success wins):
  1. https://209connect.com/209-intelligence/live-state.json
     (apex, flaps behind Cloudflare)
  2. https://sicairos4.github.io/david-sicairos-site/209-intelligence/live-state.json
     (Pages origin, stable)
Both fetched with a browser UA + cache-buster, no auth.

Wake conditions (ANY fires a wake):
  * board stale: generated_at age > 15 minutes (or board unreachable /
    timestamp unparseable — the push chain is silent, treat as stale)
  * any scored lane past 2x its cadence
    (cadence: board's own cadence_minutes when present, else
     Threads/Bluesky 20m, LinkedIn 25m, IG/FB 30m, YouTube/TikTok 35m)
  * health < 50% (system_health.pct)

Wake services emitted (subset of the wake.json enum):
  * board stale / unreachable / health < 50 -> lane-dispatcher, mesh-hub,
    cli-executor, kuma (a dead VM kills all of them; wake everything)
  * lane(s) past 2x cadence -> lane-dispatcher (it owns the refire),
    plus the per-lane entries under "lanes" (action "refire")
  * "receiver" is never emitted by this checker (no webhook receiver is
    live yet; its wakes come from the webhook path, not this board check)

Write throttle (keeps Pages builds rare while healthy):
  * wake condition  -> ALWAYS write (fresh every run, so the poller never
    sees a live wake go stale while the condition persists)
  * healthy         -> write only when the previous wake.json is missing,
    previously carried a wake (wake -> healthy flip), or is >= 60 min old
    (hourly heartbeat). Otherwise leave the file untouched.
  * Rationale: the poller treats a >15m-old wake.json as no-wake, which
    is the correct reading while healthy; only a live wake needs freshness.

Usage (workflow):
  python3 .github/scripts/wake_decision.py --out 209-intelligence/wake.json
Local dry-run:
  python3 wake_decision.py --out /tmp/wake-test/wake.json
  python3 wake_decision.py --board-file /tmp/live-state-now.json --out /tmp/wake-test/wake.json
Exit 0 on a written or correctly-skipped file; exit 1 only if the output
cannot be written. The decision is printed on stdout for the Actions log.
Stdlib only.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

APEX_URL = "https://209connect.com/209-intelligence/live-state.json"
PAGES_URL = ("https://sicairos4.github.io/david-sicairos-site"
             "/209-intelligence/live-state.json")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

STALE_MIN = 15
HEALTH_MIN = 50
HEARTBEAT_MIN = 60

# Fallback cadences (minutes) when the board carries no cadence_minutes.
CADENCE_TABLE = {"threads": 20, "bluesky": 20, "linkedin": 25,
                 "youtube": 35, "tiktok": 35}
DEFAULT_CADENCE = 30
CORE_SERVICES = ["lane-dispatcher", "mesh-hub", "cli-executor", "kuma"]

PT = ZoneInfo("America/Los_Angeles")


def _parse_iso(s):
    """Parse an ISO-8601 string to an aware UTC datetime, or None."""
    if not s or not isinstance(s, str):
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _parse_pt_display(s):
    """Parse '2026-11-20 01:22 PM PT' to an aware UTC datetime, or None."""
    if not s or not isinstance(s, str):
        return None
    txt = s.strip()
    if txt.endswith(" PT"):
        txt = txt[:-3]
    try:
        dt = datetime.strptime(txt, "%Y-%m-%d %I:%M %p")
    except ValueError:
        return None
    return dt.replace(tzinfo=PT).astimezone(timezone.utc)


def _board_generated_utc(board):
    dt = _parse_iso(board.get("generated_at_iso"))
    if dt:
        return dt, board.get("generated_at_pt")
    dt = _parse_pt_display(board.get("generated_at_pt"))
    if dt:
        return dt, board.get("generated_at_pt")
    # Last resort: an epoch field, if a future board writer adds one.
    for key in ("generated_at_epoch", "generated_at", "generated_epoch"):
        v = board.get(key)
        if isinstance(v, (int, float)):
            return (datetime.fromtimestamp(v, tz=timezone.utc),
                    board.get("generated_at_pt"))
    return None, board.get("generated_at_pt")


def _fetch_board(urls):
    """Fetch the board from the first URL that returns valid JSON.

    Returns (board_dict_or_None, source_url_or_None, error_str_or_None).
    """
    last_err = "no urls"
    for url in urls:
        bust = ("%s%st=%d" % (url, "&" if "?" in url else "?",
                              int(time.time())))
        req = urllib.request.Request(
            bust, headers={"User-Agent": UA, "Cache-Control": "no-cache"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
            board = json.loads(raw.decode("utf-8"))
            if isinstance(board, dict) and "lanes" in board:
                return board, url, None
            last_err = "%s: JSON has no 'lanes' key" % url
        except Exception as e:  # noqa: BLE001 — any fetch/parse failure
            last_err = "%s: %s" % (url, e)
    return None, None, last_err


def _cadence_for(lane):
    c = lane.get("cadence_minutes")
    if isinstance(c, (int, float)) and c > 0:
        return float(c)
    key = (lane.get("key") or "").lower()
    if key in CADENCE_TABLE:
        return float(CADENCE_TABLE[key])
    for prefix, cad in (("ig_", 30), ("fb_", 30)):
        if key.startswith(prefix):
            return float(cad)
    return float(DEFAULT_CADENCE)


def _lane_gap_min(lane, now_utc):
    g = lane.get("gap_minutes")
    if isinstance(g, (int, float)):
        return float(g)
    last = _parse_iso(lane.get("last_verified_iso"))
    if last:
        return round((now_utc - last).total_seconds() / 60.0, 1)
    return None


def _pt_display(dt_utc):
    if not dt_utc:
        return None
    return dt_utc.astimezone(PT).strftime("%Y-%m-%d %I:%M %p PT")


def _read_existing(out_path):
    try:
        with open(out_path) as f:
            prev = json.load(f)
        if isinstance(prev, dict):
            return prev
    except Exception:  # noqa: BLE001 — missing/malformed = no previous
        pass
    return None


def decide(board, board_source, fetch_error, now_utc):
    """Compute the wake.json payload from a fetched board (or None)."""
    now_pt = now_utc.astimezone(PT)
    generated_utc = None
    generated_pt = None
    board_age_min = None
    health = None
    over_lanes = []

    if board is None:
        board_age_min = None  # unreachable == stale; see wake below
    else:
        generated_utc, generated_pt = _board_generated_utc(board)
        if generated_utc is not None:
            board_age_min = round(
                (now_utc - generated_utc).total_seconds() / 60.0, 1)
        h = (board.get("system_health") or {}).get("pct")
        if isinstance(h, (int, float)):
            health = round(float(h), 1)
        for lane in board.get("lanes") or []:
            if not isinstance(lane, dict):
                continue
            if lane.get("state") not in ("ON CADENCE", "DUE", "MISSING"):
                continue  # RETIRED / NOT LIVE YET / PAUSED / BUILDING: unscored
            gap = _lane_gap_min(lane, now_utc)
            if gap is None:
                continue
            cad = _cadence_for(lane)
            if gap > 2 * cad:
                last_pt = lane.get("last_verified_pt")
                if not last_pt:
                    last_iso = _parse_iso(lane.get("last_verified_iso"))
                    last_pt = _pt_display(last_iso)
                over_lanes.append({
                    "lane": lane.get("key"),
                    "gap_min": round(float(gap), 1),
                    "last_verified_pt": last_pt,
                    "action": "refire",
                })

    board_stale = board is None or board_age_min is None or \
        board_age_min > STALE_MIN
    health_low = health is not None and health < HEALTH_MIN

    wake = []
    seen_services = set()

    def add_service(service, reason, since_pt):
        if service in seen_services:
            return
        seen_services.add(service)
        wake.append({"service": service, "reason": reason,
                     "since_pt": since_pt})

    if board is None:
        reason = ("live-state.json unreachable from both origins "
                  "(apex + Pages origin): %s" % fetch_error)
        for svc in CORE_SERVICES:
            add_service(svc, reason, None)
    elif board_stale:
        reason = ("board stale: generated %s, age %s min (> %d min); "
                  "live-state push chain silent, VM may be down"
                  % (generated_pt, board_age_min, STALE_MIN))
        for svc in CORE_SERVICES:
            add_service(svc, reason, generated_pt)
    if health_low:
        reason = ("health %.1f%% below %d%% (board generated %s)"
                  % (health, HEALTH_MIN, generated_pt))
        for svc in CORE_SERVICES:
            add_service(svc, reason, generated_pt)
    if over_lanes:
        names = ", ".join("%s (%s min)" % (l["lane"], l["gap_min"])
                          for l in over_lanes)
        since = over_lanes[0]["last_verified_pt"]
        add_service("lane-dispatcher",
                    "lanes past 2x cadence, refire: %s" % names, since)

    payload = {
        "generated_at_utc": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_at_pt": now_pt.strftime("%Y-%m-%d %I:%M %p PT"),
        "board_age_min": board_age_min,
        "health_percent": health,
        "wake": wake,
        "lanes": over_lanes,
    }
    summary = {
        "board_source": board_source,
        "fetch_error": fetch_error,
        "board_age_min": board_age_min,
        "health_percent": health,
        "wake_services": [w["service"] for w in wake],
        "refire_lanes": [l["lane"] for l in over_lanes],
        "is_wake": bool(wake),
    }
    return payload, summary


def should_write(payload, summary, out_path):
    """Healthy steady-state throttle: skip the write unless something
    changed or the hourly heartbeat is due. Wake always writes."""
    if summary["is_wake"]:
        return True, "wake condition — writing"
    prev = _read_existing(out_path)
    if prev is None:
        return True, "healthy, no previous wake.json — writing"
    if prev.get("wake"):
        return True, "healthy, previous wake.json carried a wake (flip) — writing"
    prev_gen = _parse_iso(prev.get("generated_at_utc"))
    if prev_gen is None:
        return True, "healthy, previous wake.json timestamp unparseable — writing"
    age_min = (datetime.now(timezone.utc) - prev_gen).total_seconds() / 60.0
    if age_min >= HEARTBEAT_MIN:
        return True, ("healthy, heartbeat due (previous wake.json %.0f min "
                      "old) — writing" % age_min)
    return False, ("healthy, no change (previous wake.json %.0f min old, "
                   "heartbeat in %.0f min) — leaving file untouched"
                   % (age_min, HEARTBEAT_MIN - age_min))


def main(argv=None):
    ap = argparse.ArgumentParser(description="External wake-up decision")
    ap.add_argument("--out", required=True,
                    help="path to write wake.json to")
    ap.add_argument("--board-file",
                    help="read the board from a local JSON file "
                         "instead of fetching (dry-run / tests)")
    ap.add_argument("--board-url", action="append", default=[],
                    help="board URL to try (repeatable; default apex, "
                         "then Pages origin)")
    args = ap.parse_args(argv)

    now_utc = datetime.now(timezone.utc)
    if args.board_file:
        try:
            with open(args.board_file) as f:
                board = json.load(f)
            board_source, fetch_error = "file:%s" % args.board_file, None
        except Exception as e:  # noqa: BLE001
            board, board_source, fetch_error = None, None, str(e)
    else:
        urls = args.board_url or [APEX_URL, PAGES_URL]
        board, board_source, fetch_error = _fetch_board(urls)

    payload, summary = decide(board, board_source, fetch_error, now_utc)
    write, why = should_write(payload, summary, args.out)
    print("WAKE-DECISION board_source=%s board_age_min=%s health=%s "
          "wake=%s refire=%s -> %s"
          % (summary["board_source"], summary["board_age_min"],
             summary["health_percent"], summary["wake_services"],
             summary["refire_lanes"], why))
    if not write:
        return 0
    try:
        os.makedirs(os.path.dirname(os.path.abspath(args.out))
                    or ".", exist_ok=True)
        tmp = args.out + ".tmp"
        with open(tmp, "w") as f:
            json.dump(payload, f, indent=2)
            f.write("\n")
        os.replace(tmp, args.out)
    except OSError as e:
        print("WAKE-DECISION ERROR: cannot write %s: %s" % (args.out, e),
              file=sys.stderr)
        return 1
    print("WAKE-DECISION wrote %s" % args.out)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
