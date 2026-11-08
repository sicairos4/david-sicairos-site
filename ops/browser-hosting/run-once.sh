#!/usr/bin/env bash
set -euo pipefail
if [[ "${BROWSER_WORKER_ROLE:-standby}" != primary ]]; then exit 0; fi
if [[ -z "${BROWSER_DATABASE_URL:-}" ]]; then echo 'Runtime database credential is not configured.' >&2; exit 1; fi
exec /opt/209-browser/venv/bin/python /opt/209-browser/worker/browser_worker.py run-once
