"""Read only private triad monitor. No publisher, deployment or scheduler mutation."""
import argparse
from datetime import datetime, timezone
import html
import json
import os
from pathlib import Path
import re
import tempfile
import time
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

REPOS = ("sicairos4/david-sicairos-site", "sicairos4/209-independent-publisher")
RANK = {"failed": 0, "pending": 1, "unknown": 2, "skipped_or_neutral": 3, "passed": 4}
FIELDS = "id,name,modifiedTime,lastModifyingUser(displayName)"

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

def get_json(url, token):
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc not in {"api.github.com", "www.googleapis.com"}:
        raise ValueError("Unapproved origin")
    headers = {"Accept": "application/json", "User-Agent": "209-private-triad-monitor"}
    if token:
        headers["Authorization"] = "Bearer " + token
    with build_opener(NoRedirect()).open(Request(url, headers=headers), timeout=20) as response:
        raw = response.read(1000001)
    if len(raw) > 1000000:
        raise ValueError("Response too large")
    return json.loads(raw)

def verdict(checks, statuses):
    conclusions = [c.get("conclusion") for c in checks]
    if any(c in {"failure", "cancelled", "timed_out", "action_required", "startup_failure", "stale"} for c in conclusions) or any(s.get("state") in {"failure", "error"} for s in statuses):
        return "failed"
    if any(c.get("status") != "completed" for c in checks) or any(s.get("state") == "pending" for s in statuses):
        return "pending"
    if not checks and not statuses:
        return "unknown"
    if any(c not in {"success", "skipped", "neutral"} for c in conclusions) or any(s.get("state") != "success" for s in statuses):
        return "unknown"
    return "skipped_or_neutral" if any(c in {"skipped", "neutral"} for c in conclusions) else "passed"

def collect(env, request=get_json):
    started = datetime.now(timezone.utc).isoformat()
    prs, files, errors, limits = [], {}, [], []
    def error(source, exc):
        code = getattr(exc, "code", None)
        errors.append({"source": source, "error_type": type(exc).__name__, "http_status": code if type(code) is int else None})
    for repo in REPOS:
        try:
            base = "https://api.github.com/repos/" + repo
            rows = request(base + "/pulls?state=open&per_page=20&sort=updated&direction=desc", env.get("GITHUB_TOKEN", ""))
            if not isinstance(rows, list):
                raise ValueError("Invalid pull request listing")
            if len(rows) >= 20:
                limits.append(repo + ": pull listing may be truncated")
            for index, row in enumerate(rows):
                item = {"repo": repo, "number": row["number"], "title": row["title"], "author": row.get("user", {}).get("login"), "updated_at": row["updated_at"], "head_sha": row["head"]["sha"], "check_outcome": "unknown", "checks_complete": False, "checks": [], "statuses": []}
                if index < 5:
                    try:
                        commit = base + "/commits/" + item["head_sha"]
                        checks = request(commit + "/check-runs?per_page=100", env.get("GITHUB_TOKEN", ""))
                        statuses = request(commit + "/status?per_page=100", env.get("GITHUB_TOKEN", ""))
                        item["checks"] = [{k: c.get(k) for k in ("name", "status", "conclusion")} for c in checks["check_runs"]]
                        item["statuses"] = [{k: s.get(k) for k in ("context", "state")} for s in statuses["statuses"]]
                        item["checks_complete"] = checks["total_count"] <= len(item["checks"]) and statuses["total_count"] <= len(item["statuses"])
                        result = verdict(item["checks"], item["statuses"])
                        item["check_outcome"] = result if item["checks_complete"] or result in {"failed", "pending"} else "unknown"
                    except Exception as exc:
                        error(repo + ":checks:" + str(item["number"]), exc)
                else:
                    limits.append(repo + ": checks not fetched for PR " + str(item["number"]))
                prs.append(item)
        except Exception as exc:
            error(repo, exc)
    try:
        token = env.get("GOOGLE_ACCESS_TOKEN", "")
        ids = [s.strip() for s in env.get("TRIAD_DRIVE_FILE_IDS", "").split(",") if s.strip()]
        folder = env.get("TRIAD_DRIVE_FOLDER_ID", "")
        if not token or not (ids or folder) or len(ids) > 20 or any(not re.fullmatch(r"[A-Za-z0-9_-]{10,200}", x) for x in ids + ([folder] if folder else [])):
            raise ValueError("Drive configuration missing or invalid")
        def add(row):
            files[row["id"]] = {"id": row["id"], "title": row["name"], "modified_at": row["modifiedTime"], "last_editor": row.get("lastModifyingUser", {}).get("displayName")}
        if folder:
            params = {"q": "'" + folder + "' in parents and trashed=false", "fields": "nextPageToken,files(" + FIELDS + ")", "pageSize": 100, "orderBy": "modifiedTime desc", "supportsAllDrives": "true", "includeItemsFromAllDrives": "true"}
            listing = request("https://www.googleapis.com/drive/v3/files?" + urlencode(params), token)
            for row in listing["files"]:
                add(row)
            if listing.get("nextPageToken"):
                limits.append("Drive folder listing truncated")
        for ident in ids:
            try:
                add(request("https://www.googleapis.com/drive/v3/files/" + ident + "?" + urlencode({"fields": FIELDS, "supportsAllDrives": "true"}), token))
            except Exception as exc:
                error("drive:" + ident, exc)
    except Exception as exc:
        error("drive", exc)
    prs.sort(key=lambda p: p["updated_at"], reverse=True)
    prs.sort(key=lambda p: (RANK[p["check_outcome"]], p["author"] or ""))
    return {"schema_version": 1, "collection_started_at": started, "collection_finished_at": datetime.now(timezone.utc).isoformat(), "state": "degraded" if errors else "snapshot_collected", "mode": "read_only", "automatic_actions": False, "pull_requests": prs, "drive_updates": sorted(files.values(), key=lambda f: f["modified_at"], reverse=True), "errors": errors, "limitations": limits, "attribution": "GitHub account and Drive last editor are not proof of Muse authorship. No checks is unknown, never passed. This is not a host heartbeat or required check evaluation."}

def render(report):
    return "<!doctype html><html lang='en'><meta charset='utf-8'><meta http-equiv='refresh' content='300'><title>Private triad monitor snapshot</title><h1>Private triad monitor snapshot</h1><p>Local report refresh only. Check collection timestamps. Do not publish this private metadata.</p><pre>" + html.escape(json.dumps(report, indent=2, ensure_ascii=False)) + "</pre></html>"

def write_private(path, text):
    path = Path(path)
    if path.is_symlink():
        raise ValueError("Symlink output refused")
    fd, temporary = tempfile.mkstemp(prefix=".triad-monitor-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="Private local JSON path, never commit or serve")
    parser.add_argument("--html", help="Optional private local HTML path, never deploy")
    parser.add_argument("--watch", action="store_true", help="Foreground loop only; no service installation")
    parser.add_argument("--interval", type=int, default=300)
    args = parser.parse_args()
    if args.interval < 300 or (args.html and Path(args.html).resolve() == Path(args.output).resolve()):
        parser.error("Minimum interval 300 seconds; output paths must differ")
    while True:
        report = collect(os.environ)
        report["foreground_watch_enabled"] = args.watch
        write_private(args.output, json.dumps(report, indent=2) + "\n")
        if args.html:
            write_private(args.html, render(report))
        print(json.dumps({"state": report["state"], "observed_at": report["collection_finished_at"]}))
        if not args.watch:
            break
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
