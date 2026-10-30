#!/usr/bin/env bash
set -euo pipefail
umask 077
repo_root="$(git rev-parse --show-toplevel)"
private_root="${HOME:?HOME is required}/209-private"
: "${ARCHIVE_OWNER_UUID:?Configure the actual Supabase Auth owner UUID as a Codespaces secret}"
: "${ARCHIVE_DATASET_SHA256:?Configure the trusted archive dataset fingerprint as a Codespaces secret}"
mode="${1:-review}"
case "$mode" in
  review) extra=() ;;
  apply-plan) extra=(--commit) ;;
  *) printf '%s\n' 'Usage: bash scripts/prepare_archive_codespace.sh [review|apply-plan]' >&2; exit 2 ;;
esac
mkdir -p "$private_root/sql"
chmod 700 "$private_root/sql"
output="$private_root/sql/archive-import-$(date -u +%Y%m%dT%H%M%SZ)-$mode.sql"
python3 "$repo_root/scripts/prepare_archive_import.py" --dataset "$private_root/source/attachment-index-dataset-20261024.json" --owner "$ARCHIVE_OWNER_UUID" --output "$output" "${extra[@]}"
printf '%s\n' 'SQL prepared locally only. No database operation was executed. Approve the exact populated SQL before import.'
