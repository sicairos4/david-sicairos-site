import datetime as dt
import html
import json
import os
import re
import tempfile
from pathlib import Path
from urllib.parse import urlsplit


def merge_archive(root):
    root = Path(root)
    archive_path = root / "data/newsletters.json"
    catalog_path = root / "data/media-catalog.json"
    archive = json.loads(archive_path.read_text(encoding="utf-8"))
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    imported_at = archive.get("imported_at")
    if not imported_at:
        raise ValueError("archive_import_timestamp_missing")
    timestamp = dt.datetime.fromisoformat(imported_at.replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        raise ValueError("archive_import_timezone_missing")
    articles = archive.get("articles")
    if not isinstance(articles, list) or not articles:
        raise ValueError("public_archive_empty")
    items = {item["id"]: item for item in catalog.get("items", [])}
    additions = {}
    for article in articles:
        key = article.get("id")
        link = article.get("source_url", "")
        parsed = urlsplit(link)
        if not key or parsed.scheme != "https" or parsed.hostname != "209connect.beehiiv.com" or parsed.username or parsed.password:
            raise ValueError("invalid_archive_identity_or_url")
        date = dt.date.fromisoformat(article["date"])
        midnight = dt.datetime.combine(date, dt.time(), tzinfo=dt.timezone.utc)
        identity = "beehiiv:" + str(key)
        if identity in additions:
            raise ValueError("duplicate_archive_id")
        additions[identity] = {
            "id": identity, "platform": "beehiiv",
            "title": article.get("title", "Untitled"),
            "published_at": article["date"], "url": link,
            "description": html.unescape(re.sub(r"<[^>]+>", " ", article.get("subtitle", "")))[:5000],
            "observed_at": imported_at,
            "state": "public_archive_observed",
            "published_date": {"original": article["date"], "precision": "date", "utc_iso": midnight.isoformat(), "utc_epoch": int(midnight.timestamp()), "timezone_assumed_utc": True},
            "provenance": {"source": "existing_public_newsletter_importer", "archive_imported_at": imported_at},
        }
    by_url = {item["url"]: identity for identity, item in additions.items()}
    for identity, item in list(items.items()):
        if item.get("platform") == "beehiiv" and item.get("url") in by_url and identity != by_url[item["url"]]:
            del items[identity]
    items.update(additions)
    ordered = sorted(items.values(), key=lambda item: (item.get("published_date", {}).get("utc_epoch") is not None, item.get("published_date", {}).get("utc_epoch") or 0, item["id"]), reverse=True)
    catalog["items"] = ordered
    catalog.setdefault("sources", {})["beehiiv_archive"] = {"status": "available_cached_archive", "archive_imported_at": imported_at, "returned_count": len(additions), "coverage": "existing_public_archive_not_live_rss_verification"}
    catalog["archive_merged_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    briefs = {"generated_at": catalog["archive_merged_at"], "publishing_enabled": False, "briefs": [{"source_id": item["id"], "source_url": item["url"], "title": item["title"], "state": "draft_requires_review", "instruction": "Prepare platform-specific copy; review claims, freshness, rights and prior publication before approval."} for item in ordered[:40]]}
    for path, value in [(catalog_path, catalog), (root / "data/media-draft-briefs.json", briefs)]:
        with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            temporary = handle.name
        os.replace(temporary, path)
    return len(additions)


if __name__ == "__main__":
    merge_archive(Path(__file__).resolve().parents[1])
