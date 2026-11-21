#!/usr/bin/env python3
"""209 engine health check — read-only.

Fetches the public live-state.json (receipts-only health board) from
209connect.com and scores the lanes. No credentials, no writes to any
platform, no publishing. Exit 0 = healthy, exit 1 = RED (health < 80% or
any lane at >= 2x cadence) or the board itself is stale/unreachable.

Usage:
    python3 engine_health_check.py \
        --live-state-url "https://209connect.com/209-intelligence/live-state.json" \
        --report health-report.md

Board schema (verified live 2026-11-20, live-state.json v1):
    system_health.pct            overall health percent (receipts-only)
    summary.{total_lanes,on_cadence,due,missing}
    lanes[]: {key, platform, account, cadence_minutes, state, gap_minutes,
              last_verified_pt, last_url}
    generated_at_iso             when the board was generated

Rules (David's bars):
    - health < 80%  -> FAIL (failing)
    - any lane gap >= 2x its cadence_minutes -> RED lane -> FAIL
    - board older than 30 min (generated_at_iso) -> STALE -> FAIL
      (a stale board means the VM-side publisher of the board is down)
"""

import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone

HEALTH_FAIL_PCT = 80
STALE_BOARD_MINUTES = 30
USER_AGENT = "209-engine-health-check/1.0 (github-actions; read-only)"


def fetch_live_state(url, timeout=25):
    """Fetch with retries: the Pages host occasionally resets the
    connection mid-body (urllib raises IncompleteRead); curl retries
    past it, so we do the same and keep any partial bytes.
    Fallback: curl subprocess. (On this VM, Python's TLS handshake to
    the Cloudflare front door times out — curl goes through the egress
    proxy and works. On GitHub runners, direct urllib works; curl is
    the belt-and-braces fallback there too.)"""
    import http.client
    import subprocess
    last_err = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"live-state fetch HTTP {resp.status}")
                raw = resp.read()
            return json.loads(raw.decode("utf-8"))
        except http.client.IncompleteRead as e:
            last_err = e
            if e.partial:
                try:
                    return json.loads(e.partial.decode("utf-8"))
                except (ValueError, UnicodeDecodeError):
                    pass
        except Exception as e:  # noqa: BLE001 — retry, then curl fallback
            last_err = e
    try:
        out = subprocess.run(
            ["curl", "-fsSL", "--max-time", str(timeout), "-A", USER_AGENT, url],
            capture_output=True, timeout=timeout + 5, check=True,
        )
        return json.loads(out.stdout.decode("utf-8"))
    except Exception as e:  # noqa: BLE001 — report, don't crash silently
        raise RuntimeError(
            f"live-state fetch failed after 3 urllib attempts ({last_err}) "
            f"and curl fallback ({e})"
        )


def parse_iso(s):
    try:
        return datetime.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live-state-url", required=True)
    ap.add_argument("--report", default="health-report.md")
    args = ap.parse_args()

    problems = []
    try:
        data = fetch_live_state(args.live_state_url)
    except Exception as e:  # noqa: BLE001 — report, don't crash silently
        problems.append(f"FETCH FAILED: {e}")
        data = None

    lines = ["# 209 engine health check (GitHub Actions, read-only)",
             "",
             f"Checked: {datetime.now(timezone.utc).isoformat()}",
             f"Source: {args.live_state_url}",
             ""]

    health_pct = None
    lanes = []
    generated_at = None
    if data is not None:
        sh = data.get("system_health") or {}
        health_pct = sh.get("pct")
        summary = data.get("summary") or {}
        lanes = data.get("lanes") or []
        generated_at = parse_iso(data.get("generated_at_iso"))
        lines.append(f"Board generated: {data.get('generated_at_pt') or data.get('generated_at_iso')}")
        lines.append(f"Health: **{health_pct}%** (board method: {sh.get('method', 'receipts-only')})")
        lines.append(
            f"Lanes: {summary.get('total_lanes', len(lanes))} total, "
            f"{summary.get('on_cadence', '?')} on cadence, "
            f"{summary.get('due', '?')} due, {summary.get('missing', '?')} missing"
        )
        lines.append("")

        if health_pct is not None and health_pct < HEALTH_FAIL_PCT:
            problems.append(f"HEALTH {health_pct}% < {HEALTH_FAIL_PCT}% (failing bar)")

        if generated_at is not None:
            age_min = (datetime.now(timezone.utc) - generated_at).total_seconds() / 60
            lines.append(f"Board age: {age_min:.1f} min")
            if age_min > STALE_BOARD_MINUTES:
                problems.append(f"BOARD STALE: {age_min:.1f} min old (> {STALE_BOARD_MINUTES} min) — VM-side board publisher may be down")
        else:
            problems.append("BOARD HAS NO generated_at_iso — cannot prove freshness")

        red, due, green = [], [], []
        for lane in lanes:
            key = lane.get("key", "?")
            cad = lane.get("cadence_minutes") or 0
            gap = lane.get("gap_minutes")
            state = lane.get("state", "?")
            if gap is None or not cad:
                due.append((key, state, gap, cad, lane.get("last_verified_pt")))
                continue
            if gap >= 2 * cad:
                red.append((key, state, gap, cad, lane.get("last_verified_pt")))
                problems.append(f"RED lane {key}: gap {gap}m >= 2x cadence {cad}m (last verified {lane.get('last_verified_pt')})")
            elif gap >= cad:
                due.append((key, state, gap, cad, lane.get("last_verified_pt")))
            else:
                green.append((key, state, gap, cad, lane.get("last_verified_pt")))

        def table(title, rows):
            out = [f"## {title} ({len(rows)})", "",
                   "| lane | state | gap | cadence | last verified |",
                   "|---|---|---|---|---|"]
            for key, state, gap, cad, last in sorted(rows):
                gap_s = f"{gap}m" if gap is not None else "—"
                out.append(f"| {key} | {state} | {gap_s} | {cad}m | {last or '?'} |")
            out.append("")
            return out

        lines += table("RED lanes (>= 2x cadence)", red)
        lines += table("DUE lanes (>= 1x cadence)", due)
        lines += table("GREEN lanes", green)
    else:
        lines.append("No board data — fetch failed. The board URL or the VM publisher is down.")

    lines.append("## Verdict")
    lines.append("")
    if problems:
        lines.append("**FAIL** — problems:")
        lines += [f"- {p}" for p in problems]
    else:
        lines.append(f"**PASS** — health {health_pct}%, no RED lanes, board fresh.")
    lines.append("")

    with open(args.report, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    for p in problems:
        print(f"PROBLEM: {p}", file=sys.stderr)
    print(f"Health: {health_pct}% | lanes: {len(lanes)} | problems: {len(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
