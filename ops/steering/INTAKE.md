# Private snapshot intake

This adds the next local step between the agreed v1 export and the existing operator dashboard. It is not a provider collector, public upload endpoint, authenticated web service or publisher. Muse must still identify the actual runtime and produce an authorized sanitized export matching 209-steering-snapshot.schema.json. No source-format mapping, live metrics, credentials or runtime connection are invented.

## Usage

Run with Python 3.9+ and timezone data, from the website checkout:

```sh
python ops/steering/ingest_209_steering.py /private/runtime/export.json --render
```

The example path is a placeholder for an actual private file outside the checkout. Use --directory to choose a private operator-owned destination outside the website checkout and --max-rows (1–1000) for the dashboard display limit. Default: ~/.local/share/209-steering/inbox. Do not select another public checkout, shared/synced directory or web-served folder.

Each accepted payload gets a checksum-named directory containing snapshot.json, receipt.json and, with --render, dashboard.html. The command prints only the bundle ID and review-only status, not post contents. Output files are created owner-only; on POSIX, an existing intake directory must be owned by the operator and deny group/other access. The bundle is staged before rename so incomplete bundles are not intentionally exposed as accepted. This is not a power-loss recovery guarantee.

Identical canonical JSON payloads reuse a matching existing bundle without overwriting it. Changing measurements or generation time creates a different bundle. If the original bundle has no dashboard, use the standalone renderer to generate one outside the checkout. No latest/active pointer is changed and no publisher consumer is called. Existing bundles are not evidence that they remain fresh: validation runs again on every intake, and dashboard expiry labels still apply.

## Additional review gates

The existing validator remains unchanged. Intake also rejects duplicate JSON keys and non-finite numbers. Advisories must expire within the snapshot lifetime and reference available/ok sources with collection timestamps within that declared freshness interval and at least one reported metric. Stale observations may remain visible as history, but cannot drive an intake-accepted advisory. Collection freshness is distinct from the historical measurement window.

A passing receipt means declared structure and these consistency gates passed. It does not establish that provider evidence, sample counts, access authorization, redaction or analytics are genuine. A checksum detects payload differences; it does not authenticate the exporter or provide a digital signature. This remains advisory-only, with review required. Never put real private data into ops/steering or treat ignore rules as access control.

No cron/watch process, API call, database mutation, posting, website reordering or autonomous execution is enabled. Source authored only; no real export, tests, browser run or live runtime acceptance is claimed.
