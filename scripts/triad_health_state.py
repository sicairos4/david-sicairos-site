"""Pure health projection and recovery intent. No network, queue writes or posting."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Timezone required")
    return parsed


def project_lane(lane, receipts, now):
    cadence = lane["cadence_seconds"]
    if type(cadence) is not int or cadence < 900:
        raise ValueError("Cadence must be at least 900 seconds for these default thresholds")
    if now.tzinfo is None:
        raise ValueError("Timezone required")
    base = {"lane_id": lane["lane_id"], "observation_time": now.isoformat(), "input_provenance": "Caller must authenticate source observations and receipts", "automatic_execution": False}
    age = (now - timestamp(lane["observed_at"])).total_seconds()
    if age < -30 or age > 600:
        return {**base, "state": "invalid_clock_skew" if age < -30 else "stale_source", "intent": "refresh_source", "dispatch_allowed": False}
    eligible, rejected = [], []
    for receipt in receipts:
        if receipt.get("lane_id") != lane["lane_id"]:
            continue
        try:
            published = timestamp(receipt["published_at"])
            gap = (now - published).total_seconds()
            if gap < -30:
                raise ValueError("future_publication")
            if receipt.get("action_type") != "root_publish" or receipt.get("visibility") != "public":
                raise ValueError("not_public_root_publish")
            if receipt.get("verification_state") != "verified_live":
                raise ValueError("not_verified_live")
            if not receipt.get("fired_by") or not receipt.get("verified_by") or receipt["fired_by"] == receipt["verified_by"]:
                raise ValueError("independent_verifier_required")
            if not receipt.get("platform_post_id") or not isinstance(receipt.get("public_url"), str) or not receipt["public_url"].startswith("https://"):
                raise ValueError("platform_identity_required")
            eligible.append((published, receipt))
        except (ValueError, TypeError, KeyError, AttributeError):
            rejected.append("receipt_rejected")
    if not eligible:
        return {**base, "state": "unknown", "intent": "reconcile_receipts", "rejected_receipts": len(rejected), "dispatch_allowed": False}
    published, latest = max(eligible, key=lambda row: row[0])
    raw_gap = (now - published).total_seconds()
    gap = max(0, raw_gap)
    thresholds = ((2 * cadence, "red"), (2 * cadence - 300, "diagnose_due"), (cadence + 600, "override_due"), (cadence, "yellow"), (cadence - 600, "prefire_due"))
    cadence_state = next((state for threshold, state in thresholds if gap >= threshold), "green")
    intent = "none" if cadence_state == "green" else "request_claimed_recovery"
    if lane.get("submission_state") in {"submitted", "submitted_uncertain", "uncertain"}:
        intent = "reconcile_uncertain_submission"
    elif lane.get("active_lease") is True:
        intent = "stand_down_existing_owner"
    if rejected:
        intent = "reconcile_receipts"
    key = hashlib.sha256(json.dumps([lane["lane_id"], latest["platform_post_id"], cadence_state], separators=(",", ":")).encode()).hexdigest()
    supply = lane.get("staged_count")
    supply_state = "unknown" if type(supply) is not int or supply < 0 else "refill_due" if supply < 25 else "sufficient"
    return {**base, "state": "degraded" if rejected else cadence_state, "cadence_state": cadence_state, "gap_seconds": gap, "clock_skew_tolerated": raw_gap < 0, "last_verified_publish_at": published.isoformat(), "rejected_receipts": len(rejected), "supply_state": supply_state, "intent": intent, "idempotency_key": key, "authoritative_claim_required": True, "monotonic_fencing_required": True, "dispatch_allowed": False, "note": "Intent only. Existing authorized executor must acquire the authoritative claim. No proof of three independent mechanisms or source authenticity is asserted."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Private JSON with lanes and receipts; no secrets")
    parser.add_argument("output", help="New private local report; never public hosting")
    args = parser.parse_args()
    with Path(args.input).open("rb") as stream:
        raw = stream.read(1000001)
    if len(raw) > 1000000:
        raise ValueError("Input too large")
    data = json.loads(raw)
    if not isinstance(data["lanes"], list) or not isinstance(data["receipts"], list) or len(data["lanes"]) > 100 or len(data["receipts"]) > 10000:
        raise ValueError("Invalid input bounds")
    now = datetime.now(timezone.utc)
    report = {"schema_version": 1, "clock_source": "local_host_clock_not_independently_verified", "mode": "projection_only", "lanes": [project_lane(lane, data["receipts"], now) for lane in data["lanes"]]}
    import os
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
